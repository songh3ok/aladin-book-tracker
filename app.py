#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
import glob
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from scraper import scrape_aladin_new_books, get_latest_books, get_latest_interesting_books

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("aladin_app")

# 데이터 디렉토리
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Flask 앱 초기화
app = Flask(__name__)

def get_available_weeks():
    """
    사용 가능한 모든 주차 데이터를 가져옵니다.
    Returns: {year: [weeks]} 형식의 딕셔너리
    """
    try:
        # 모든 interesting_week 파일 찾기
        files = glob.glob(os.path.join(DATA_DIR, "interesting_week_*.json"))

        # 파일명에서 연도와 주차 추출 (interesting_week_2025_W01.json)
        weeks_by_year = {}
        for file in files:
            filename = os.path.basename(file)
            # interesting_week_2025_W01.json → 2025, 01
            parts = filename.replace("interesting_week_", "").replace(".json", "").split("_")
            if len(parts) == 2:
                year = int(parts[0])
                week = int(parts[1].replace("W", ""))

                if year not in weeks_by_year:
                    weeks_by_year[year] = []
                weeks_by_year[year].append(week)

        # 각 연도별로 주차 정렬
        for year in weeks_by_year:
            weeks_by_year[year].sort(reverse=True)  # 최신 주차가 먼저

        return weeks_by_year
    except Exception as e:
        logger.error(f"주차 목록 가져오기 실패: {e}")
        return {}

def get_books_by_week(year, week):
    """
    특정 연도/주차의 책 데이터를 가져옵니다.
    """
    try:
        all_books_file = os.path.join(DATA_DIR, f"week_{year}_W{week:02d}.json")
        featured_books_file = os.path.join(DATA_DIR, f"interesting_week_{year}_W{week:02d}.json")

        all_books = []
        featured_books = []

        if os.path.exists(all_books_file):
            with open(all_books_file, 'r', encoding='utf-8') as f:
                all_books = json.load(f)

        if os.path.exists(featured_books_file):
            with open(featured_books_file, 'r', encoding='utf-8') as f:
                featured_books = json.load(f)

        return all_books, featured_books
    except Exception as e:
        logger.error(f"{year}년 {week}주차의 책 데이터 가져오기 실패: {e}")
        return [], []

@app.route('/')
def index():
    """
    메인 페이지 렌더링
    """
    try:
        # 연도와 주차 파라미터 확인
        year_param = request.args.get('year', None)
        week_param = request.args.get('week', None)

        # 사용 가능한 모든 주차 가져오기
        available_weeks = get_available_weeks()

        # 현재 연도와 주차
        now = datetime.now()
        current_year, current_week, _ = now.isocalendar()

        # 파라미터가 없으면 최신 데이터 사용
        if not year_param or not week_param:
            # 최신 도서 데이터 가져오기
            all_books = get_latest_books()
            featured_books = get_latest_interesting_books()

            # 데이터가 없으면 스크래핑 실행
            if not all_books or not featured_books:
                logger.info("데이터가 없어 스크래핑을 실행합니다.")
                all_books, featured_books = scrape_aladin_new_books()

            # 마지막 업데이트 시간 계산
            last_update = "데이터 없음"
            if all_books and len(all_books) > 0:
                if 'scrape_date' in all_books[0]:
                    last_update = all_books[0]['scrape_date']
                else:
                    # 파일 수정 시간으로 대체
                    files = [f for f in os.listdir(DATA_DIR) if f.startswith("week_")]
                    if files:
                        latest_file = max(files)
                        file_path = os.path.join(DATA_DIR, latest_file)
                        last_update = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

            # 사용할 연도와 주차 결정
            selected_year = current_year
            selected_week = current_week
            if available_weeks:
                # 가장 최근 연도
                latest_year = max(available_weeks.keys())
                selected_year = latest_year
                # 해당 연도의 가장 최근 주차
                if available_weeks[latest_year]:
                    selected_week = max(available_weeks[latest_year])
        else:
            # 지정된 연도/주차의 데이터 가져오기
            selected_year = int(year_param)
            selected_week = int(week_param)
            all_books, featured_books = get_books_by_week(selected_year, selected_week)

            # 마지막 업데이트 시간
            if all_books and len(all_books) > 0 and 'scrape_date' in all_books[0]:
                last_update = all_books[0]['scrape_date']
            else:
                last_update = f"{selected_year}년 {selected_week}주차 데이터"

        return render_template('index.html',
                              all_books=all_books,
                              featured_books=featured_books,
                              last_update=last_update,
                              selected_year=selected_year,
                              selected_week=selected_week,
                              current_year=current_year,
                              current_week=current_week,
                              available_weeks=available_weeks)

    except Exception as e:
        logger.error(f"메인 페이지 렌더링 중 오류 발생: {e}")
        return render_template('error.html', error=str(e))

@app.route('/refresh')
def refresh_data():
    """
    데이터 수동 새로고침 API
    """
    try:
        all_books, featured_books = scrape_aladin_new_books()
        return jsonify({
            "success": True,
            "message": f"데이터 새로고침 완료. {len(all_books)}권의 책 정보를 가져왔습니다.",
            "count": len(all_books)
        })
    except Exception as e:
        logger.error(f"데이터 새로고침 중 오류 발생: {e}")
        return jsonify({
            "success": False,
            "message": f"오류 발생: {str(e)}"
        }), 500

@app.route('/api/books')
def api_books():
    """
    모든 책 정보를 JSON으로 제공하는 API
    """
    try:
        books = get_latest_books()
        return jsonify(books)
    except Exception as e:
        logger.error(f"API 호출 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/featured')
def api_featured():
    """
    주목할만한 책 5권 정보를 JSON으로 제공하는 API
    """
    try:
        books = get_latest_interesting_books()
        return jsonify(books)
    except Exception as e:
        logger.error(f"API 호출 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 초기 데이터가 없으면 스크래핑 실행
    try:
        all_books = get_latest_books()
        featured_books = get_latest_interesting_books()
        
        if not all_books or not featured_books:
            logger.info("초기 데이터가 없어 스크래핑을 실행합니다.")
            scrape_aladin_new_books()
    except Exception as e:
        logger.error(f"초기 데이터 확인 중 오류 발생: {e}")
    
    # 앱 실행
    app.run(host='0.0.0.0', port=5000, debug=True)
