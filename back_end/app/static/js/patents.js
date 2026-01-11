class PatentSearch {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 10;
        this.totalPages = 1;
        this.currentQuery = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSearchForm();
    }

    setupEventListeners() {
        document.getElementById('search-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });

        document.getElementById('clear-search').addEventListener('click', () => {
            this.clearSearch();
        });

        document.getElementById('apply-filters').addEventListener('click', () => {
            this.performSearch();
        });

        document.getElementById('results-limit').addEventListener('change', () => {
            this.pageSize = parseInt(document.getElementById('results-limit').value);
            this.currentPage = 1;
            this.performSearch();
        });
    }

    setupSearchForm() {
        this.searchInputs = {
            query: document.getElementById('search-query'),
            title: document.getElementById('title-search'),
            abstract: document.getElementById('abstract-search'),
            assignee: document.getElementById('assignee-search'),
            inventors: document.getElementById('inventors-search'),
            searchMode: document.getElementById('search-mode'),
            sortBy: document.getElementById('sort-by'),
            sortOrder: document.getElementById('sort-order'),
            dateFrom: document.getElementById('date-from'),
            dateTo: document.getElementById('date-to'),
            status: document.getElementById('status')
        };
    }

    buildSearchQuery() {
        const query = {
            limit: this.pageSize,
            offset: (this.currentPage - 1) * this.pageSize
        };

        Object.keys(this.searchInputs).forEach(key => {
            const input = this.searchInputs[key];
            if (input && input.value) {
                if (key === 'inventors') {
                    query[key] = input.value.split(',').map(s => s.trim()).filter(s => s);
                } else if (key === 'dateFrom') {
                    query.filing_date_from = input.value ? new Date(input.value).toISOString() : null;
                } else if (key === 'dateTo') {
                    query.filing_date_to = input.value ? new Date(input.value).toISOString() : null;
                } else if (key !== 'dateFrom' && key !== 'dateTo') {
                    query[key === 'dateFrom' ? 'filing_date_from' : 
                           key === 'dateTo' ? 'filing_date_to' : key] = input.value;
                }
            }
        });

        this.currentQuery = query;
        return query;
    }

    async performSearch() {
        try {
            this.showLoading();
            const query = this.buildSearchQuery();
            
            const response = await apiClient.post(ApiEndpoints.patents.search, query);

            if (!response) {
                return;
            }

            const data = await response.json();
            this.displayResults(data);
            this.updatePagination(data);
            this.updateSearchStats(data);
            this.updateActiveFilters();

        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed. Please try again.');
        }
    }

    displayResults(data) {
        const resultsContainer = document.getElementById('search-results');
        
        if (!data.patents || data.patents.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> No patents found matching your criteria.
                </div>
            `;
            return;
        }

        const patentsHtml = data.patents.map(patent => this.createPatentCard(patent)).join('');
        resultsContainer.innerHTML = patentsHtml;
    }

    createPatentCard(patent) {
        const filingDate = patent.filing_date ? 
            new Date(patent.filing_date).toLocaleDateString() : 'Not specified';
        const statusClass = `status-${patent.status || 'pending'}`;
        const inventorsList = patent.inventors && patent.inventors.length > 0 ? 
            patent.inventors.slice(0, 3).join(', ') + 
            (patent.inventors.length > 3 ? '...' : '') : 'Not specified';

        return `
            <div class="patent-card slide-up">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center mb-2">
                            <h6 class="mb-0 me-3">
                                <a href="#" class="patent-card-link" data-patent-id="${patent.patent_id}">
                                    ${this.highlightText(patent.title)}
                                </a>
                            </h6>
                            <span class="status-badge ${statusClass}">${patent.status || 'Pending'}</span>
                        </div>
                        <p class="text-muted mb-3">
                            ${this.truncateText(patent.abstract, 250)}
                        </p>
                        <div class="row patent-card-meta">
                            <div class="col-md-3 mb-2">
                                <i class="fas fa-hashtag me-2 text-muted"></i>
                                <strong>${patent.patent_id}</strong>
                            </div>
                            <div class="col-md-3 mb-2">
                                <i class="fas fa-calendar-alt me-2 text-muted"></i>
                                ${filingDate}
                            </div>
                            <div class="col-md-4 mb-2">
                                <i class="fas fa-building me-2 text-muted"></i>
                                ${patent.assignee || 'Not specified'}
                            </div>
                            <div class="col-md-2 mb-2 text-end">
                                <span class="badge bg-light text-dark">
                                    ${patent.patent_type || 'Utility'}
                                </span>
                            </div>
                        </div>
                        ${patent.inventors && patent.inventors.length > 0 ? `
                        <div class="mt-2">
                            <small class="text-muted">
                                <i class="fas fa-users me-2"></i>
                                ${inventorsList}
                            </small>
                        </div>
                        ` : ''}
                    </div>
                    <div class="ms-3">
                        <div class="btn-group-vertical">
                            <button class="btn btn-primary btn-sm mb-2" onclick="patentSearch.viewPatentDetails('${patent.patent_id}')" title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-success btn-sm mb-2" onclick="patentSearch.analyzePatent('${patent.patent_id}')" title="AI Analysis">
                                <i class="fas fa-brain"></i>
                            </button>
                            <button class="btn btn-outline-secondary btn-sm" onclick="patentSearch.exportPatent('${patent.patent_id}')" title="Export">
                                <i class="fas fa-download"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
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

    highlightText(text) {
        if (!this.currentQuery.query) return text;
        const regex = new RegExp(`(${this.currentQuery.query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    updatePagination(data) {
        const paginationContainer = document.getElementById('pagination-container');
        
        if (data.total_pages <= 1) {
            paginationContainer.classList.add('d-none');
            return;
        }

        paginationContainer.classList.remove('d-none');
        this.totalPages = data.total_pages;
        
        const paginationHtml = this.createPaginationHTML(data);
        paginationContainer.querySelector('.pagination').innerHTML = paginationHtml;
        
        this.setupPaginationEvents();
    }

    createPaginationHTML(data) {
        let html = '';
        
        const prevDisabled = !data.has_prev ? 'disabled' : '';
        const nextDisabled = !data.has_next ? 'disabled' : '';
        
        html += `
            <li class="page-item ${prevDisabled}" id="prev-page">
                <a class="page-link" href="#" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                </a>
            </li>
        `;
        
        const startPage = Math.max(1, data.page - 2);
        const endPage = Math.min(data.total_pages, data.page + 2);
        
        if (startPage > 1) {
            html += '<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>';
            if (startPage > 2) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const active = i === data.page ? 'active' : '';
            html += `<li class="page-item ${active}"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
        }
        
        if (endPage < data.total_pages) {
            if (endPage < data.total_pages - 1) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${data.total_pages}">${data.total_pages}</a></li>`;
        }
        
        html += `
            <li class="page-item ${nextDisabled}" id="next-page">
                <a class="page-link" href="#" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                </a>
            </li>
        `;
        
        return html;
    }

    setupPaginationEvents() {
        const pageLinks = document.querySelectorAll('.page-link[data-page]');
        pageLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(link.dataset.page);
                this.goToPage(page);
            });
        });

        const prevLink = document.getElementById('prev-page');
        if (prevLink && !prevLink.classList.contains('disabled')) {
            prevLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.goToPage(this.currentPage - 1);
            });
        }

        const nextLink = document.getElementById('next-page');
        if (nextLink && !nextLink.classList.contains('disabled')) {
            nextLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.goToPage(this.currentPage + 1);
            });
        }
    }

    goToPage(page) {
        this.currentPage = page;
        this.performSearch();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    updateSearchStats(data) {
        const statsContainer = document.getElementById('search-stats');
        const start = (data.page - 1) * data.page_size + 1;
        const end = Math.min(data.page * data.page_size, data.total_count);
        
        statsContainer.textContent = `Showing ${start}-${end} of ${data.total_count} results`;
    }

    updateActiveFilters() {
        const filtersContainer = document.getElementById('active-filters');
        const filters = [];

        if (this.currentQuery.query) {
            filters.push(`<span class="badge bg-primary">Search: ${this.currentQuery.query}</span>`);
        }
        if (this.currentQuery.status) {
            filters.push(`<span class="badge bg-info">Status: ${this.currentQuery.status}</span>`);
        }
        if (this.currentQuery.filing_date_from) {
            filters.push(`<span class="badge bg-success">From: ${new Date(this.currentQuery.filing_date_from).toLocaleDateString()}</span>`);
        }
        if (this.currentQuery.filing_date_to) {
            filters.push(`<span class="badge bg-warning">To: ${new Date(this.currentQuery.filing_date_to).toLocaleDateString()}</span>`);
        }

        if (filters.length === 0) {
            filtersContainer.innerHTML = '<p class="text-muted small mb-0">No filters applied.</p>';
        } else {
            filtersContainer.innerHTML = filters.join(' ') + 
                '<button class="btn btn-sm btn-outline-danger ms-2" onclick="patentSearch.clearFilters()">Clear All</button>';
        }
    }

    clearSearch() {
        Object.keys(this.searchInputs).forEach(key => {
            if (this.searchInputs[key]) {
                this.searchInputs[key].value = '';
            }
        });
        this.currentPage = 1;
        document.getElementById('search-results').innerHTML = '<p class="text-muted">Enter a search query to see results.</p>';
        document.getElementById('pagination-container').classList.add('d-none');
        document.getElementById('search-stats').textContent = '';
        this.updateActiveFilters();
    }

    clearFilters() {
        this.searchInputs.dateFrom.value = '';
        this.searchInputs.dateTo.value = '';
        this.searchInputs.status.value = '';
        this.performSearch();
    }

    showLoading() {
        document.getElementById('search-results').innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Searching patents...</p>
            </div>
        `;
    }

    showError(message) {
        if (typeof authManager !== 'undefined') {
            authManager.showAlert(message, 'danger');
        } else {
            document.getElementById('search-results').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> ${message}
                </div>
            `;
        }
    }

    async viewPatentDetails(patentId) {
        try {
            const response = await apiClient.get(ApiEndpoints.patents.get(patentId));

            if (!response) {
                return;
            }

            const patent = await response.json();
            this.showPatentModal(patent);
        } catch (error) {
            console.error('Error fetching patent details:', error);
        }
    }

    async     analyzePatent(patentId) {
        window.location.href = `/chat?patent=${patentId}`;
    }

    async exportPatent(patentId) {
        try {
            const response = await apiClient.download(ApiEndpoints.export.patents, { id: patentId }, `patent_${patentId}.pdf`);
            if (!response) {
                authManager.showAlert('Failed to export patent', 'warning');
            }
        } catch (error) {
            console.error('Export error:', error);
            authManager.showAlert('Export failed. Please try again.', 'danger');
        }
    }

    showPatentModal(patent) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Patent Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <h6>${patent.title}</h6>
                        <p><strong>Patent ID:</strong> ${patent.patent_id}</p>
                        <p><strong>Abstract:</strong> ${patent.abstract}</p>
                        <p><strong>Assignee:</strong> ${patent.assignee || 'Not specified'}</p>
                        <p><strong>Inventors:</strong> ${patent.inventors ? patent.inventors.join(', ') : 'Not specified'}</p>
                        <p><strong>Status:</strong> ${this.getStatusBadge(patent.status)}</p>
                        <p><strong>Filing Date:</strong> ${patent.filing_date ? new Date(patent.filing_date).toLocaleDateString() : 'Not specified'}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="patentSearch.analyzePatent('${patent.patent_id}')">
                            <i class="fas fa-brain"></i> Analyze with AI
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
}

const patentSearch = new PatentSearch();