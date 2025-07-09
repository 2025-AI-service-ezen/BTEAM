document.addEventListener("DOMContentLoaded", () => {
    const chartDataElement = document.getElementById("priceChartData");
    if (!chartDataElement) return;

    const chartData = JSON.parse(chartDataElement.textContent);
    if (chartData.length === 0) return;

    const ctx = document.getElementById("priceChart").getContext("2d");
    const labels = chartData.map(item => item.date);  // 날짜 라벨
    const volumes = chartData.map(item => item['거래량']);  // 거래량 값

    const volumeChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
        label: '최대 거래량',
        data: volumes,
        backgroundColor: 'skyblue',
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        onClick: (e, activeElements) => {
        if (!isLogin) {
            alert('로그인이 필요합니다.');
            return;
        }
        if (activeElements.length > 0) {
            const index = activeElements[0].index;
            const selectedStock = labels[index];
            window.location.href = `/search?search=${encodeURIComponent(selectedStock)}`;
        } else {
            openTop20Popup();
        }
        },
        scales: {
        y: { beginAtZero: true }
        }
    }
});
