class NotificationCenter {
    constructor() {
        this.notifications = [];
        this.unreadCount = 0;
        this.preferences = {};
        this.websocket = null;
        this.init();
    }

    init() {
        this.loadPreferences();
        this.loadNotifications();
        this.setupWebSocketConnection();
        this.setupEventListeners();
        this.createNotificationUI();
    }

    setupWebSocketConnection() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/v1/notifications/ws/user_${this.getUserId()}`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onmessage = (event) => {
                const notification = JSON.parse(event.data);
                this.handleIncomingNotification(notification);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket connection closed');
                setTimeout(() => this.setupWebSocketConnection(), 5000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to establish WebSocket connection:', error);
        }
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.notification-item')) {
                this.handleNotificationClick(e.target.closest('.notification-item'));
            }
            
            if (e.target.closest('[data-action="mark-read"]')) {
                e.preventDefault();
                this.markNotificationAsRead(e.target.closest('[data-notification-id]').dataset.notificationId);
            }
            
            if (e.target.closest('[data-action="delete"]')) {
                e.preventDefault();
                this.deleteNotification(e.target.closest('[data-notification-id]').dataset.notificationId);
            }
            
            if (e.target.closest('[data-action="mark-all-read"]')) {
                e.preventDefault();
                this.markAllAsRead();
            }
        });
    }

    createNotificationUI() {
        const notificationHTML = `
            <div class="position-fixed top-0 end-0 p-3" style="z-index: 1050; max-width: 400px;">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="fas fa-bell"></i> 
                            Notifications 
                            <span class="badge bg-danger ms-2" id="notification-badge" style="display: none;">0</span>
                        </h6>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                <i class="fas fa-cog"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" data-action="mark-all-read">Mark All Read</a></li>
                                <li><a class="dropdown-item" href="/notifications/preferences">Preferences</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="#" data-action="test-notification">Test Notification</a></li>
                            </ul>
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    <div class="card-body" id="notifications-container" style="max-height: 400px; overflow-y: auto;">
                        <div class="text-center text-muted">
                            <i class="fas fa-bell fa-2x mb-2"></i>
                            <p>Loading notifications...</p>
                        </div>
                    </div>
                    <div class="card-footer text-end">
                        <small class="text-muted">Click a notification to view details</small>
                    </div>
                </div>
            </div>
        `;

        const notificationContainer = document.createElement('div');
        notificationContainer.innerHTML = notificationHTML;
        notificationContainer.id = 'notification-center';
        document.body.appendChild(notificationContainer);
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/v1/notifications/');
            if (!response.ok) throw new Error('Failed to load notifications');
            
            const data = await response.json();
            this.notifications = data.notifications || [];
            this.updateNotificationDisplay();
            this.updateUnreadCount();

        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    handleIncomingNotification(notification) {
        this.notifications.unshift(notification);
        this.updateNotificationDisplay();
        this.updateUnreadCount();
        this.showDesktopNotification(notification);
        
        if (this.preferences.sound_enabled && this.notificationSound) {
            this.playNotificationSound();
        }
    }

    updateNotificationDisplay() {
        const container = document.getElementById('notifications-container');
        
        if (!this.notifications || this.notifications.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-bell fa-2x mb-2"></i>
                    <p>No notifications</p>
                </div>
            `;
            return;
        }

        const notificationsHTML = this.notifications.map(notification => 
            this.createNotificationElement(notification)
        ).join('');
        
        container.innerHTML = notificationsHTML;
    }

    createNotificationElement(notification) {
        const isRead = notification.read || false;
        const typeIcon = this.getNotificationIcon(notification.type);
        const bgClass = isRead ? 'bg-light' : 'bg-white';
        const borderClass = isRead ? 'border-muted' : 'border-primary';
        const textClass = isRead ? 'text-muted' : '';
        
        return `
            <div class="notification-item ${borderClass} border mb-2 p-2 ${bgClass}" 
                 data-notification-id="${notification.id}"
                 style="cursor: pointer; position: relative;">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="d-flex">
                        <div class="me-2">${typeIcon}</div>
                        <div>
                            <h6 class="mb-1 ${textClass}">${notification.title}</h6>
                            <p class="mb-1 small ${textClass}">${notification.message}</p>
                            <small class="text-muted">
                                ${new Date(notification.timestamp).toLocaleString()}
                            </small>
                        </div>
                    </div>
                    <div class="dropdown">
                        <button class="btn btn-sm" data-bs-toggle="dropdown">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" data-action="mark-read">Mark as Read</a></li>
                            <li><a class="dropdown-item" href="#" data-action="delete">Delete</a></li>
                        </ul>
                    </div>
                </div>
                ${!isRead ? '<div class="position-absolute top-0 start-0 bg-primary" style="width: 4px; height: 4px; border-radius: 50%;"></div>' : ''}
            </div>
        `;
    }

    getNotificationIcon(type) {
        const icons = {
            report_completion: '<i class="fas fa-file-alt text-success"></i>',
            patent_update: '<i class="fas fa-sync text-info"></i>',
            new_patent: '<i class="fas fa-plus text-primary"></i>',
            system_alert: '<i class="fas fa-exclamation-triangle text-warning"></i>',
            test: '<i class="fas fa-bell text-secondary"></i>'
        };
        return icons[type] || '<i class="fas fa-info-circle text-secondary"></i>';
    }

    updateUnreadCount() {
        const unreadCount = this.notifications.filter(n => !n.read).length;
        this.unreadCount = unreadCount;
        
        const badge = document.getElementById('notification-badge');
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount > 99 ? '99+' : unreadCount.toString();
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }

        document.title = unreadCount > 0 ? `(${unreadCount}) Patent Board` : 'Patent Board';
    }

    handleNotificationClick(notificationElement) {
        const notificationId = notificationElement.dataset.notificationId;
        const notification = this.notifications.find(n => n.id === notificationId);
        
        if (!notification) return;
        
        if (!notification.read) {
            this.markNotificationAsRead(notificationId);
        }
        
        this.showNotificationDetails(notification);
    }

    showNotificationDetails(notification) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${notification.title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${notification.message}</p>
                        ${notification.data ? `<pre>${JSON.stringify(notification.data, null, 2)}</pre>` : ''}
                        <small class="text-muted">
                            ${new Date(notification.timestamp).toLocaleString()}
                        </small>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
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

    async markNotificationAsRead(notificationId) {
        try {
            const response = await fetch(`/api/v1/notifications/mark-read/${notificationId}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const notification = this.notifications.find(n => n.id === notificationId);
                if (notification) {
                    notification.read = true;
                }
                this.updateNotificationDisplay();
                this.updateUnreadCount();
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/api/v1/notifications/mark-all-read', {
                method: 'POST'
            });
            
            if (response.ok) {
                this.notifications.forEach(n => n.read = true);
                this.updateNotificationDisplay();
                this.updateUnreadCount();
            }
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
        }
    }

    async deleteNotification(notificationId) {
        if (!confirm('Are you sure you want to delete this notification?')) return;
        
        try {
            const response = await fetch(`/api/v1/notifications/${notificationId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.notifications = this.notifications.filter(n => n.id !== notificationId);
                this.updateNotificationDisplay();
                this.updateUnreadCount();
            }
        } catch (error) {
            console.error('Error deleting notification:', error);
        }
    }

    showDesktopNotification(notification) {
        if (!this.preferences.desktop_notifications || !("Notification" in window)) return;
        
        if (Notification.permission === "default") {
            Notification.requestPermission();
        } else if (Notification.permission === "granted") {
            const desktopNotification = new Notification(notification.title, {
                body: notification.message,
                icon: '/static/icons/notification-icon.png',
                tag: notification.id
            });
            
            desktopNotification.onclick = () => {
                this.showNotificationDetails(notification);
                desktopNotification.close();
            };
            
            setTimeout(() => desktopNotification.close(), 5000);
        }
    }

    async loadPreferences() {
        try {
            const response = await fetch('/api/v1/notifications/preferences');
            if (!response.ok) return;
            
            this.preferences = await response.json();
            this.notificationSound = new Audio('/static/sounds/notification.mp3');
            
        } catch (error) {
            console.error('Error loading notification preferences:', error);
        }
    }

    playNotificationSound() {
        if (this.notificationSound) {
            this.notificationSound.volume = 0.3;
            this.notificationSound.play().catch(e => console.log('Sound play failed:', e));
        }
    }

    async testNotification() {
        try {
            const response = await fetch('/api/v1/notifications/test', {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccess('Test notification sent!');
            } else {
                this.showError('Failed to send test notification');
            }
        } catch (error) {
            console.error('Error sending test notification:', error);
            this.showError('Failed to send test notification');
        }
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'danger');
    }

    showToast(message, type) {
        const toastHTML = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert" style="position: fixed; bottom: 20px; right: 20px; z-index: 1060;">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        const toastContainer = document.createElement('div');
        toastContainer.innerHTML = toastHTML;
        document.body.appendChild(toastContainer.firstElementChild);
        
        const toast = new bootstrap.Toast(toastContainer.firstElementChild);
        toast.show();
        
        setTimeout(() => {
            if (toastContainer.parentNode) {
                toastContainer.parentNode.removeChild(toastContainer);
            }
        }, 3000);
    }

    getUserId() {
        return localStorage.getItem('user_id') || 'guest';
    }
}

const notificationCenter = new NotificationCenter();