#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
import datetime
import requests
import re
from bs4 import BeautifulSoup
import time
import random

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("aladin_scraper")

# 데이터 저장 디렉토리
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 헤더 설정 - 브라우저처럼 보이게 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://www.aladin.co.kr'
}

# 알라딘 주목할만한 새 책 URL
ALADIN_URL = "https://www.aladin.co.kr/shop/common/wnew.aspx?BranchType=1&NewType=SpecialNew"

def extract_book_info_from_text(text):
    """
    텍스트에서 저자, 출판사, 출판일, 가격 정보를 추출합니다.
    
    사용자 지정 규칙:
    - 저자: (지은이) 앞에 있는 이름
    - 출판사: (지은이) | 뒤에 있는 이름
    - 출판일: | 다음에 있는 년월 정보
    - 가격: → 다음에 있는 금액
    """
    author = "저자 정보 없음"
    publisher = "출판사 정보 없음"
    pub_date = "출판일 정보 없음"
    price = "가격 정보 없음"
    
    try:
        logger.debug(f"추출할 텍스트: {text}")
        
        # 저자 추출: (지은이) 앞에 있는 이름
        author_match = re.search(r'([^|]+?)\s*\(지은이\)', text)
        if author_match:
            author = author_match.group(1).strip()
            logger.debug(f"저자 추출 성공: {author}")
        
        # 출판사 추출: (지은이) | 뒤에 있는 이름
        publisher_match = re.search(r'\(지은이\)\s*\|\s*([^|]+?)(?=\||$)', text)
        if publisher_match:
            publisher = publisher_match.group(1).strip()
            logger.debug(f"출판사 추출 성공: {publisher}")
        
        # 출판일 추출: | 다음에 있는 년월 정보
        pub_date_match = re.search(r'\|\s*(20\d{2}년\s*\d{1,2}월)', text)
        if pub_date_match:
            pub_date = pub_date_match.group(1).strip()
            logger.debug(f"출판일 추출 성공: {pub_date}")
        
        # 가격 추출: → 다음에 있는 금액
        price_match = re.search(r'→\s*([\d,]+원)', text)
        if price_match:
            price = price_match.group(1).strip()
            logger.debug(f"가격 추출 성공: {price}")
        
        # 추가 패턴 시도 - 알라딘 웹페이지의 다양한 형식 대응
        if author == "저자 정보 없음":
            # 다른 형식의 저자 정보 시도
            alt_author_match = re.search(r'([^|]+?)\s*저자', text)
            if alt_author_match:
                author = alt_author_match.group(1).strip()
                logger.debug(f"대체 패턴으로 저자 추출 성공: {author}")
        
        if publisher == "출판사 정보 없음":
            # 다른 형식의 출판사 정보 시도
            alt_publisher_match = re.search(r'출판사\s*:\s*([^|]+?)(?=\||$)', text)
            if alt_publisher_match:
                publisher = alt_publisher_match.group(1).strip()
                logger.debug(f"대체 패턴으로 출판사 추출 성공: {publisher}")
        
        if pub_date == "출판일 정보 없음":
            # 다른 형식의 출판일 정보 시도
            alt_pub_date_match = re.search(r'출간일\s*:\s*(20\d{2}-\d{2}-\d{2}|20\d{2}년\s*\d{1,2}월)', text)
            if alt_pub_date_match:
                pub_date = alt_pub_date_match.group(1).strip()
                logger.debug(f"대체 패턴으로 출판일 추출 성공: {pub_date}")
        
        if price == "가격 정보 없음":
            # 다른 형식의 가격 정보 시도
            alt_price_match = re.search(r'정가\s*:\s*([\d,]+원)', text)
            if alt_price_match:
                price = alt_price_match.group(1).strip()
                logger.debug(f"대체 패턴으로 가격 추출 성공: {price}")
    except Exception as e:
        logger.error(f"텍스트에서 책 정보 추출 실패: {e}")
    
    return {
        "author": author,
        "publisher": publisher,
        "pub_date": pub_date,
        "price": price
    }

def get_book_details(book_url):
    """
    책 상세 페이지에서 추가 정보를 가져옵니다.
    가능한 모든 정보를 수집하여 빈 값을 최소화합니다.
    """
    try:
        response = requests.get(book_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 책 소개 추출 - 여러 선택자 시도
        description = ""
        description_selectors = ['#div_book_content', '.Ere_prod_mconts_box', '.book_info_area']
        for selector in description_selectors:
            description_div = soup.select_one(selector)
            if description_div and description_div.get_text(strip=True):
                description = description_div.get_text(strip=True)
                break
        
        # 책 정보 텍스트 추출 - 사용자 지정 규칙에 따라 정보 추출
        book_info_text = ""
        book_info_selectors = ['.Ere_book_info', '.book_info_area', '.info_list']
        for selector in book_info_selectors:
            book_info_div = soup.select_one(selector)
            if book_info_div:
                book_info_text = book_info_div.get_text(strip=True)
                break
        
        # 텍스트에서 저자, 출판사, 출판일, 가격 정보 추출
        extracted_info = extract_book_info_from_text(book_info_text)
        
        # 카테고리 정보 추출
        category = ""
        category_selectors = [
            '.location', 
            '.catetab_cont li:contains("분야")',
            '.book_info_area li:contains("분야")'
        ]
        for selector in category_selectors:
            category_info = soup.select_one(selector)
            if category_info:
                category = category_info.get_text(strip=True)
                category = category.replace('분야 :', '').replace('분야:', '').strip()
                break
        
        # ISBN 추출
        isbn = ""
        isbn_info_selectors = [
            '.info_list li:contains("ISBN")', 
            '.book_info_area li:contains("ISBN")',
            '.Ere_sub2_title:contains("ISBN")'
        ]
        for selector in isbn_info_selectors:
            isbn_info = soup.select_one(selector)
            if isbn_info:
                isbn = isbn_info.get_text(strip=True)
                isbn = isbn.replace('ISBN :', '').replace('ISBN:', '').strip()
                break
        
        # 페이지 수 추출
        pages = ""
        page_info_selectors = [
            '.info_list li:contains("페이지")', 
            '.book_info_area li:contains("페이지")',
            '.Ere_sub2_title:contains("페이지")'
        ]
        for selector in page_info_selectors:
            page_info = soup.select_one(selector)
            if page_info:
                pages = page_info.get_text(strip=True)
                pages = pages.replace('페이지 :', '').replace('쪽수 :', '').replace('쪽수:', '').strip()
                break
        
        return {
            "description": description[:500] + "..." if len(description) > 500 else description,
            "pub_date": extracted_info["pub_date"],
            "pages": pages if pages else "페이지 정보 없음",
            "isbn": isbn if isbn else "ISBN 정보 없음",
            "detailed_price": extracted_info["price"],
            "detailed_author": extracted_info["author"],
            "detailed_publisher": extracted_info["publisher"],
            "category": category if category else "분류 정보 없음"
        }
    except Exception as e:
        logger.error(f"책 상세 정보 가져오기 실패: {e}")
        return {
            "description": "책 소개 정보를 가져오지 못했습니다.",
            "pub_date": "출판일 정보 없음",
            "pages": "페이지 정보 없음",
            "isbn": "ISBN 정보 없음",
            "detailed_price": "가격 정보 없음",
            "detailed_author": "저자 정보 없음",
            "detailed_publisher": "출판사 정보 없음",
            "category": "분류 정보 없음"
        }

def scrape_aladin_new_books():
    """
    알라딘 주목할만한 새 책 페이지에서 책 정보를 스크래핑합니다.
    """
    logger.info("알라딘 주목할만한 새 책 스크래핑 시작")
    
    try:
        # 페이지 요청
        response = requests.get(ALADIN_URL, headers=HEADERS)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 책 목록 컨테이너 찾기
        book_items = soup.select('.ss_book_box')
        
        books = []
        
        for item in book_items:
            try:
                # 책 제목
                title_elem = item.select_one('.bo3')
                title = title_elem.get_text(strip=True) if title_elem else "제목 없음"
                
                # 책 URL
                book_url = title_elem['href'] if title_elem and title_elem.has_attr('href') else ""
                
                # 이미지 URL
                img_elem = item.select_one('.front_cover img')
                img_url = img_elem['src'] if img_elem and img_elem.has_attr('src') else ""
                
                # 책 정보 텍스트 (저자, 출판사, 출판일, 가격 정보 추출용)
                book_info_text = ""
                info_elem = item.select_one('.ss_book_list')
                if info_elem:
                    book_info_text = info_elem.get_text(strip=True)
                
                # 텍스트에서 저자, 출판사, 출판일, 가격 정보 추출
                extracted_info = extract_book_info_from_text(book_info_text)
                
                # 간단한 설명
                short_description_elem = item.select_one('.ss_book_list:nth-of-type(3)')
                short_description = short_description_elem.get_text(strip=True) if short_description_elem else ""
                
                # 책 상세 페이지에서 추가 정보 가져오기
                details = {}
                if book_url:
                    # 너무 많은 요청을 방지하기 위해 잠시 대기
                    time.sleep(random.uniform(1, 3))
                    details = get_book_details(book_url)
                
                book_info = {
                    "title": title,
                    "author": details.get("detailed_author", extracted_info["author"]),
                    "publisher": details.get("detailed_publisher", extracted_info["publisher"]),
                    "price": details.get("detailed_price", extracted_info["price"]),
                    "img_url": img_url,
                    "book_url": book_url,
                    "short_description": short_description,
                    "description": details.get("description", ""),
                    "pub_date": details.get("pub_date", extracted_info["pub_date"]),
                    "pages": details.get("pages", ""),
                    "isbn": details.get("isbn", ""),
                    "category_info": details.get("category", ""),
                    "scrape_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                books.append(book_info)
                logger.info(f"책 정보 추출 성공: {title}")
                
            except Exception as e:
                logger.error(f"책 정보 추출 실패: {e}")
                continue
        
        logger.info(f"총 {len(books)}권의 책 정보 추출 완료")
        
        # 결과 저장
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(DATA_DIR, f"aladin_new_books_{today}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        
        logger.info(f"책 정보 저장 완료: {filename}")
        
        # 가장 흥미로운 책 30권 선정 (여기서는 간단히 처리)
        # 실제로는 더 복잡한 알고리즘을 적용할 수 있음
        interesting_books = select_interesting_books(books, 30)
        
        interesting_filename = os.path.join(DATA_DIR, f"interesting_books_{today}.json")
        with open(interesting_filename, 'w', encoding='utf-8') as f:
            json.dump(interesting_books, f, ensure_ascii=False, indent=2)
        
        logger.info(f"주목할만한 책 30권 저장 완료: {interesting_filename}")
        
        return books, interesting_books
        
    except Exception as e:
        logger.error(f"스크래핑 중 오류 발생: {e}")
        return [], []

def select_interesting_books(books, count=30):
    """
    경제, 정치, 인문, 사회, 자기계발, 과학 분야의 책 중에서
    가장 흥미로운 책 30권을 선정합니다.
    """
    # 관심 카테고리 정의
    target_categories = [
        "경제", "정치", "인문", "사회", "자기계발", "과학",
        "경영", "비즈니스", "심리", "철학", "역사", "사회과학"
    ]
    
    # 카테고리에 해당하는 책만 필터링
    filtered_books = []
    for book in books:
        title = book.get("title", "").lower()
        description = book.get("description", "").lower() + book.get("short_description", "").lower()
        publisher = book.get("publisher", "").lower()
        
        # 카테고리 관련 키워드가 제목, 설명, 출판사에 포함되어 있는지 확인
        for category in target_categories:
            if (category.lower() in title or 
                category.lower() in description or 
                category.lower() in publisher):
                filtered_books.append(book)
                break
    
    # 필터링된 책이 count보다 적으면 원래 목록에서 추가
    if len(filtered_books) < count:
        remaining_count = count - len(filtered_books)
        # 이미 선택된 책은 제외
        remaining_books = [b for b in books if b not in filtered_books]
        # 설명 길이를 기준으로 정렬
        sorted_remaining = sorted(remaining_books, key=lambda x: len(x.get("description", "")), reverse=True)
        filtered_books.extend(sorted_remaining[:remaining_count])
    
    # 설명 길이를 기준으로 정렬
    sorted_books = sorted(filtered_books, key=lambda x: len(x.get("description", "")), reverse=True)
    
    # 상위 count개 선택
    selected_books = sorted_books[:count]
    
    # 선택된 책에 카테고리 정보 추가
    for book in selected_books:
        book_categories = []
        title = book.get("title", "").lower()
        description = book.get("description", "").lower() + book.get("short_description", "").lower()
        
        for category in target_categories:
            if (category.lower() in title or 
                category.lower() in description):
                book_categories.append(category)
        
        book["categories"] = book_categories if book_categories else ["기타"]
    
    return selected_books

def get_latest_books():
    """
    가장 최근에 스크래핑한 책 정보를 가져옵니다.
    """
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.startswith("aladin_new_books_")]
        if not files:
            return []
        
        # 가장 최근 파일 찾기
        latest_file = max(files)
        file_path = os.path.join(DATA_DIR, latest_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            books = json.load(f)
        
        return books
    except Exception as e:
        logger.error(f"최근 책 정보 가져오기 실패: {e}")
        return []

def get_latest_interesting_books():
    """
    가장 최근에 선정된 흥미로운 책 30권을 가져옵니다.
    """
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.startswith("interesting_books_")]
        if not files:
            return []
        
        # 가장 최근 파일 찾기
        latest_file = max(files)
        file_path = os.path.join(DATA_DIR, latest_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            books = json.load(f)
        
        return books
    except Exception as e:
        logger.error(f"최근 흥미로운 책 정보 가져오기 실패: {e}")
        return []

if __name__ == "__main__":
    # 테스트 실행
    books, interesting_books = scrape_aladin_new_books()
    print(f"총 {len(books)}권의 책 정보 추출 완료")
    print(f"주목할만한 책 {len(interesting_books)}권 선정 완료")
