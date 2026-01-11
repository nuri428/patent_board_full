/**
 * Authentication utilities for token management
 */
class AuthManager {
    constructor() {
        this.tokenKey = 'access_token';
        this.userKey = 'user_data';
        this.refreshKey = 'refresh_token';
    }

    /**
     * Store authentication tokens and user data
     */
    setAuthData(token, user = null, refreshToken = null) {
        localStorage.setItem(this.tokenKey, token);
        if (user) {
            localStorage.setItem(this.userKey, JSON.stringify(user));
        }
        if (refreshToken) {
            localStorage.setItem(this.refreshKey, refreshToken);
        }
    }

    /**
     * Get current access token
     */
    getAccessToken() {
        return localStorage.getItem(this.tokenKey);
    }

    /**
     * Get refresh token
     */
    getRefreshToken() {
        return localStorage.getItem(this.refreshKey);
    }

    /**
     * Get current user data
     */
    getCurrentUser() {
        const userData = localStorage.getItem(this.userKey);
        return userData ? JSON.parse(userData) : null;
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        const token = this.getAccessToken();
        if (!token) return false;
        
        try {
            // Parse JWT token to check expiration
            const payload = JSON.parse(atob(token.split('.')[1]));
            const currentTime = Math.floor(Date.now() / 1000);
            return payload.exp > currentTime;
        } catch (error) {
            console.error('Error parsing token:', error);
            return false;
        }
    }

    /**
     * Clear all authentication data
     */
    clearAuth() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
        localStorage.removeItem(this.refreshKey);
    }

    /**
     * Refresh access token using refresh token
     */
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        try {
            const response = await fetch('/api/v1/auth/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();
            this.setAuthData(data.access_token, data.user, data.refresh_token);
            return data.access_token;
        } catch (error) {
            console.error('Token refresh error:', error);
            this.clearAuth();
            this.redirectToLogin();
            throw error;
        }
    }

    /**
     * Redirect to login page
     */
    redirectToLogin() {
        const currentPath = window.location.pathname;
        if (currentPath !== '/login') {
            window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
        }
    }

    /**
     * Get authorization headers for API requests
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };

        const token = this.getAccessToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    /**
     * Handle API response with authentication errors
     */
    async handleAuthResponse(response) {
        if (response.status === 401) {
            // Token expired or invalid
            try {
                // Try to refresh token
                await this.refreshAccessToken();
                return true; // Indicate that request should be retried
            } catch (error) {
                // Refresh failed, redirect to login
                this.redirectToLogin();
                return false;
            }
        } else if (response.status === 403) {
            // Insufficient permissions
            this.showPermissionError();
            return false;
        }

        return true;
    }

    /**
     * Show permission error message
     */
    showPermissionError() {
        this.showAlert('You do not have permission to perform this action.', 'danger');
    }

    /**
     * Show alert message (common utility)
     */
    showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.auth-alert');
        existingAlerts.forEach(alert => alert.remove());

        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show auth-alert" role="alert">
                <i class="fas fa-${type === 'danger' ? 'exclamation-triangle' : 'info-circle'}"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.container');
        if (container) {
            const alertDiv = document.createElement('div');
            alertDiv.innerHTML = alertHtml;
            container.insertBefore(alertDiv.firstElementChild, container.firstChild);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                const alert = container.querySelector('.auth-alert');
                if (alert) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 5000);
        }
    }
}

// Global instance
const authManager = new AuthManager();