# 알라딘 신간 도서 트래커 - 최종 업데이트 내용

## 최신 변경사항 요약
1. **리스트 형식으로 변경**: 갤러리 형식에서 테이블 기반 리스트 형식으로 변경하여 더 많은 책 정보를 한눈에 볼 수 있도록 개선했습니다.
2. **추천 책 수 증가**: 추천 책 수를 5권에서 30권으로 증가시켜 더 다양한 신간 도서를 확인할 수 있습니다.
3. **책 정보 수집 개선**: 책 정보 수집 알고리즘을 강화하여 가능한 모든 정보를 수집하고 빈 값을 최소화했습니다.
4. **분야 정보 명확화**: 각 책의 분야 정보를 명확하게 표시하여 사용자가 관심 분야의 책을 쉽게 식별할 수 있습니다.

## 리스트 형식 변경
기존의 갤러리 형식에서 테이블 기반 리스트 형식으로 변경했습니다. 이제 다음 정보가 테이블 형식으로 표시됩니다:
- 번호 (순서)
- 제목
- 저자
- 출판사
- 가격
- 출판일
- 분야
- 상세정보 링크

이 형식은 더 많은 책을 효율적으로 표시하고, 사용자가 원하는 정보를 빠르게 찾을 수 있도록 합니다.

## 추천 책 수 증가
추천 책 수를 5권에서 30권으로 증가시켰습니다. 이를 통해:
- 더 다양한 신간 도서를 확인할 수 있습니다.
- 여러 분야의 책을 더 많이 포함할 수 있습니다.
- 사용자가 더 많은 선택지를 가질 수 있습니다.

## 책 정보 수집 개선
책 정보 수집 알고리즘을 다음과 같이 개선했습니다:
- 여러 CSS 선택자를 시도하여 정보 추출 성공률 향상
- 빈 값이 발생할 경우 기본값 제공 ("출판일 정보 없음" 등)
- 상세 페이지에서 더 정확한 정보 추출 (가격, 저자, 출판사 등)
- 카테고리 정보 추가 추출

이를 통해 사용자에게 더 완전하고 정확한 정보를 제공합니다.

## 분야 정보 명확화
각 책의 분야 정보를 명확하게 표시하여 사용자가 관심 분야의 책을 쉽게 식별할 수 있도록 했습니다:
- 경제, 정치, 인문, 사회, 자기계발, 과학 등의 분야 정보 표시
- 테이블의 별도 열에 분야 정보 표시
- 분야 정보가 없는 경우 "기타"로 표시

## 사용 방법

### 웹사이트 접속
최신 버전의 웹사이트는 다음 URL에서 접근할 수 있습니다:
[https://vmwoumwo.manus.space](https://vmwoumwo.manus.space)

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

## 기술적 구현 세부사항

### 리스트 형식 구현
HTML 템플릿에서 기존의 카드 기반 갤러리 형식을 테이블 기반 리스트 형식으로 변경했습니다:
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
        {% for book in featured_books %}
        <tr class="book-item">
            <td>{{ loop.index }}</td>
            <td class="book-title">{{ book.title }}</td>
            <td class="book-author">{{ book.author }}</td>
            <td class="book-publisher">{{ book.publisher }}</td>
            <td class="book-price">{{ book.price }}</td>
            <td class="book-pub-date">{{ book.pub_date }}</td>
            <td class="book-categories">{{ book.categories|join(', ') }}</td>
            <td><a href="{{ book.book_url }}" class="book-link" target="_blank">자세히 보기</a></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### 책 정보 수집 개선
`get_book_details` 함수를 개선하여 여러 CSS 선택자를 시도하고 빈 값을 최소화했습니다:
```python
def get_book_details(book_url):
    """
    책 상세 페이지에서 추가 정보를 가져옵니다.
    가능한 모든 정보를 수집하여 빈 값을 최소화합니다.
    """
    try:
        # 여러 선택자 시도하여 정보 추출
        description_selectors = ['#div_book_content', '.Ere_prod_mconts_box', '.book_info_area']
        for selector in description_selectors:
            description_div = soup.select_one(selector)
            if description_div and description_div.get_text(strip=True):
                description = description_div.get_text(strip=True)
                break
        
        # 빈 값 처리
        return {
            "description": description[:500] + "..." if len(description) > 500 else description,
            "pub_date": pub_date if pub_date else "출판일 정보 없음",
            "pages": pages if pages else "페이지 정보 없음",
            "isbn": isbn if isbn else "ISBN 정보 없음",
            # 추가 정보
        }
    except Exception as e:
        # 오류 처리
        return {
            "description": "책 소개 정보를 가져오지 못했습니다.",
            "pub_date": "출판일 정보 없음",
            # 기본값 제공
        }
```

## 향후 개선 계획
- 정렬 및 필터링 기능 강화
- 책 상세 정보 페이지 추가
- 사용자 리뷰 및 평점 시스템 추가
- 모바일 앱 개발
