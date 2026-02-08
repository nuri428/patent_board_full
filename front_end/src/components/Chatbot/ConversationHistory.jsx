import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import ChatMessage from './ChatMessage';

function ConversationHistory({ 
    messages, 
    isLoading = false, 
    error = null,
    onRetry = null,
    retryMessage = null
}) {
    const messagesEndRef = useRef(null);
    const [autoScroll, setAutoScroll] = useState(true);

    // Scroll to bottom when messages change
    useEffect(() => {
        if (autoScroll) {
            scrollToBottom();
        }
    }, [messages, autoScroll]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const handleScroll = (e) => {
        const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
        const isNearBottom = scrollHeight - scrollTop - clientHeight < 50;
        setAutoScroll(isNearBottom);
    };

    const retryLastMessage = () => {
        if (onRetry && retryMessage) {
            onRetry(retryMessage);
        }
    };

    const formatTime = (timestampString) => {
        if (!timestampString) return '';
        const date = new Date(timestampString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const getConversationStats = () => {
        const userMessages = messages.filter(m => m.role === 'user').length;
        const assistantMessages = messages.filter(m => m.role === 'assistant').length;
        return {
            total: messages.length,
            user: userMessages,
            assistant: assistantMessages
        };
    };

    const stats = getConversationStats();

    return (
        <div className="conversation-history-container h-100 d-flex flex-column">
            {/* Header */}
            <div className="conversation-header mb-3">
                <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">
                        <i className="bi bi-chat-text me-2"></i>
                        Conversation
                    </h5>
                    <div className="conversation-stats">
                        <small className="text-muted">
                            {stats.total} messages • 
                            You: {stats.user} • 
                            AI: {stats.assistant}
                        </small>
                        {autoScroll && (
                            <button
                                className="btn btn-sm btn-outline-secondary ms-2"
                                onClick={() => setAutoScroll(false)}
                                title="Disable auto-scroll"
                            >
                                <i className="bi bi-pin"></i>
                            </button>
                        )}
                        {!autoScroll && (
                            <button
                                className="btn btn-sm btn-outline-secondary ms-2"
                                onClick={() => setAutoScroll(true)}
                                title="Enable auto-scroll"
                            >
                                <i className="bi bi-pin-angle"></i>
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Messages container */}
            <div 
                className="messages-container flex-grow-1 overflow-auto"
                onScroll={handleScroll}
            >
                {error ? (
                    <div className="error-container text-center py-5">
                        <i className="bi bi-exclamation-triangle-fill text-warning display-4"></i>
                        <h5 className="mt-3">Connection Error</h5>
                        <p className="text-muted">{error}</p>
                        {onRetry && retryMessage && (
                            <button
                                className="btn btn-primary"
                                onClick={retryLastMessage}
                            >
                                <i className="bi bi-arrow-clockwise me-2"></i>
                                Retry Last Message
                            </button>
                        )}
                    </div>
                ) : messages.length === 0 ? (
                    <div className="empty-state text-center py-5">
                        <i className="bi bi-chat-square-text display-1 text-muted"></i>
                        <h5 className="mt-3 text-muted">No messages yet</h5>
                        <p className="text-muted">
                            Start a conversation by typing a message below.
                        </p>
                    </div>
                ) : (
                    <div className="messages-list">
                        {messages.map((message, index) => (
                            <ChatMessage key={message.id || index} message={message} />
                        ))}
                        
                        {/* Loading indicator */}
                        {isLoading && (
                            <div className="chat-message assistant-message">
                                <div className="message-container">
                                    <div className="message-header">
                                        <div className="d-flex justify-content-between align-items-center">
                                            <div className="message-role">
                                                <span className="badge bg-success">
                                                    <i className="bi bi-robot me-1"></i>
                                                    Assistant
                                                </span>
                                            </div>
                                            <div className="message-timestamp">
                                                <small className="text-muted">Just now</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="message-body">
                                        <div className="message-pending">
                                            <div className="typing-indicator">
                                                <span className="dot"></span>
                                                <span className="dot"></span>
                                                <span className="dot"></span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                        
                        {/* Scroll anchor */}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Message actions */}
            <div className="message-actions mt-3">
                <div className="d-flex justify-content-between align-items-center">
                    <small className="text-muted">
                        <i className="bi bi-info-circle me-1"></i>
                        {autoScroll ? 'Auto-scroll enabled' : 'Auto-scroll disabled'}
                    </small>
                    
                    {messages.length > 0 && (
                        <button
                            className="btn btn-sm btn-outline-secondary"
                            onClick={scrollToBottom}
                            title="Scroll to bottom"
                        >
                            <i className="bi bi-arrow-down-circle me-1"></i>
                            Bottom
                        </button>
                    )}
                </div>
            </div>

            {/* Style for typing indicator */}
            <style jsx>{`
                .typing-indicator {
                    display: flex;
                    align-items: center;
                    padding: 1rem 0;
                }
                
                .typing-indicator .dot {
                    height: 8px;
                    width: 8px;
                    background-color: #6c757d;
                    border-radius: 50%;
                    display: inline-block;
                    margin: 0 2px;
                    animation: bounce 1.4s infinite ease-in-out both;
                }
                
                .typing-indicator .dot:nth-child(1) {
                    animation-delay: -0.32s;
                }
                
                .typing-indicator .dot:nth-child(2) {
                    animation-delay: -0.16s;
                }
                
                @keyframes bounce {
                    0%, 80%, 100% {
                        transform: scale(0);
                    } 40% {
                        transform: scale(1);
                    }
                }
                
                .chat-message {
                    margin-bottom: 1rem;
                    animation: fadeIn 0.3s ease-in-out;
                }
                
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .user-message {
                    margin-left: 20%;
                }
                
                .assistant-message {
                    margin-right: 20%;
                }
                
                @media (max-width: 768px) {
                    .user-message,
                    .assistant-message {
                        margin-left: 0;
                        margin-right: 0;
                    }
                }
            `}</style>
        </div>
    );
}

ConversationHistory.propTypes = {
    messages: PropTypes.array.isRequired,
    isLoading: PropTypes.bool,
    error: PropTypes.string,
    onRetry: PropTypes.func,
    retryMessage: PropTypes.string
};

export default ConversationHistory;