document.addEventListener('DOMContentLoaded', () => {
    const newsListContainer = document.getElementById('news-list');

    /**
     * 특정 종목에 대한 뉴스 기사를 API에서 가져와 화면에 표시합니다.
     * 이 함수는 search.html의 스크립트 블록이나 다른 JS 파일에서 호출될 수 있습니다.
     * @param {string} companyName - 검색할 종목명
     */
    window.fetchNewsForStock = async function(companyName) {
        newsListContainer.innerHTML = '<p>뉴스 기사를 불러오는 중...</p>'; // 로딩 메시지

        if (!companyName) {
            newsListContainer.innerHTML = '<p>종목명을 입력해주세요.</p>';
            return;
        }

        try {
            // Flask API 호출: /api/news 엔드포인트 사용
            const response = await fetch(`/api/news?company_name=${encodeURIComponent(companyName)}`);
            const data = await response.json();

            if (!response.ok) { // HTTP 응답 코드가 200번대가 아닐 경우
                newsListContainer.innerHTML = `<p class="error-message">뉴스 데이터를 불러오는 데 실패했습니다: ${data.error || '알 수 없는 오류'}</p>`;
                return;
            }

            displayNewsArticles(data.news_articles);

        } catch (error) {
            console.error('Fetch news error:', error);
            newsListContainer.innerHTML = '<p class="error-message">서버 통신 중 뉴스 데이터를 불러오는 데 오류가 발생했습니다.</p>';
        }
    };

    /**
     * 뉴스 기사 목록을 HTML에 표시합니다.
     * @param {Array<Object>} newsArticles - [{date: 'YYYY-MM-DD', title: '...', link: '...'}, ...] 형태의 뉴스 기사 데이터
     */
    function displayNewsArticles(newsArticles) {
        newsListContainer.innerHTML = ''; // 기존 목록 초기화

        if (!newsArticles || newsArticles.length === 0) {
            newsListContainer.innerHTML = '<p>해당 종목에 대한 뉴스 기사를 찾을 수 없습니다.</p>';
            return;
        }

        const ul = document.createElement('ul');
        newsArticles.forEach(article => {
            const li = document.createElement('li');
            li.classList.add('news-article');
            li.innerHTML = `
                <p><strong>날짜:</strong> ${article.date}</p>
                <p><strong>제목:</strong> <a href="${article.link}" target="_blank">${article.title}</a></p>
            `;
            ul.appendChild(li);
        });
        newsListContainer.appendChild(ul);
    }
});