document.addEventListener('DOMContentLoaded', function() {
    const priceChartDataContainer = document.getElementById('priceChartDataContainer');
    if (!priceChartDataContainer) {
        console.warn("priceChartDataContainer div를 찾을 수 없습니다. 차트 데이터를 로드할 수 없습니다.");
        return;
    }

    const priceChartDataJson = priceChartDataContainer.dataset.chartData;
    const stockNameForChart = priceChartDataContainer.dataset.stockName;
    
    // 데이터가 없거나 비어있는 JSON 배열인 경우
    if (!priceChartDataJson || priceChartDataJson.length <= 2) { 
        console.log("No price chart data available. Chart will not be rendered.");
        const chartContainer = document.getElementById('chart-container');
        if (chartContainer) {
            chartContainer.innerHTML = '<p>해당 종목의 유효한 주가 데이터를 찾을 수 없습니다.</p>';
        }
        return;
    }

    // JSON 문자열을 JavaScript 객체로 파싱
    const data = JSON.parse(priceChartDataJson);
    const labels = data.map(item => item.date);
    const prices = data.map(item => item.close);

    const ctx = document.getElementById('stockChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${stockNameForChart} 주가`,
                data: prices,
                borderColor: 'rgb(75, 192, 192)',
                fill: false,
                tension: 0.1 // 부드러운 곡선 효과
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, // 캔버스 크기 조절 허용
            scales: {
                x: { 
                    type: 'time', // Chart.js 날짜/시간 축 사용을 명시
                    time: {
                        unit: 'month', // 월 단위로 표시
                        tooltipFormat: 'yyyy-MM-dd', // 툴팁에 표시될 날짜 형식
                        displayFormats: { // 축 라벨에 표시될 날짜 형식
                            month: 'yyyy년 MM월'
                        }
                    },
                    title: { display: true, text: '날짜' } // x축 제목
                },
                y: { 
                    title: { display: true, text: '종가 (원)' }, // y축 제목
                    ticks: {
                        callback: function(value, index, values) {
                            return value.toLocaleString(); // 숫자를 콤마 형식으로 표시 (예: 12,345)
                        }
                    }
                }
            },
            plugins: {
                tooltip: { // 툴팁 설정
                    callbacks: {
                        title: function(context) {
                            return context[0].label; // 툴팁 제목: 날짜
                        },
                        label: function(context) {
                            return `종가: ${context.raw.toLocaleString()}원`; // 툴팁 내용: 종가
                        }
                    }
                }
            }
        }
    });
});