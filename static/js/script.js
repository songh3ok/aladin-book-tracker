// 검색 및 정렬 기능을 위한 JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    const dateSelect = document.getElementById('date-select');
    const booksTable = document.querySelector('.books-table');
    const noResults = document.querySelector('.no-results');
    const bookItems = Array.from(document.querySelectorAll('.book-item'));
    
    // 원본 도서 데이터 저장
    const originalBooks = bookItems.map(item => {
        return {
            element: item,
            title: item.querySelector('.book-title').textContent.toLowerCase(),
            author: item.querySelector('.book-author').textContent.toLowerCase(),
            publisher: item.querySelector('.book-publisher').textContent.toLowerCase(),
            category: item.querySelector('.book-categories').textContent.toLowerCase()
        };
    });
    
    // 검색 기능
    if (searchInput) {
        searchInput.addEventListener('input', filterBooks);
    }
    
    // 정렬 기능
    if (sortSelect) {
        sortSelect.addEventListener('change', sortBooks);
    }
    
    // 날짜 선택 기능
    if (dateSelect) {
        dateSelect.addEventListener('change', function() {
            const selectedDate = this.value;
            changeDate(selectedDate);
        });
    }
    
    // 도서 필터링 함수
    function filterBooks() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        
        let visibleCount = 0;
        
        originalBooks.forEach(book => {
            const isVisible = 
                book.title.includes(searchTerm) || 
                book.author.includes(searchTerm) || 
                book.publisher.includes(searchTerm) ||
                book.category.includes(searchTerm);
            
            book.element.style.display = isVisible ? '' : 'none';
            
            if (isVisible) {
                visibleCount++;
            }
        });
        
        // 검색 결과가 없을 때 메시지 표시
        if (noResults) {
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }
    
    // 도서 정렬 함수
    function sortBooks() {
        const sortBy = sortSelect.value;
        const tbody = booksTable.querySelector('tbody');
        
        const sortedBooks = [...originalBooks].sort((a, b) => {
            switch(sortBy) {
                case 'title':
                    return a.title.localeCompare(b.title, 'ko');
                case 'author':
                    return a.author.localeCompare(b.author, 'ko');
                case 'publisher':
                    return a.publisher.localeCompare(b.publisher, 'ko');
                case 'pub_date':
                    // 출간일 정보가 있다면 이를 기준으로 정렬
                    const dateA = a.element.querySelector('.book-pub-date').textContent || '';
                    const dateB = b.element.querySelector('.book-pub-date').textContent || '';
                    return dateB.localeCompare(dateA); // 최신순
                default:
                    return 0;
            }
        });
        
        // DOM 재정렬
        sortedBooks.forEach(book => {
            tbody.appendChild(book.element);
        });
    }
});

// 날짜 선택 시 페이지 이동 또는 데이터 로드 함수
function changeDate(date) {
    if (!date) return;
    
    // 정적 HTML 버전에서는 날짜 선택 시 알림 표시
    if (window.location.protocol === 'file:' || !window.location.search) {
        // 정적 HTML 파일에서 실행 중인 경우
        alert(`선택하신 날짜(${date})의 추천 도서를 표시합니다.\n\n참고: 정적 HTML 버전에서는 실제 데이터가 변경되지 않습니다. 전체 기능을 사용하려면 Flask 애플리케이션을 실행해주세요.`);
        document.querySelector('.last-update').textContent = `마지막 업데이트: ${date}`;
        return;
    }
    
    // Flask 애플리케이션에서는 실제 데이터 로드
    window.location.href = `/?date=${date}`;
}

// 페이지 로드 시 애니메이션 효과
window.addEventListener('load', function() {
    const bookItems = document.querySelectorAll('.book-item');
    
    // 모든 책 애니메이션
    bookItems.forEach((book, index) => {
        setTimeout(() => {
            book.style.opacity = '1';
            book.style.transform = 'translateY(0)';
        }, 30 * index);
    });
});

// 스크롤 시 헤더 스타일 변경
window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});
