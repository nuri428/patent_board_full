/**
 * Authentication middleware for protecting routes
 */
class AuthMiddleware {
    constructor() {
        this.publicRoutes = [
            '/login',
            '/register',
            '/health',
            '/api/v1/auth/login',
            '/api/v1/auth/register'
        ];
    }

    /**
     * Check if current route requires authentication
     */
    requiresAuth(currentPath) {
        return !this.publicRoutes.some(route => currentPath.startsWith(route));
    }

    /**
     * Protect current page
     */
    protectPage() {
        const currentPath = window.location.pathname;
        
        if (this.requiresAuth(currentPath) && !authManager.isAuthenticated()) {
            // Store current path for redirect after login
            const redirectUrl = encodeURIComponent(currentPath + window.location.search);
            window.location.href = `/login?redirect=${redirectUrl}`;
            return false;
        }
        
        return true;
    }

    /**
     * Initialize auth protection
     */
    init() {
        // Check authentication on page load
        if (!this.protectPage()) {
            return; // Redirecting to login
        }

        // Add logout button to navigation
        this.addLogoutButton();
        
        // Add user info to navigation
        this.updateNavigation();
    }

    /**
     * Add logout functionality
     */
    addLogoutButton() {
        const logoutBtn = document.querySelector('[data-action="logout"]');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
        }
    }

    /**
     * Update navigation with user info
     */
    updateNavigation() {
        const user = authManager.getCurrentUser();
        if (!user) return;

        // Update user name display
        const userNameElements = document.querySelectorAll('[data-user="name"]');
        userNameElements.forEach(element => {
            element.textContent = user.full_name || user.email;
        });

        // Update user email display
        const userEmailElements = document.querySelectorAll('[data-user="email"]');
        userEmailElements.forEach(element => {
            element.textContent = user.email;
        });

        // Show/hide admin-only elements
        const adminElements = document.querySelectorAll('[data-require="admin"]');
        adminElements.forEach(element => {
            if (user.is_admin) {
                element.style.display = '';
            } else {
                element.style.display = 'none';
            }
        });
    }

    /**
     * Handle user logout
     */
    async logout() {
        try {
            // Call logout API
            await apiClient.post(ApiEndpoints.auth.logout);
        } catch (error) {
            console.error('Logout API error:', error);
        } finally {
            // Clear local auth data regardless of API success
            authManager.clearAuth();
            
            // Show success message
            authManager.showAlert('Logged out successfully', 'success');
            
            // Redirect to login page
            setTimeout(() => {
                window.location.href = '/login';
            }, 1000);
        }
    }

    /**
     * Handle session expiration
     */
    handleSessionExpired() {
        authManager.showAlert('Your session has expired. Please login again.', 'warning');
        authManager.clearAuth();
        
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    }

    /**
     * Periodic token validation
     */
    startTokenValidation() {
        // Check token expiration every minute
        setInterval(() => {
            if (!authManager.isAuthenticated()) {
                this.handleSessionExpired();
            }
        }, 60000);
    }
}

// Global auth middleware instance
const authMiddleware = new AuthMiddleware();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    authMiddleware.init();
    authMiddleware.startTokenValidation();
});