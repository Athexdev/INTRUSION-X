document.addEventListener('DOMContentLoaded', () => {
    // Initialize Charts
    const lineCtx = document.getElementById('lineChart')?.getContext('2d');
    const donutCtx = document.getElementById('donutChart')?.getContext('2d');
    
    let lineChart, donutChart;

    if (lineCtx) {
        lineChart = new Chart(lineCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Normal Traffic',
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        data: [],
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Anomalous Traffic',
                        borderColor: '#ff3e3e',
                        backgroundColor: 'rgba(255, 62, 62, 0.1)',
                        data: [],
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false } // Disable default legend
                },
                scales: {
                    y: { grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: '#94a3b8' } },
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                }
            }
        });

        // Toggle Legend Logic
        const toggleChart = (elementId, datasetIndex) => {
            const el = document.getElementById(elementId);
            if (!el || !lineChart) return;

            el.addEventListener('click', () => {
                const isVisible = lineChart.isDatasetVisible(datasetIndex);
                lineChart.setDatasetVisibility(datasetIndex, !isVisible);
                lineChart.update();

                el.classList.toggle('enabled', !isVisible);
                el.classList.toggle('disabled', isVisible);
            });
        };

        toggleChart('toggle-normal', 0);
        toggleChart('toggle-anomaly', 1);
    }

    if (donutCtx) {
        donutChart = new Chart(donutCtx, {
            type: 'doughnut',
            data: {
                labels: ['Safe', 'Warning', 'Critical'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#00ff88', '#ffcc00', '#ff3e3e'],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } }
            }
        });
    }

    // Auto-refresh Functionality
    function updateStats() {
        fetch('/api/stats/')
            .then(res => res.json())
            .then(data => {
                if (document.getElementById('stat-packets')) document.getElementById('stat-packets').innerText = data.packets;
                if (document.getElementById('stat-active')) document.getElementById('stat-active').innerText = data.active;
                if (document.getElementById('stat-anomalies')) document.getElementById('stat-anomalies').innerText = data.anomalies;
                
                const threatBadge = document.getElementById('threat-level-badge');
                if (threatBadge) {
                    threatBadge.innerText = data.threat_level;
                    threatBadge.className = 'threat-badge threat-' + data.threat_level.toLowerCase();
                }
            });
    }

    function updateChartData() {
        fetch('/api/chart-data/')
            .then(res => res.json())
            .then(data => {
                if (lineChart) {
                    lineChart.data.labels = data.labels;
                    lineChart.data.datasets[0].data = data.normal_data;
                    lineChart.data.datasets[1].data = data.anomaly_data;
                    lineChart.update();
                }
            }).catch(e => console.error("Chart Error:", e));
    }

    function updateClassificationData() {
        fetch('/api/classification-data/')
            .then(res => res.json())
            .then(data => {
                if (donutChart) {
                    donutChart.data.datasets[0].data = [data.safe, data.warning, data.critical];
                    donutChart.update();
                }
            });
    }

    function updateDashboardEvents() {
        const alertsContainer = document.getElementById('alerts-container');
        const logsBody = document.getElementById('recent-logs-body');

        if (alertsContainer) {
            fetch('/api/alerts/')
                .then(r => r.json())
                .then(data => {
                    alertsContainer.innerHTML = data.alerts.map(a => `
                        <div class="alert-item alert-${a.severity.toLowerCase()}">
                            <div class="alert-title">${a.type}</div>
                            <div class="alert-msg">${a.message}</div>
                            <div class="alert-time">${a.timestamp}</div>
                        </div>
                    `).join('');
                });
        }

        if (logsBody) {
            fetch('/api/recent-logs/')
                .then(r => r.json())
                .then(data => {
                    logsBody.innerHTML = data.logs.map(l => `
                        <tr>
                            <td class="ip-address ip-src">${l.src_ip}</td>
                            <td class="ip-address ip-dst">${l.dst_ip}</td>
                            <td>${l.protocol}</td>
                            <td>${l.packet_size}</td>
                            <td><code class="score-${l.status === 'Critical' ? 'anomaly' : 'normal'}">${l.anomaly_score}</code></td>
                            <td><span class="status-pill status-${l.status.toLowerCase()}">${l.status === 'Critical' ? '<i class="fa-solid fa-triangle-exclamation"></i> ' : ''}${l.status}</span></td>
                        </tr>
                    `).join('');
                });
        }
    }

    // Interval to refresh everything
    setInterval(() => {
        updateStats();
        updateChartData();
        updateClassificationData();
        updateDashboardEvents();
    }, 10000);

    // Initial load
    updateStats();
    updateChartData();
    updateClassificationData();
    updateDashboardEvents();
});
