// Setting universal chart styling
Chart.defaults.color = "#8b949e";
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.borderColor = "rgba(255, 255, 255, 0.05)";

// Function to generate distinct colors for datasets
const colors = [
    'rgb(88, 166, 255)',  // accent
    'rgb(163, 113, 247)', // purple
    'rgb(46, 160, 67)',   // green
    'rgb(248, 81, 73)',   // red
    'rgb(210, 153, 34)',  // orange
    'rgb(64, 196, 255)'   // light blue
];

function loadDashboardData() {
    fetch('/api/dashboard_data')
        .then(response => response.json())
        .then(data => {
            renderPriceTrendChart(data.price_trend);
            renderRiskChart(data.risk_data);
            renderReturnsChart(data.avg_returns);
            renderPriceVolumeChart(data.price_vol);
        })
        .catch(err => console.error("Error loading dashboard data:", err));
}

function renderPriceTrendChart(priceTrend) {
    const ctx = document.getElementById('priceTrendChart').getContext('2d');
    
    // We assume dates are same across currencies for simplicity
    const labels = priceTrend[Object.keys(priceTrend)[0]].dates;
    
    const datasets = Object.keys(priceTrend).map((name, index) => {
        return {
            label: name,
            data: priceTrend[name].prices,
            borderColor: colors[index % colors.length],
            backgroundColor: 'transparent',
            tension: 0.3, // smooth curves
            borderWidth: 2
        };
    });

    new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: { title: { display: true, text: 'Price (USD)' } },
                x: { title: { display: true, text: 'Date' } }
            }
        }
    });
}

function renderRiskChart(riskData) {
    const ctx = document.getElementById('riskChart').getContext('2d');
    
    const labels = Object.keys(riskData);
    
    // For Boxplot simulation we just use bar charts for average volatility since Chart.js by default doesn't have boxplot without plugin
    // Let's compute min, max, avg to draw a simple custom representation, or just average volatility.
    // Given the Python script plotted BoxPlot (distribution of Volatility), let's plot average volatility as a Bar chart for simplicity.
    const avgVolatility = labels.map(name => {
        const arr = riskData[name];
        return arr.reduce((a, b) => a + b, 0) / arr.length;
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Volatility (High - Low)',
                data: avgVolatility,
                backgroundColor: colors.slice(0, labels.length).map(c => c.replace('rgb', 'rgba').replace(')', ', 0.6)')),
                borderColor: colors.slice(0, labels.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { title: { display: true, text: 'Volatility' } }
            }
        }
    });
}

function renderReturnsChart(avgReturns) {
    const ctx = document.getElementById('returnsChart').getContext('2d');
    const labels = Object.keys(avgReturns);
    const data = Object.values(avgReturns);
    
    const bgColors = data.map(val => val >= 0 ? 'rgba(46, 160, 67, 0.7)' : 'rgba(248, 81, 73, 0.7)');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Avg Daily Return (%)',
                data: data,
                backgroundColor: bgColors,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
}

function renderPriceVolumeChart(priceVol) {
    const ctx = document.getElementById('priceVolumeChart').getContext('2d');
    
    const datasets = Object.keys(priceVol).map((name, index) => {
        // Map data arrays into scatter points {x, y}
        const dataArr = priceVol[name].volumes.map((vol, i) => ({
            x: vol,
            y: priceVol[name].prices[i]
        }));
        
        return {
            label: name,
            data: dataArr,
            backgroundColor: colors[index % colors.length].replace('rgb', 'rgba').replace(')', ', 0.7)'),
            pointRadius: 6,
            pointHoverRadius: 8
        };
    });

    new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { 
                    title: { display: true, text: 'Trading Volume' },
                    type: 'linear',
                    position: 'bottom'
                },
                y: { title: { display: true, text: 'Price (USD)' } }
            }
        }
    });
}
