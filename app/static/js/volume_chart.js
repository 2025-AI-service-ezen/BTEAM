document.addEventListener("DOMContentLoaded", () => {
    const chartDataElement = document.getElementById("priceChartData");
    if (!chartDataElement) return;

    const chartData = JSON.parse(chartDataElement.textContent);
    if (chartData.length === 0) return;

    const ctx = document.getElementById("priceChart").getContext("2d");
    const labels = chartData.map(item => item.date);
    const volumes = chartData.map(item => item['거래량']);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '거래량',
                data: volumes,
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: { display: true, text: '최근 10일 거래량' }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});
