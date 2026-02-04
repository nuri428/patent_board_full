import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    CheckCircle, 
    XCircle, 
    Info, 
    AlertTriangle, 
    X 
} from 'lucide-react';

const iconMap = {
    success: CheckCircle,
    error: XCircle,
    info: Info,
    warning: AlertTriangle,
};

const colorMap = {
    success: {
        bg: 'bg-green-50',
        border: 'border-green-200',
        icon: 'text-green-500',
        progress: 'bg-green-500',
    },
    error: {
        bg: 'bg-red-50',
        border: 'border-red-200',
        icon: 'text-red-500',
        progress: 'bg-red-500',
    },
    info: {
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        icon: 'text-blue-500',
        progress: 'bg-blue-500',
    },
    warning: {
        bg: 'bg-yellow-50',
        border: 'border-yellow-200',
        icon: 'text-yellow-500',
        progress: 'bg-yellow-500',
    },
};

const Toast = ({ notification, onRemove, duration = 5000 }) => {
    const { id, type = 'info', title, message, data } = notification;
    const Icon = iconMap[type] || Info;
    const colors = colorMap[type] || colorMap.info;

    // Auto-remove after duration
    React.useEffect(() => {
        const timer = setTimeout(() => {
            onRemove(id);
        }, duration);

        return () => clearTimeout(timer);
    }, [id, onRemove, duration]);

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            className={`relative w-full max-w-sm overflow-hidden rounded-lg border shadow-lg ${colors.bg} ${colors.border}`}
        >
            {/* Progress bar */}
            <motion.div
                initial={{ width: '100%' }}
                animate={{ width: '0%' }}
                transition={{ duration: duration / 1000, ease: 'linear' }}
                className={`absolute bottom-0 left-0 h-1 ${colors.progress}`}
            />

            <div className="p-4">
                <div className="flex items-start gap-3">
                    <div className={`flex-shrink-0 ${colors.icon}`}>
                        <Icon className="h-5 w-5" />
                    </div>

                    <div className="flex-1 min-w-0">
                        {title && (
                            <h4 className="text-sm font-semibold text-gray-900">
                                {title}
                            </h4>
                        )}
                        {message && (
                            <p className="mt-1 text-sm text-gray-600">
                                {message}
                            </p>
                        )}
                        {data?.report_id && (
                            <p className="mt-1 text-xs text-gray-500">
                                Report ID: {data.report_id}
                            </p>
                        )}
                    </div>

                    <button
                        onClick={() => onRemove(id)}
                        className="flex-shrink-0 rounded-md p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                    >
                        <X className="h-4 w-4" />
                    </button>
                </div>
            </div>
        </motion.div>
    );
};

export default Toast;
