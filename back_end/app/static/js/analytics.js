class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.currentPeriod = 7;
        this.dashboardData = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        document.getElementById('refresh-data').addEventListener('click', () => {
            this.loadDashboardData();
        });

        document.querySelectorAll('[data-period]').forEach(button => {
            button.addEventListener('click', (e) => {
                this.changePeriod(parseInt(e.target.dataset.period));
            });
        });
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/v1/analytics/dashboard');
            if (!response.ok) throw new Error('Failed to load dashboard data');
            
            const data = await response.json();
            this.dashboardData = data;
            this.updateOverviewCards(data.overview);
            this.createCharts(data);
            this.updateLiveUpdates(data);

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    updateOverviewCards(overview) {
        document.getElementById('total-patents').textContent = overview.total_patents.toLocaleString();
        document.getElementById('patents-30-days').textContent = overview.patents_last_30_days;
        document.getElementById('total-reports').textContent = overview.total_reports.toLocaleString();
        document.getElementById('reports-30-days').textContent = '+' + overview.reports_last_30_days;
        
        const growthPercent = overview.patents_last_year > 0 
            ? Math.round((overview.patents_last_30_days / overview.patents_last_year) * 100) 
            : 0;
        document.getElementById('patents-growth').textContent = '+' + growthPercent + '%';
        
        document.getElementById('active-companies').textContent = 
            this.dashboardData.top_assignees?.top_assignees?.length || 0;
    }

    createCharts(data) {
        this.createTimelineChart(data.timeline);
        this.createMonthlyTrendsChart(data.timeline);
        this.createStatusChart(data.status_distribution);
        this.createTopAssigneesChart(data.top_assignees);
        this.createFilingTrendsChart(data.filing_trends);
        this.createReportTypesChart(data.reports);
    }

    createTimelineChart(timelineData) {
        const ctx = document.getElementById('timeline-chart').getContext('2d');
        
        if (this.charts.timeline) {
            this.charts.timeline.destroy();
        }

        const dates = timelineData.timeline.map(item => new Date(item.date).toLocaleDateString());
        const counts = timelineData.timeline.map(item => item.count);

        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Patents Added',
                    data: counts,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    createMonthlyTrendsChart(data) {
        const ctx = document.getElementById('monthly-trends-chart').getContext('2d');
        
        if (this.charts.monthlyTrends) {
            this.charts.monthlyTrends.destroy();
        }

        const monthlyData = data.monthly || [];
        const months = monthlyData.map(item => item.month_name.slice(0, 3));
        const counts = monthlyData.map(item => item.count);

        this.charts.monthlyTrends = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [{
                    label: 'Patents per Month',
                    data: counts,
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    createStatusChart(statusData) {
        const ctx = document.getElementById('status-chart').getContext('2d');
        
        if (this.charts.status) {
            this.charts.status.destroy();
        }

        const colors = {
            pending: '#ffc107',
            granted: '#198754',
            expired: '#6c757d',
            abandoned: '#dc3545'
        };

        const distribution = statusData.status_distribution || [];
        
        this.charts.status = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: distribution.map(item => item.status.charAt(0).toUpperCase() + item.status.slice(1)),
                datasets: [{
                    data: distribution.map(item => item.count),
                    backgroundColor: distribution.map(item => colors[item.status] || '#6c757d'),
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const item = context.raw;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((item / total) * 100).toFixed(1);
                                return `${context.label}: ${item} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    createTopAssigneesChart(assigneeData) {
        const ctx = document.getElementById('top-assignees-chart').getContext('2d');
        
        if (this.charts.topAssignees) {
            this.charts.topAssignees.destroy();
        }

        const topAssignees = assigneeData.top_assignees || [];
        const labels = topAssignees.map(item => 
            item.assignee.length > 15 ? item.assignee.slice(0, 12) + '...' : item.assignee
        );
        const counts = topAssignees.map(item => item.patent_count);

        this.charts.topAssignees = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Patent Count',
                    data: counts,
                    backgroundColor: 'rgba(255, 99, 132, 0.8)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    createFilingTrendsChart(filingData) {
        const ctx = document.getElementById('filing-trends-chart').getContext('2d');
        
        if (this.charts.filingTrends) {
            this.charts.filingTrends.destroy();
        }

        const trends = filingData.filing_trends || [];
        const years = trends.map(item => item.year);
        const counts = trends.map(item => item.patent_count);

        this.charts.filingTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: years,
                datasets: [{
                    label: 'Patents Filed',
                    data: counts,
                    borderColor: 'rgb(153, 102, 255)',
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    createReportTypesChart(reportsData) {
        const ctx = document.getElementById('report-types-chart').getContext('2d');
        
        if (this.charts.reportTypes) {
            this.charts.reportTypes.destroy();
        }

        const reportTypes = reportsData.report_types || [];
        const labels = reportTypes.map(item => item.type);
        const counts = reportTypes.map(item => item.count);

        this.charts.reportTypes = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    updateLiveUpdates(data) {
        this.updateRecentActivity();
        this.updateSystemHealth();
        this.updateQuickStats(data);
    }

    updateRecentActivity() {
        const activities = [
            { time: '2 hours ago', action: 'New patent added: US20240012345' },
            { time: '4 hours ago', action: 'Report generated: AI in Healthcare' },
            { time: '6 hours ago', action: 'Patent status updated: US20240012344' },
            { time: '1 day ago', action: 'User registration: john.doe@example.com' }
        ];

        const activityHtml = activities.map(activity => `
            <div class="mb-2">
                <div class="text-muted small">${activity.time}</div>
                <div>${activity.action}</div>
            </div>
        `).join('');

        document.getElementById('recent-activity').innerHTML = activityHtml;
    }

    updateSystemHealth() {
        const healthChecks = [
            { service: 'Database', status: 'healthy', icon: 'fa-check-circle text-success' },
            { service: 'AI Services', status: 'healthy', icon: 'fa-check-circle text-success' },
            { service: 'Neo4j Graph DB', status: 'healthy', icon: 'fa-check-circle text-success' },
            { service: 'Cache', status: 'warning', icon: 'fa-exclamation-triangle text-warning' }
        ];

        const healthHtml = healthChecks.map(check => `
            <div class="mb-2 d-flex justify-content-between">
                <span>${check.service}</span>
                <i class="fas ${check.icon}"></i>
            </div>
        `).join('');

        document.getElementById('system-health').innerHTML = healthHtml;
    }

    updateQuickStats(data) {
        const stats = {
            'Avg. Patents/Day': Math.round(data.overview.patents_last_30_days / 30),
            'Reports Generated': data.overview.total_reports,
            'Top Assignee': data.top_assignees?.top_assignees?.[0]?.assignee || 'N/A',
            'Growth Rate': Math.round((data.overview.patents_last_30_days / Math.max(data.overview.patents_last_year, 1)) * 100) + '%'
        };

        const statsHtml = Object.entries(stats).map(([key, value]) => `
            <div class="mb-2 d-flex justify-content-between">
                <span>${key}:</span>
                <strong>${value}</strong>
            </div>
        `).join('');

        document.getElementById('quick-stats').innerHTML = statsHtml;
    }

    async changePeriod(days) {
        this.currentPeriod = days;
        
        document.querySelectorAll('[data-period]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-period="${days}"]`).classList.add('active');

        try {
            const response = await fetch(`/api/v1/analytics/patents/timeline?days=${days}`);
            if (!response.ok) throw new Error('Failed to load timeline data');
            
            const data = await response.json();
            this.createTimelineChart(data);

        } catch (error) {
            console.error('Error loading timeline data:', error);
        }
    }

    startAutoRefresh() {
        setInterval(() => {
            this.loadDashboardData();
        }, 300000);
    }

    showError(message) {
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.container');
        const firstRow = container.querySelector('.row');
        
        const alertDiv = document.createElement('div');
        alertDiv.innerHTML = alertHtml;
        container.insertBefore(alertDiv.firstElementChild, firstRow);
        
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

const analyticsDashboard = new AnalyticsDashboard();