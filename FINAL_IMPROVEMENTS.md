# 알라딘 신간 도서 트래커 - 최종 업데이트 내용

## 최종 개선사항 요약
1. **책 정보 추출 로직 개선**: 사용자 지정 규칙에 따라 저자, 출판사, 출판일, 가격 정보를 정확하게 추출하도록 개선했습니다.
2. **리스트 형식 표시**: 갤러리 형식에서 테이블 기반 리스트 형식으로 변경하여 더 많은 책 정보를 한눈에 볼 수 있도록 했습니다.
3. **추천 책 수 증가**: 추천 책 수를 5권에서 30권으로 증가시켜 더 다양한 신간 도서를 확인할 수 있습니다.
4. **분야 정보 표시**: 각 책의 분야 정보를 명확하게 표시하여 관심 분야의 책을 쉽게 식별할 수 있습니다.

## 책 정보 추출 로직 개선
사용자 지정 규칙에 따라 책 정보를 정확하게 추출하도록 로직을 개선했습니다:

- **저자**: (지은이) 앞에 있는 이름 (예: "전영수")
- **출판사**: (지은이) | 뒤에 있는 이름 (예: "라의눈")
- **출판일**: | 다음에 있는 년월 정보 (예: "2025년 4월")
- **가격**: → 다음에 있는 금액 (예: "22,500원")

이를 위해 정규 표현식을 사용한 `extract_book_info_from_text()` 함수를 구현했습니다:

```python
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
        # 저자 추출: (지은이) 앞에 있는 이름
        author_match = re.search(r'([^|]+?)\s*\(지은이\)', text)
        if author_match:
            author = author_match.group(1).strip()
        
        # 출판사 추출: (지은이) | 뒤에 있는 이름
        publisher_match = re.search(r'\(지은이\)\s*\|\s*([^|]+?)(?=\||$)', text)
        if publisher_match:
            publisher = publisher_match.group(1).strip()
        
        # 출판일 추출: | 다음에 있는 년월 정보
        pub_date_match = re.search(r'\|\s*(20\d{2}년\s*\d{1,2}월)', text)
        if pub_date_match:
            pub_date = pub_date_match.group(1).strip()
        
        # 가격 추출: → 다음에 있는 금액
        price_match = re.search(r'→\s*([\d,]+원)', text)
        if price_match:
            price = price_match.group(1).strip()
    except Exception as e:
        logger.error(f"텍스트에서 책 정보 추출 실패: {e}")
    
    return {
        "author": author,
        "publisher": publisher,
        "pub_date": pub_date,
        "price": price
    }
```

또한 알라딘 웹페이지의 다양한 형식에 대응하기 위해 추가 패턴도 구현했습니다:

```python
# 추가 패턴 시도 - 알라딘 웹페이지의 다양한 형식 대응
if author == "저자 정보 없음":
    # 다른 형식의 저자 정보 시도
    alt_author_match = re.search(r'([^|]+?)\s*저자', text)
    if alt_author_match:
        author = alt_author_match.group(1).strip()

if publisher == "출판사 정보 없음":
    # 다른 형식의 출판사 정보 시도
    alt_publisher_match = re.search(r'출판사\s*:\s*([^|]+?)(?=\||$)', text)
    if alt_publisher_match:
        publisher = alt_publisher_match.group(1).strip()

if pub_date == "출판일 정보 없음":
    # 다른 형식의 출판일 정보 시도
    alt_pub_date_match = re.search(r'출간일\s*:\s*(20\d{2}-\d{2}-\d{2}|20\d{2}년\s*\d{1,2}월)', text)
    if alt_pub_date_match:
        pub_date = alt_pub_date_match.group(1).strip()

if price == "가격 정보 없음":
    # 다른 형식의 가격 정보 시도
    alt_price_match = re.search(r'정가\s*:\s*([\d,]+원)', text)
    if alt_price_match:
        price = alt_price_match.group(1).strip()
```

## 리스트 형식 표시
갤러리 형식에서 테이블 기반 리스트 형식으로 변경하여 다음 정보를 한눈에 볼 수 있도록 했습니다:

- 번호 (순서)
- 제목
- 저자
- 출판사
- 가격
- 출판일
- 분야
- 상세정보 링크

```html
<table class="books-table">
    <thead>
        <tr>
            <th>No.</th>
            <th>제목</th>
            <th>저자</th>
            <th>출판사</th>
            <th>가격</th>
            <th>출판일</th>
            <th>분야</th>
            <th>상세정보</th>
        </tr>
    </thead>
    <tbody>
        <tr class="book-item">
            <td>1</td>
            <td class="book-title">요즘어른의 부머 경제학</td>
            <td class="book-author">전영수</td>
            <td class="book-publisher">라의눈</td>
            <td class="book-price">22,500원</td>
            <td class="book-pub-date">2025년 4월</td>
            <td class="book-categories">경제</td>
            <td><a href="https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=361349536" class="book-link" target="_blank">자세히 보기</a></td>
        </tr>
        <!-- 추가 책 정보 -->
    </tbody>
</table>
```

## 추천 책 수 증가
추천 책 수를 5권에서 30권으로 증가시켜 더 다양한 신간 도서를 확인할 수 있도록 했습니다:

```python
# 가장 흥미로운 책 30권 선정
interesting_books = select_interesting_books(books, 30)
```

## 분야 정보 표시
각 책의 분야 정보를 명확하게 표시하여 관심 분야의 책을 쉽게 식별할 수 있도록 했습니다:

```python
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
```

## 사용 방법

### 웹사이트 접속
최신 버전의 웹사이트는 다음 URL에서 접근할 수 있습니다:
[https://rhczpint.manus.space](https://rhczpint.manus.space)

### 과거 추천 도서 확인하기
1. 웹사이트 상단의 "과거 추천 도서 보기" 드롭다운 메뉴를 클릭합니다.
2. 원하는 날짜를 선택합니다.
3. 해당 날짜에 추천된 도서 목록이 표시됩니다.

### 전체 기능 사용하기
정적 웹사이트는 최신 수집 데이터의 스냅샷만 제공합니다. 실시간 업데이트와 모든 기능을 사용하려면 Flask 애플리케이션을 실행해야 합니다:

```bash
cd /home/ubuntu/aladin_book_tracker
python3 app.py
```

스케줄러를 실행하여 매주 월요일과 목요일에 자동으로 데이터를 수집하도록 설정할 수 있습니다:

```bash
cd /home/ubuntu/aladin_book_tracker
python3 scheduler.py
```

## 향후 개선 계획
- 정렬 및 필터링 기능 강화
- 책 상세 정보 페이지 추가
- 사용자 리뷰 및 평점 시스템 추가
- 모바일 앱 개발
