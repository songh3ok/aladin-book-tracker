# 알라딘 신간 도서 트래커 (Aladin New Book Tracker)

이 프로젝트는 알라딘 온라인 서점에서 신간 도서 정보를 자동으로 수집하고, 주목할만한 책을 선정하여 보여주는 웹 애플리케이션입니다.

## 주요 기능

1. **자동 데이터 수집**: 매주 월요일과 목요일에 알라딘 온라인 서점에서 신간 도서 정보를 자동으로 수집합니다.
2. **주차별 관리**: 연도와 주차 기반으로 데이터를 관리하여 체계적으로 도서 정보를 확인할 수 있습니다.
3. **주목할만한 책 선정**: 경제, 정치, 인문, 사회, 자기계발, 과학 분야에서 30권의 주목할만한 책을 선정합니다.
4. **리스트 형식 표시**: 선정된 책을 리스트 형식으로 표시하여 제목, 저자, 출판사, 가격, 출판일, 분야 정보를 한눈에 볼 수 있습니다.
5. **과거 추천 도서 아카이브**: 연도와 주차를 선택하여 이전 추천 도서 목록을 확인할 수 있습니다.
   - 2025년 1월부터 데이터 수집 시작
   - 아직 지나지 않은 주차는 선택 불가

## 프로젝트 구조

```
aladin_book_tracker/
├── app.py                 # Flask 애플리케이션 (웹 서버)
├── scraper.py             # 웹 스크래핑 스크립트
├── scheduler.py           # 스케줄러 (월요일, 목요일 자동 실행)
├── index.html             # 정적 웹페이지
├── data/                  # 수집된 데이터 저장 디렉토리
├── static/                # 정적 파일 (CSS, JS)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── templates/             # Flask 템플릿
    ├── index.html
    └── error.html
```

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/yourusername/aladin-book-tracker.git
cd aladin-book-tracker
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. 애플리케이션 실행
```bash
python app.py
```

## 스크래퍼 실행

```bash
python scraper.py
```

## 스케줄러 실행

```bash
python scheduler.py
```

## 기술 스택

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Web Scraping**: BeautifulSoup4, Requests
- **Scheduling**: Schedule

## 책 정보 추출 로직

사용자 지정 규칙에 따라 책 정보를 정확하게 추출합니다:

- **저자**: (지은이) 앞에 있는 이름 (예: "전영수")
- **출판사**: (지은이) | 뒤에 있는 이름 (예: "라의눈")
- **출판일**: | 다음에 있는 년월 정보 (예: "2025년 4월")
- **가격**: → 다음에 있는 금액 (예: "22,500원")

## 라이센스

MIT

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새 기능 브랜치를 만듭니다 (`git checkout -b feature/amazing-feature`).
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.
