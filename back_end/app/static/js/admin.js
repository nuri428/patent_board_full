class AdminDashboard {
    constructor() {
        this.patents = [];
        this.statistics = {};
        this.statusChart = null;
        this.assigneeChart = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStatistics();
        this.loadPatents();
    }

    setupEventListeners() {
        document.getElementById('add-patent-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addPatent();
        });

        document.getElementById('clear-form').addEventListener('click', () => {
            this.clearForm();
        });

        document.getElementById('refresh-patents').addEventListener('click', () => {
            this.loadPatents();
        });

        document.getElementById('export-csv').addEventListener('click', () => {
            this.exportData('csv');
        });

        document.getElementById('export-excel').addEventListener('click', () => {
            this.exportData('excel');
        });

        document.getElementById('export-pdf').addEventListener('click', () => {
            this.exportData('pdf');
        });
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/v1/admin/statistics');
            if (!response.ok) throw new Error('Failed to load statistics');
            
            const stats = await response.json();
            this.statistics = stats;
            this.updateStatisticsDisplay(stats);
            this.createCharts(stats);

        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    updateStatisticsDisplay(stats) {
        document.getElementById('total-patents').textContent = stats.total_patents || 0;
        document.getElementById('granted-patents').textContent = stats.status_distribution.granted || 0;
        document.getElementById('pending-patents').textContent = stats.status_distribution.pending || 0;
        document.getElementById('total-companies').textContent = Object.keys(stats.top_assignees || {}).length;
    }

    createCharts(stats) {
        this.createStatusChart(stats.status_distribution || {});
        this.createAssigneeChart(stats.top_assignees || {});
    }

    createStatusChart(statusData) {
        const ctx = document.getElementById('status-chart').getContext('2d');
        
        if (this.statusChart) {
            this.statusChart.destroy();
        }

        const colors = {
            pending: '#ffc107',
            granted: '#198754',
            expired: '#6c757d',
            abandoned: '#dc3545'
        };

        this.statusChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(statusData).map(s => s.charAt(0).toUpperCase() + s.slice(1)),
                datasets: [{
                    data: Object.values(statusData),
                    backgroundColor: Object.keys(statusData).map(s => colors[s] || '#6c757d'),
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
                    }
                }
            }
        });
    }

    createAssigneeChart(assigneeData) {
        const ctx = document.getElementById('assignee-chart').getContext('2d');
        
        if (this.assigneeChart) {
            this.assigneeChart.destroy();
        }

        const top10 = Object.entries(assigneeData).slice(0, 10);

        this.assigneeChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: top10.map(([assignee]) => assignee),
                datasets: [{
                    label: 'Patent Count',
                    data: top10.map(([, count]) => count),
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    async loadPatents() {
        try {
            const response = await fetch('/api/v1/patents?limit=50');
            if (!response.ok) throw new Error('Failed to load patents');
            
            const patents = await response.json();
            this.patents = patents;
            this.displayPatents(patents);

        } catch (error) {
            console.error('Error loading patents:', error);
            this.showError('Failed to load patents');
        }
    }

    displayPatents(patents) {
        const tbody = document.getElementById('patents-table-body');
        
        if (!patents || patents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No patents found.</td></tr>';
            return;
        }

        const patentsHtml = patents.slice(0, 20).map(patent => this.createPatentRow(patent)).join('');
        tbody.innerHTML = patentsHtml;
    }

    createPatentRow(patent) {
        const filingDate = patent.filing_date ? 
            new Date(patent.filing_date).toLocaleDateString() : 'Not specified';
        const statusBadge = this.getStatusBadge(patent.status);

        return `
            <tr>
                <td><code>${patent.patent_id}</code></td>
                <td>${this.truncateText(patent.title, 50)}</td>
                <td>${patent.assignee || 'Not specified'}</td>
                <td>${statusBadge}</td>
                <td>${filingDate}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="adminDashboard.editPatent('${patent.patent_id}')" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-info" onclick="adminDashboard.updateStatus('${patent.patent_id}')" title="Update Status">
                            <i class="fas fa-exchange-alt"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="adminDashboard.deletePatent('${patent.patent_id}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
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

    async addPatent() {
        try {
            const patentData = this.collectFormData();
            
            const response = await fetch('/api/v1/admin/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(patentData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to add patent');
            }

            this.showSuccess('Patent added successfully!');
            this.clearForm();
            this.loadPatents();
            this.loadStatistics();

        } catch (error) {
            console.error('Error adding patent:', error);
            this.showError(error.message || 'Failed to add patent');
        }
    }

    collectFormData() {
        const inventorsText = document.getElementById('patent-inventors').value;
        const inventors = inventorsText 
            ? inventorsText.split(',').map(s => s.trim()).filter(s => s)
            : [];

        return {
            patent_id: document.getElementById('patent-id').value,
            title: document.getElementById('patent-title').value,
            abstract: document.getElementById('patent-abstract').value,
            assignee: document.getElementById('patent-assignee').value || null,
            status: document.getElementById('patent-status').value,
            inventors: inventors,
            filing_date: document.getElementById('patent-filing-date').value 
                ? new Date(document.getElementById('patent-filing-date').value).toISOString() 
                : null
        };
    }

    clearForm() {
        document.getElementById('add-patent-form').reset();
    }

    async editPatent(patentId) {
        const patent = this.patents.find(p => p.patent_id === patentId);
        if (!patent) return;

        this.populateForm(patent);
        
        document.getElementById('patent-id').readOnly = true;
        document.getElementById('add-patent-form').scrollIntoView({ behavior: 'smooth' });
    }

    populateForm(patent) {
        document.getElementById('patent-id').value = patent.patent_id;
        document.getElementById('patent-title').value = patent.title;
        document.getElementById('patent-abstract').value = patent.abstract;
        document.getElementById('patent-assignee').value = patent.assignee || '';
        document.getElementById('patent-status').value = patent.status;
        document.getElementById('patent-inventors').value = patent.inventors ? patent.inventors.join(', ') : '';
        document.getElementById('patent-filing-date').value = patent.filing_date 
            ? new Date(patent.filing_date).toISOString().split('T')[0] 
            : '';
    }

    async updateStatus(patentId) {
        const patent = this.patents.find(p => p.patent_id === patentId);
        if (!patent) return;

        const newStatus = prompt(`Update status for ${patentId} (current: ${patent.status}):\n\nOptions: pending, granted, expired, abandoned`, patent.status);
        
        if (!newStatus || newStatus === patent.status) return;

        try {
            const response = await fetch(`/api/v1/admin/${patentId}/status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newStatus)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to update status');
            }

            this.showSuccess('Status updated successfully!');
            this.loadPatents();
            this.loadStatistics();

        } catch (error) {
            console.error('Error updating status:', error);
            this.showError(error.message || 'Failed to update status');
        }
    }

    async deletePatent(patentId) {
        if (!confirm(`Are you sure you want to delete patent ${patentId}?`)) return;

        try {
            const response = await fetch(`/api/v1/admin/${patentId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to delete patent');
            }

            this.showSuccess('Patent deleted successfully!');
            this.loadPatents();
            this.loadStatistics();

        } catch (error) {
            console.error('Error deleting patent:', error);
            this.showError(error.message || 'Failed to delete patent');
        }
    }

    async exportData(format) {
        try {
            const response = await fetch(`/api/v1/export/patents/${format}`);
            if (!response.ok) throw new Error(`Failed to export ${format.toUpperCase()}`);
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
            a.download = `patents_export_${timestamp}.${format}`;
            
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showSuccess(`Patents exported as ${format.toUpperCase()} successfully!`);

        } catch (error) {
            console.error(`Error exporting ${format}:`, error);
            this.showError(`Failed to export patents as ${format.toUpperCase()}`);
        }
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
                ${message}
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

const adminDashboard = new AdminDashboard();