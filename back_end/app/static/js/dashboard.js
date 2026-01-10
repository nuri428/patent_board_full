class UserDashboard {
    constructor() {
        this.dashboardData = {};
        this.preferences = {};
        this.charts = {};
        this.refreshInterval = null;
        this.currentPeriod = 7;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.loadUserPreferences();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        document.getElementById('theme-select').addEventListener('change', (e) => {
            this.updateTheme(e.target.value);
        });

        document.getElementById('notifications-toggle').addEventListener('change', (e) => {
            this.updateNotifications(e.target.checked);
        });

        document.getElementById('refresh-interval').addEventListener('change', (e) => {
            this.updateRefreshInterval(parseInt(e.target.value));
        });

        document.querySelectorAll('[data-period]').forEach(button => {
            button.addEventListener('click', (e) => {
                this.changeActivityPeriod(parseInt(e.target.dataset.period));
            });
        });
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/v1/user/dashboard');
            if (!response.ok) throw new Error('Failed to load dashboard data');
            
            const data = await response.json();
            this.dashboardData = data;
            this.updateOverviewCards(data.overview);
            this.updateRecentPatents(data.recent_patents);
            this.createActivityChart(data);
            this.loadRecommendations();

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    updateOverviewCards(overview) {
        document.getElementById('total-patents').textContent = overview.total_patents.toLocaleString();
        document.getElementById('recent-patents').textContent = overview.recent_patents_count;
        document.getElementById('recent-reports').textContent = overview.recent_reports_count;
        document.getElementById('recent-chats').textContent = overview.recent_chats_count;
    }

    updateRecentPatents(patents) {
        const tbody = document.getElementById('recent-patents-table');
        
        if (!patents || patents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No recent patents found.</td></tr>';
            return;
        }

        const patentsHtml = patents.map(patent => `
            <tr>
                <td><code>${patent.patent_id}</code></td>
                <td>${this.truncateText(patent.title, 40)}</td>
                <td>${this.getStatusBadge(patent.status)}</td>
                <td>${new Date(patent.created_at).toLocaleDateString()}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary btn-sm" onclick="userDashboard.viewPatent('${patent.patent_id}')" title="View">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-success btn-sm" onclick="userDashboard.analyzePatent('${patent.patent_id}')" title="Analyze">
                            <i class="fas fa-brain"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        tbody.innerHTML = patentsHtml;
    }

    createActivityChart(data) {
        const ctx = document.getElementById('activity-chart').getContext('2d');
        
        if (this.charts.activity) {
            this.charts.activity.destroy();
        }

        const patentsActivity = data.patents_activity || [];
        const reportsActivity = data.reports_activity || [];

        const dates = [...new Set([
            ...patentsActivity.map(item => item.date),
            ...reportsActivity.map(item => item.date)
        ])].sort();

        const patentsData = dates.map(date => {
            const found = patentsActivity.find(item => item.date === date);
            return found ? found.count : 0;
        });

        const reportsData = dates.map(date => {
            const found = reportsActivity.find(item => item.date === date);
            return found ? found.count : 0;
        });

        this.charts.activity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates.map(date => new Date(date).toLocaleDateString()),
                datasets: [
                    {
                        label: 'Patents Added',
                        data: patentsData,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Reports Generated',
                        data: reportsData,
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
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

    async loadRecommendations() {
        try {
            const response = await fetch('/api/v1/user/recommendations');
            if (!response.ok) throw new Error('Failed to load recommendations');
            
            const recommendations = await response.json();
            this.updateRecommendations(recommendations);

        } catch (error) {
            console.error('Error loading recommendations:', error);
            document.getElementById('recommended-patents').innerHTML = 
                '<p class="text-danger small">Failed to load recommendations.</p>';
        }
    }

    updateRecommendations(recommendations) {
        const recommendedPatents = recommendations.recommended_patents || [];
        const trendingTopics = suggestionsuggested_searches || [];
        const trendingAssignees = recommendations.trending_assignees || [];

        const patentsHtml = recommendedPatents.map(patent => `
            <div class="mb-2">
                <small class="text-muted">${patent.patent_id}</small><br>
                <a href="#" onclick="userDashboard.viewPatent('${patent.patent_id}')" class="text-decoration-none">
                    ${this.truncateText(patent.title, 30)}
                </a>
                ${patent.assignee ? `<br><small class="text-muted">${patent.assignee}</small>` : ''}
            </div>
        `).join('');

        const topicsHtml = trendingTopics.map(topic => `
            <span class="badge bg-primary me-1 mb-1" style="cursor: pointer;" onclick="userDashboard.searchTopic('${topic}')">
                ${topic}
            </span>
        `).join('');

        const assigneesHtml = trendingAssignees.map(item => `
            <div class="mb-1">
                <small>${item.assignee}</small>
                <span class="badge bg-secondary float-end">${item.patent_count}</span>
            </div>
        `).join('');

        document.getElementById('recommended-patents').innerHTML = patentsHtml || '<p class="text-muted small">No recommendations available.</p>';
        document.getElementById('trending-topics').innerHTML = topicsHtml || '<p class="text-muted small">No trends available.</p>';
    }

    async loadUserPreferences() {
        try {
            const response = await fetch('/api/v1/user/preferences');
            if (!response.ok) throw new Error('Failed to load preferences');
            
            this.preferences = await response.json();
            this.applyPreferences();

        } catch (error) {
            console.error('Error loading preferences:', error);
        }
    }

    applyPreferences() {
        if (this.preferences.theme) {
            document.getElementById('theme-select').value = this.preferences.theme;
        }

        if (this.preferences.notifications && this.preferences.notifications.email !== undefined) {
            document.getElementById('notifications-toggle').checked = this.preferences.notifications.email;
        }

        if (this.preferences.dashboard && this.preferences.dashboard.refresh_interval !== undefined) {
            document.getElementById('refresh-interval').value = this.preferences.dashboard.refresh_interval;
            this.updateRefreshInterval(this.preferences.dashboard.refresh_interval);
        }
    }

    async savePreferences() {
        const preferences = {
            theme: document.getElementById('theme-select').value,
            notifications: {
                email: document.getElementById('notifications-toggle').checked
            },
            dashboard: {
                refresh_interval: parseInt(document.getElementById('refresh-interval').value)
            }
        };

        try {
            const response = await fetch('/api/v1/user/preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(preferences)
            });

            if (!response.ok) throw new Error('Failed to save preferences');
            
            this.preferences = preferences;
            this.showSuccess('Preferences saved successfully!');

        } catch (error) {
            console.error('Error saving preferences:', error);
            this.showError('Failed to save preferences');
        }
    }

    updateTheme(theme) {
        document.body.className = theme === 'dark' ? 'bg-dark text-light' : '';
        this.showSuccess(`Theme changed to ${theme}`);
    }

    updateNotifications(enabled) {
        this.showSuccess(`Email notifications ${enabled ? 'enabled' : 'disabled'}`);
    }

    updateRefreshInterval(seconds) {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        if (seconds > 0) {
            this.refreshInterval = setInterval(() => {
                this.loadDashboardData();
            }, seconds * 1000);
        }

        this.showSuccess(`Refresh interval set to ${seconds > 0 ? seconds/60 + ' minutes' : 'disabled'}`);
    }

    async changeActivityPeriod(days) {
        this.currentPeriod = days;
        
        document.querySelectorAll('[data-period]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-period="${days}"]`).classList.add('active');

        try {
            const response = await fetch(`/api/v1/user/activity?days=${days}`);
            if (!response.ok) throw new Error('Failed to load activity data');
            
            const data = await response.json();
            this.createActivityChart(data);

        } catch (error) {
            console.error('Error loading activity data:', error);
        }
    }

    startAutoRefresh() {
        const defaultInterval = 300; // 5 minutes
        this.updateRefreshInterval(defaultInterval);
    }

    newPatent() {
        window.location.href = '/admin#add-patent';
    }

    newReport() {
        window.location.href = '/reports';
    }

    startChat() {
        window.location.href = '/chat';
    }

    viewAnalytics() {
        window.location.href = '/analytics';
    }

    viewPatent(patentId) {
        window.location.href = `/patents?search=${patentId}`;
    }

    analyzePatent(patentId) {
        window.location.href = `/chat?patent=${patentId}`;
    }

    searchTopic(topic) {
        window.location.href = `/patents?search=${encodeURIComponent(topic)}`;
    }

    getStatusBadge(status) {
        const badges = {
            pending: '<span class="badge bg-warning">Pending</span>',
            granted: '<span class="badge bg-success">Granted</span>',
            expired: '<span class="badge bg-secondary">Expired</span>',
            abandoned: '<span class="badge bg-danger">Abandoned</span>'
        };
        return badges[status] || '<span class="badge bg-secondary">Unknown</span>';
    }

    truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showAlert(message, type) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i> ${message}
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

const userDashboard = new UserDashboard();