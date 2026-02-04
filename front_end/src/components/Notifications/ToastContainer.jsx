import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { useNotifications } from '../../context/NotificationsContext';
import Toast from './Toast';

const ToastContainer = ({ position = 'top-right', duration = 5000 }) => {
    const { notifications, removeNotification } = useNotifications();

    // Filter out read notifications for display
    const activeNotifications = notifications.filter((n) => !n.read);

    // Position classes
    const positionClasses = {
        'top-right': 'top-4 right-4',
        'top-left': 'top-4 left-4',
        'top-center': 'top-4 left-1/2 -translate-x-1/2',
        'bottom-right': 'bottom-4 right-4',
        'bottom-left': 'bottom-4 left-4',
        'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
    };

    if (activeNotifications.length === 0) {
        return null;
    }

    return (
        <div
            className={`fixed z-50 flex flex-col gap-2 ${positionClasses[position]} pointer-events-none`}
            style={{ maxWidth: '400px' }}
        >
            <AnimatePresence mode="popLayout">
                {activeNotifications.map((notification) => (
                    <div key={notification.id} className="pointer-events-auto">
                        <Toast
                            notification={notification}
                            onRemove={removeNotification}
                            duration={duration}
                        />
                    </div>
                ))}
            </AnimatePresence>
        </div>
    );
};

export default ToastContainer;
