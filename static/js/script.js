// 검색 및 정렬 기능을 위한 JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    const booksGrid = document.querySelector('.books-grid');
    const noResults = document.querySelector('.no-results');
    const bookCards = Array.from(document.querySelectorAll('.book-card'));
    
    // 원본 도서 데이터 저장
    const originalBooks = bookCards.map(card => {
        return {
            element: card,
            title: card.querySelector('.book-title').textContent.toLowerCase(),
            author: card.querySelector('.book-author').textContent.toLowerCase(),
            publisher: card.querySelector('.book-publisher').textContent.toLowerCase()
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
    
    // 도서 필터링 함수
    function filterBooks() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        
        let visibleCount = 0;
        
        originalBooks.forEach(book => {
            const isVisible = 
                book.title.includes(searchTerm) || 
                book.author.includes(searchTerm) || 
                book.publisher.includes(searchTerm);
            
            book.element.style.display = isVisible ? 'flex' : 'none';
            
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
                    const dateA = a.element.dataset.pubDate || '';
                    const dateB = b.element.dataset.pubDate || '';
                    return dateB.localeCompare(dateA); // 최신순
                default:
                    return 0;
            }
        });
        
        // DOM 재정렬
        sortedBooks.forEach(book => {
            booksGrid.appendChild(book.element);
        });
    }
});

// 날짜 선택 시 페이지 이동 함수
function changeDate(date) {
    if (date) {
        window.location.href = `/?date=${date}`;
    }
}

// 페이지 로드 시 애니메이션 효과
window.addEventListener('load', function() {
    const featuredBooks = document.querySelectorAll('.featured-book-card');
    const bookCards = document.querySelectorAll('.book-card');
    
    // 주목할만한 책 애니메이션
    featuredBooks.forEach((book, index) => {
        setTimeout(() => {
            book.style.opacity = '1';
            book.style.transform = 'translateY(0)';
        }, 100 * index);
    });
    
    // 모든 책 애니메이션
    bookCards.forEach((book, index) => {
        setTimeout(() => {
            book.style.opacity = '1';
            book.style.transform = 'translateY(0)';
        }, 50 * index);
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
