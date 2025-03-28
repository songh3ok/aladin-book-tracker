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

def get_available_dates():
    """
    사용 가능한 모든 데이터 날짜를 가져옵니다.
    """
    try:
        # 모든 interesting_books 파일 찾기
        files = glob.glob(os.path.join(DATA_DIR, "interesting_books_*.json"))
        
        # 파일명에서 날짜 추출 (interesting_books_YYYY-MM-DD.json)
        dates = []
        for file in files:
            filename = os.path.basename(file)
            date_str = filename.replace("interesting_books_", "").replace(".json", "")
            dates.append(date_str)
        
        # 날짜 내림차순 정렬 (최신순)
        dates.sort(reverse=True)
        return dates
    except Exception as e:
        logger.error(f"날짜 목록 가져오기 실패: {e}")
        return []

def get_books_by_date(date_str):
    """
    특정 날짜의 책 데이터를 가져옵니다.
    """
    try:
        all_books_file = os.path.join(DATA_DIR, f"aladin_new_books_{date_str}.json")
        featured_books_file = os.path.join(DATA_DIR, f"interesting_books_{date_str}.json")
        
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
        logger.error(f"{date_str} 날짜의 책 데이터 가져오기 실패: {e}")
        return [], []

@app.route('/')
def index():
    """
    메인 페이지 렌더링
    """
    try:
        # 날짜 파라미터 확인
        date_str = request.args.get('date', None)
        
        # 사용 가능한 모든 날짜 가져오기
        available_dates = get_available_dates()
        
        # 데이터가 없거나 날짜가 지정되지 않은 경우 최신 데이터 사용
        if not available_dates or not date_str:
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
                    files = [f for f in os.listdir(DATA_DIR) if f.startswith("aladin_new_books_")]
                    if files:
                        latest_file = max(files)
                        file_path = os.path.join(DATA_DIR, latest_file)
                        last_update = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            
            # 날짜가 지정되지 않았으면 최신 날짜 사용
            if available_dates:
                current_date = available_dates[0]
            else:
                current_date = datetime.now().strftime("%Y-%m-%d")
        else:
            # 지정된 날짜의 데이터 가져오기
            all_books, featured_books = get_books_by_date(date_str)
            current_date = date_str
            
            # 마지막 업데이트 시간
            if all_books and len(all_books) > 0 and 'scrape_date' in all_books[0]:
                last_update = all_books[0]['scrape_date']
            else:
                last_update = f"{date_str} 데이터"
        
        return render_template('index.html', 
                              all_books=all_books, 
                              featured_books=featured_books, 
                              last_update=last_update,
                              current_date=current_date,
                              available_dates=available_dates)
    
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
