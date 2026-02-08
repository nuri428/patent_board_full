import React, { useState, useRef, useEffect } from 'react';
import { Bell, Check, Trash2, X, Clock, ExternalLink } from 'lucide-react';
import { useNotifications } from '../../context/NotificationsContext';

const NotificationCenter = () => {
    const {
        notifications,
        unreadCount,
        markAsRead,
        markAllAsRead,
        removeNotification,
        clearAll
    } = useNotifications();
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    // Close on click outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const formatTime = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="relative" ref={dropdownRef}>
            {/* Bell Icon & Badge */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="relative p-2 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-all"
            >
                <Bell className="w-6 h-6" />
                {unreadCount > 0 && (
                    <span className="absolute top-1.5 right-1.5 flex h-4 w-4">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500 text-[10px] text-white items-center justify-center font-bold">
                            {unreadCount > 9 ? '9+' : unreadCount}
                        </span>
                    </span>
                )}
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                        <h3 className="font-bold text-gray-800">Notifications</h3>
                        <div className="flex gap-2">
                            <button
                                onClick={markAllAsRead}
                                className="text-xs text-purple-600 hover:text-purple-700 font-medium"
                            >
                                Mark all read
                            </button>
                            <button
                                onClick={clearAll}
                                className="text-gray-400 hover:text-red-500 transition-colors"
                                title="Clear all"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    <div className="max-h-96 overflow-y-auto">
                        {notifications.length === 0 ? (
                            <div className="p-8 text-center text-gray-400">
                                <Bell className="w-12 h-12 mx-auto mb-3 opacity-20" />
                                <p className="text-sm">No new notifications</p>
                            </div>
                        ) : (
                            <div className="divide-y divide-gray-50">
                                {notifications.map((n) => (
                                    <div
                                        key={n.id}
                                        className={`p-4 hover:bg-gray-50 transition-colors group relative ${!n.read ? 'bg-purple-50/30' : ''}`}
                                    >
                                        <div className="flex gap-3">
                                            <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${!n.read ? 'bg-purple-500' : 'bg-transparent'}`} />
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-start justify-between gap-2">
                                                    <p className={`text-sm font-semibold truncate ${!n.read ? 'text-gray-900' : 'text-gray-600'}`}>
                                                        {n.title}
                                                    </p>
                                                    <span className="text-[10px] text-gray-400 whitespace-nowrap flex items-center gap-1">
                                                        <Clock className="w-3 h-3" />
                                                        {formatTime(n.timestamp)}
                                                    </span>
                                                </div>
                                                <p className="text-xs text-gray-500 mt-1 line-clamp-2 leading-relaxed">
                                                    {n.message}
                                                </p>
                                                {n.data?.report_id && (
                                                    <button className="mt-2 text-[10px] flex items-center gap-1 text-purple-600 font-bold hover:underline">
                                                        <ExternalLink className="w-3 h-3" />
                                                        View Report
                                                    </button>
                                                )}
                                            </div>
                                            <div className="flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button
                                                    onClick={() => removeNotification(n.id)}
                                                    className="p-1 text-gray-400 hover:text-red-500"
                                                >
                                                    <X className="w-3.5 h-3.5" />
                                                </button>
                                                {!n.read && (
                                                    <button
                                                        onClick={() => markAsRead(n.id)}
                                                        className="p-1 text-gray-400 hover:text-green-500"
                                                    >
                                                        <Check className="w-3.5 h-3.5" />
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="p-3 border-t border-gray-100 text-center bg-gray-50/30">
                        <button className="text-xs font-bold text-gray-500 hover:text-purple-600 transition-colors">
                            View all history
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default NotificationCenter;
