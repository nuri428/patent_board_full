import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';

function TypingIndicator({ isStreaming = false }) {
    if (!isStreaming) return null;

    return (
        <div className="typing-indicator-wrapper">
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ duration: 0.2, ease: "easeInOut" }}
                aria-live="polite"
                aria-label="AI is typing"
                role="status"
            >
                <div className="typing-dots flex items-center gap-1.5">
                    <motion.span
                        animate={{ scale: [1, 0.8, 1] }}
                        transition={{
                            repeat: Infinity,
                            duration: 0.8,
                            delay: 0,
                            ease: "easeInOut"
                        }}
                        className="typing-dot w-2 h-2 bg-indigo-600 rounded-full"
                        aria-hidden="true"
                    />
                    <motion.span
                        animate={{ scale: [1, 0.8, 1] }}
                        transition={{
                            repeat: Infinity,
                            duration: 0.8,
                            delay: 0.2,
                            ease: "easeInOut"
                        }}
                        className="typing-dot w-2 h-2 bg-indigo-600 rounded-full"
                        aria-hidden="true"
                    />
                    <motion.span
                        animate={{ scale: [1, 0.8, 1] }}
                        transition={{
                            repeat: Infinity,
                            duration: 0.8,
                            delay: 0.4,
                            ease: "easeInOut"
                        }}
                        className="typing-dot w-2 h-2 bg-indigo-600 rounded-full"
                        aria-hidden="true"
                    />
                </div>
            </motion.div>
        </div>
    );
}

TypingIndicator.propTypes = {
    isStreaming: PropTypes.bool
};

export default TypingIndicator;
