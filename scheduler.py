#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import logging
import schedule
from datetime import datetime
from scraper import scrape_aladin_new_books

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("aladin_scheduler")

def job():
    """
    스케줄링된 작업: 알라딘 신간 도서 스크래핑
    """
    logger.info("스케줄된 작업 시작: 알라딘 신간 도서 스크래핑")
    current_day = datetime.now().strftime("%A")
    logger.info(f"현재 요일: {current_day}")
    
    try:
        books, interesting_books = scrape_aladin_new_books()
        logger.info(f"작업 완료: 총 {len(books)}권의 책 정보 추출, 주목할만한 책 {len(interesting_books)}권 선정")
    except Exception as e:
        logger.error(f"스케줄된 작업 실행 중 오류 발생: {e}")

def run_scheduler():
    """
    매주 월요일과 목요일에 실행되는 스케줄러를 설정합니다.
    """
    logger.info("알라딘 신간 도서 스케줄러 시작")
    
    # 매주 월요일 오전 9시에 실행
    schedule.every().monday.at("09:00").do(job)
    logger.info("스케줄 등록: 매주 월요일 오전 9시")
    
    # 매주 목요일 오전 9시에 실행
    schedule.every().thursday.at("09:00").do(job)
    logger.info("스케줄 등록: 매주 목요일 오전 9시")
    
    # 서버 시작 시 즉시 한 번 실행
    logger.info("초기 데이터 수집을 위해 즉시 실행")
    job()
    
    # 스케줄러 무한 루프
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 스케줄 확인

if __name__ == "__main__":
    run_scheduler()
