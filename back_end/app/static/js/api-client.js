/**
 * Centralized API client with authentication support
 */
class ApiClient {
    constructor() {
        this.baseURL = '/api/v1';
        this.defaultTimeout = 30000; // 30 seconds
    }

    /**
     * Make authenticated API request with retry logic
     */
    async request(endpoint, options = {}, retryOnAuth = true) {
        const url = `${this.baseURL}${endpoint}`;
        const controller = new AbortController();
        
        // Set timeout
        const timeoutId = setTimeout(() => {
            controller.abort();
        }, options.timeout || this.defaultTimeout);

        try {
            const response = await fetch(url, {
                signal: controller.signal,
                ...options,
                headers: {
                    ...authManager.getAuthHeaders(),
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            // Handle authentication errors
            if (response.status === 401 && retryOnAuth) {
                const shouldRetry = await authManager.handleAuthResponse(response);
                if (shouldRetry) {
                    // Retry the request once with new token
                    return this.request(endpoint, options, false);
                }
                return null;
            }

            // Handle other HTTP errors
            if (!response.ok) {
                await this.handleHttpError(response);
                return null;
            }

            return response;

        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            
            throw error;
        }
    }

    /**
     * Handle HTTP errors with user-friendly messages
     */
    async handleHttpError(response) {
        let errorMessage = 'An error occurred';
        
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
            errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }

        switch (response.status) {
            case 400:
                authManager.showAlert(errorMessage, 'warning');
                break;
            case 403:
                authManager.showAlert('You do not have permission to perform this action.', 'danger');
                break;
            case 404:
                authManager.showAlert('The requested resource was not found.', 'warning');
                break;
            case 429:
                authManager.showAlert('Too many requests. Please try again later.', 'warning');
                break;
            case 500:
                authManager.showAlert('Server error. Please try again later.', 'danger');
                break;
            default:
                authManager.showAlert(errorMessage, 'danger');
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}, options = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        return this.request(url, {
            method: 'GET',
            ...options
        });
    }

    /**
     * POST request
     */
    async post(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint, options = {}) {
        return this.request(endpoint, {
            method: 'DELETE',
            ...options
        });
    }

    /**
     * PATCH request
     */
    async patch(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data),
            ...options
        });
    }

    /**
     * Upload file
     */
    async upload(endpoint, file, additionalData = {}, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Add additional form data
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        return this.request(endpoint, {
            method: 'POST',
            body: formData,
            headers: {
                // Don't set Content-Type for FormData (browser sets it with boundary)
                ...authManager.getAuthHeaders(),
                'Content-Type': undefined
            },
            ...options
        });
    }

    /**
     * Download file
     */
    async download(endpoint, params = {}, filename = null) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        const response = await this.request(url, {
            method: 'GET'
        });

        if (!response) return null;

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename || 'download';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.URL.revokeObjectURL(downloadUrl);
        return blob;
    }
}

// API endpoints organized by module
const ApiEndpoints = {
    // Authentication
    auth: {
        login: '/auth/login',
        register: '/auth/register',
        logout: '/auth/logout',
        me: '/auth/me',
        refresh: '/auth/refresh'
    },

    // Patents
    patents: {
        list: '/patents/',
        search: '/patents/search',
        get: (id) => `/patents/${id}`,
        getByNumber: (number) => `/patents/number/${number}`,
        similar: (id) => `/patents/${id}/similar`,
        create: '/patents/',
        update: (id) => `/patents/${id}`,
        delete: (id) => `/patents/${id}`
    },

    // User
    user: {
        dashboard: '/user/dashboard',
        preferences: '/user/preferences',
        recommendations: '/user/recommendations',
        activity: '/user/activity'
    },

    // Chat
    chat: {
        ask: '/chat/ask',
        history: '/chat/history',
        delete: (id) => `/chat/${id}`
    },

    // Reports
    reports: {
        list: '/reports/',
        generate: '/reports/generate',
        get: (id) => `/reports/${id}`,
        delete: (id) => `/reports/${id}`
    },

    // Analytics
    analytics: {
        overview: '/analytics/overview',
        patents: '/analytics/patents',
        searches: '/analytics/searches',
        reports: '/analytics/reports'
    },

    // Notifications
    notifications: {
        list: '/notifications/',
        markRead: (id) => `/notifications/${id}/read`,
        delete: (id) => `/notifications/${id}`
    },

    // Admin
    admin: {
        users: '/admin/users',
        system: '/admin/system',
        settings: '/admin/settings'
    },

    // Export
    export: {
        patents: '/export/patents',
        reports: '/export/reports',
        analytics: '/export/analytics'
    }
};

// Global API client instance
const apiClient = new ApiClient();