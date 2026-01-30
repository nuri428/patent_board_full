import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

function ChatInput({ onSendMessage, disabled = false, placeholder = 'Type your message...' }) {
    const [message, setMessage] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const inputRef = useRef(null);

    // Auto-focus input when component mounts or when not disabled
    useEffect(() => {
        if (inputRef.current && !disabled) {
            inputRef.current.focus();
        }
    }, [disabled]);

    const handleInputChange = (e) => {
        setMessage(e.target.value);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleSend = async () => {
        if (!message.trim() || disabled) return;

        const messageToSend = message.trim();
        setMessage('');
        setIsTyping(true);

        try {
            await onSendMessage(messageToSend);
        } catch (error) {
            console.error('Failed to send message:', error);
            // The parent component will handle the error display
        } finally {
            setIsTyping(false);
        }
    };

    const handleClear = () => {
        setMessage('');
    };

    const isSendDisabled = !message.trim() || disabled || isTyping;

    return (
        <div className="chat-input-container">
            <div className="input-group">
                <input
                    ref={inputRef}
                    type="text"
                    className="form-control"
                    placeholder={placeholder}
                    value={message}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    disabled={disabled || isTyping}
                    aria-label="Chat message input"
                />
                
                <div className="input-group-append">
                    <button
                        className="btn btn-primary"
                        type="button"
                        onClick={handleSend}
                        disabled={isSendDisabled}
                        title="Send message (Enter)"
                    >
                        <i className={`bi ${isTyping ? 'bi-hourglass-split' : 'bi-send'}`}></i>
                        <span className="ms-1 d-none d-sm-inline">
                            {isTyping ? 'Sending...' : 'Send'}
                        </span>
                    </button>
                    
                    {message && (
                        <button
                            className="btn btn-outline-secondary"
                            type="button"
                            onClick={handleClear}
                            disabled={disabled || isTyping}
                            title="Clear input"
                        >
                            <i className="bi bi-x-lg"></i>
                        </button>
                    )}
                </div>
            </div>
            
            {/* Input hints */}
            <div className="input-hints mt-2">
                <small className="text-muted">
                    <i className="bi bi-keyboard me-1"></i>
                    Press Enter to send, Shift+Enter for new line
                </small>
            </div>
            
            {/* Quick actions */}
            <div className="quick-actions mt-3">
                <div className="d-flex gap-2 flex-wrap">
                    <button
                        className="btn btn-sm btn-outline-primary"
                        onClick={() => onSendMessage('Hello! Can you help me with patent analysis?')}
                        disabled={disabled || isTyping}
                        title="Send greeting message"
                    >
                        <i className="bi bi-chat-dots me-1"></i>
                        Quick Start
                    </button>
                    
                    <button
                        className="btn btn-sm btn-outline-info"
                        onClick={() => onSendMessage('What patents are related to artificial intelligence in healthcare?')}
                        disabled={disabled || isTyping}
                        title="Ask about AI in healthcare patents"
                    >
                        <i className="bi bi-lightbulb me-1"></i>
                        AI + Healthcare
                    </button>
                    
                    <button
                        className="btn btn-sm btn-outline-warning"
                        onClick={() => onSendMessage('Analyze the competitive landscape for machine learning patents')}
                        disabled={disabled || isTyping}
                        title="Request competitive analysis"
                    >
                        <i className="bi bi-graph-up me-1"></i>
                        Market Analysis
                    </button>
                </div>
            </div>
        </div>
    );
}

ChatInput.propTypes = {
    onSendMessage: PropTypes.func.isRequired,
    disabled: PropTypes.bool,
    placeholder: PropTypes.string
};

export default ChatInput;