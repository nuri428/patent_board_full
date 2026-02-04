import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from './AuthContext';

const NotificationsContext = createContext(null);

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';
const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');

export const NotificationsProvider = ({ children }) => {
    const { user } = useAuth();
    const [notifications, setNotifications] = useState([]);
    const [isConnected, setIsConnected] = useState(false);
    const [connectionError, setConnectionError] = useState(null);
    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const reconnectAttempts = useRef(0);
    const MAX_RECONNECT_ATTEMPTS = 5;
    const RECONNECT_DELAY = 3000;

    // Add a notification to the list
    const addNotification = useCallback((notification) => {
        const newNotification = {
            id: Date.now() + Math.random().toString(36).substr(2, 9),
            timestamp: new Date().toISOString(),
            read: false,
            ...notification,
        };
        setNotifications((prev) => [newNotification, ...prev]);
        return newNotification.id;
    }, []);

    // Remove a notification
    const removeNotification = useCallback((id) => {
        setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, []);

    // Mark notification as read
    const markAsRead = useCallback((id) => {
        setNotifications((prev) =>
            prev.map((n) => (n.id === id ? { ...n, read: true } : n))
        );
    }, []);

    // Mark all as read
    const markAllAsRead = useCallback(() => {
        setNotifications((prev) =>
            prev.map((n) => ({ ...n, read: true }))
        );
    }, []);

    // Clear all notifications
    const clearAll = useCallback(() => {
        setNotifications([]);
    }, []);

    // Connect WebSocket
    const connect = useCallback(() => {
        if (!user?.id) {
            console.log('[WebSocket] No user ID, skipping connection');
            return;
        }

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            console.log('[WebSocket] Already connected');
            return;
        }

        try {
            const wsUrl = `${WS_BASE_URL}/api/v1/notifications/ws/${user.id}`;
            console.log(`[WebSocket] Connecting to ${wsUrl}`);

            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('[WebSocket] Connected successfully');
                setIsConnected(true);
                setConnectionError(null);
                reconnectAttempts.current = 0;
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('[WebSocket] Received message:', data);

                    // Handle different message types
                    switch (data.type) {
                        case 'report_completion':
                        case 'report_complete':
                            addNotification({
                                type: 'success',
                                title: data.title || 'Report Completed',
                                message: data.message || 'Your report has been generated successfully.',
                                data: data.data,
                            });
                            break;

                        case 'report_failed':
                            addNotification({
                                type: 'error',
                                title: data.title || 'Report Failed',
                                message: data.message || 'Report generation failed. Please try again.',
                                data: data.data,
                            });
                            break;

                        case 'patent_status_change':
                            addNotification({
                                type: 'info',
                                title: data.title || 'Patent Status Updated',
                                message: data.message,
                                data: data.data,
                            });
                            break;

                        case 'new_patent':
                            addNotification({
                                type: 'info',
                                title: data.title || 'New Patent Added',
                                message: data.message,
                                data: data.data,
                            });
                            break;

                        case 'test':
                            addNotification({
                                type: 'info',
                                title: data.title || 'Test Notification',
                                message: data.message,
                                data: data.data,
                            });
                            break;

                        default:
                            console.log('[WebSocket] Unknown message type:', data.type);
                            addNotification({
                                type: 'info',
                                title: data.title || 'Notification',
                                message: data.message || JSON.stringify(data),
                                data: data,
                            });
                    }
                } catch (error) {
                    console.error('[WebSocket] Error parsing message:', error);
                }
            };

            ws.onerror = (error) => {
                console.error('[WebSocket] Error:', error);
                setConnectionError('Connection error occurred');
            };

            ws.onclose = (event) => {
                console.log(`[WebSocket] Closed: ${event.code} ${event.reason}`);
                setIsConnected(false);
                wsRef.current = null;

                // Attempt reconnection if not intentionally closed
                if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS && user?.id) {
                    reconnectAttempts.current += 1;
                    console.log(`[WebSocket] Reconnecting in ${RECONNECT_DELAY}ms (attempt ${reconnectAttempts.current})`);
                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, RECONNECT_DELAY);
                } else if (reconnectAttempts.current >= MAX_RECONNECT_ATTEMPTS) {
                    setConnectionError('Max reconnection attempts reached');
                }
            };
        } catch (error) {
            console.error('[WebSocket] Connection error:', error);
            setConnectionError(error.message);
        }
    }, [user, addNotification]);

    // Disconnect WebSocket
    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }

        if (wsRef.current) {
            // Clear onclose handler to prevent reconnection
            wsRef.current.onclose = null;
            wsRef.current.close();
            wsRef.current = null;
        }

        setIsConnected(false);
        reconnectAttempts.current = MAX_RECONNECT_ATTEMPTS; // Prevent auto-reconnect
    }, []);

    // Connect when user changes
    useEffect(() => {
        if (user?.id) {
            connect();
        } else {
            disconnect();
        }

        return () => {
            disconnect();
        };
    }, [user, connect, disconnect]);

    // Send a test notification
    const sendTestNotification = useCallback(() => {
        addNotification({
            type: 'info',
            title: 'Test Notification',
            message: 'This is a test notification to verify the system is working.',
        });
    }, [addNotification]);

    const value = {
        notifications,
        unreadCount: notifications.filter((n) => !n.read).length,
        isConnected,
        connectionError,
        addNotification,
        removeNotification,
        markAsRead,
        markAllAsRead,
        clearAll,
        connect,
        disconnect,
        sendTestNotification,
    };

    return (
        <NotificationsContext.Provider value={value}>
            {children}
        </NotificationsContext.Provider>
    );
};

export const useNotifications = () => {
    const context = useContext(NotificationsContext);
    if (!context) {
        throw new Error('useNotifications must be used within a NotificationsProvider');
    }
    return context;
};

export default NotificationsContext;
