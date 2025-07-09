document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("stock_input");
    const suggestionsDiv = document.getElementById("suggestions");

    input.addEventListener("input", () => {
        const query = input.value.trim();
        suggestionsDiv.innerHTML = '';

        if (!query) {
            suggestionsDiv.style.display = 'none';
            return;
        }

        const filtered = stockList.filter(s => s.stock_name.includes(query));

        if (filtered.length === 0) {
            suggestionsDiv.style.display = 'none';
            return;
        }

        filtered.forEach(s => {
            const div = document.createElement('div');
            div.textContent = s.stock_name;
            div.classList.add('autocomplete-item');
            div.style.cursor = "pointer";
            div.addEventListener('click', () => {
                input.value = s.stock_name;
                suggestionsDiv.style.display = 'none';
            });
            suggestionsDiv.appendChild(div);
        });

        suggestionsDiv.style.display = 'block';
    });

    document.addEventListener("click", (e) => {
        if (e.target !== input && e.target.parentNode !== suggestionsDiv) {
            suggestionsDiv.style.display = 'none';
        }
    });
});
