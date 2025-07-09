function setupAutocomplete(inputId, listId, apiUrl) {
    const searchInput = document.getElementById(inputId);
    const list = document.getElementById(listId);

    if (!searchInput || !list) return;

    let selectedIndex = -1;  // 현재 선택된 추천 항목 인덱스
    let suggestions = [];

    searchInput.addEventListener("input", async () => {
        const query = searchInput.value.trim();
        list.innerHTML = "";
        selectedIndex = -1;
        
        if (!query) return;

        try {
            const res = await fetch(`${apiUrl}?query=${encodeURIComponent(query)}`);
            suggestions = await res.json();

            suggestions.forEach((item, index) => {
                const div = document.createElement("div");
                div.className = "autocomplete-item";
                div.textContent = item;
                div.addEventListener("click", () => {
                    searchInput.value = item;
                    list.innerHTML = "";
                });
                list.appendChild(div);
            });
        } catch (err) {
            console.error("자동완성 오류:", err);
        }
    });

    // 키보드 ↑↓ 선택 및 Enter 처리
    searchInput.addEventListener("keydown", (e) => {
        const items = list.querySelectorAll(".autocomplete-item");
        if (items.length === 0) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            selectedIndex = (selectedIndex + 1) % items.length;
            updateSelection(items);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            selectedIndex = (selectedIndex - 1 + items.length) % items.length;
            updateSelection(items);
        } else if (e.key === "Enter") {
            if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
                e.preventDefault();
                searchInput.value = suggestions[selectedIndex];
                list.innerHTML = "";
            }
        }
    });

    // focus 벗어나면 추천 닫기
    document.addEventListener("click", (e) => {
        if (!searchInput.contains(e.target) && !list.contains(e.target)) {
            list.innerHTML = "";
            selectedIndex = -1;
        }
    });

    function updateSelection(items) {
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.style.backgroundColor = "#eee";
            } else {
                item.style.backgroundColor = "";
            }
        });
    }
}
