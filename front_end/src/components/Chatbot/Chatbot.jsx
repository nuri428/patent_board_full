import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useChatbot } from '../../context/ChatbotContext';
import { chatbotAPI } from '../../api/chatbot_modes';
import { useNavigate } from 'react-router-dom';
import SessionList from './SessionList';
import ConversationHistory from './ConversationHistory';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';

const MAX_RETRIES = 3;

function Chatbot({ userId, layout = 'split' }) {
    const navigate = useNavigate();
    const {
        currentSession,
        sessions,
        messages,
        isLoading,
        error,
        isConnected,
        isInitialized,
        authStatus,
        createSession,
        loadSession,
        sendMessage,
        setUserProperties,
        clearChat,
        refreshSessions,
        dispatch
    } = useChatbot();

    const [sidebarOpen, setSidebarOpen] = useState(layout === 'split');
    const [lastFailedMessage, setLastFailedMessage] = useState(null);

    const [isStreaming, setIsStreaming] = useState(false);
    const [streamingMessageId, setStreamingMessageId] = useState(null);
    const [abortController, setAbortController] = useState(null);
    const [pendingPatentUrls, setPendingPatentUrls] = useState([]);

    const [errorType, setErrorType] = useState(null);
    const [errorMessage, setErrorMessage] = useState(null);
    const [retryCount, setRetryCount] = useState(0);
    const [showError, setShowError] = useState(false);
    const [connectionLost, setConnectionLost] = useState(false);
    const [reconnecting, setReconnecting] = useState(false);

    useEffect(() => {
        if (userId && isInitialized) {
            refreshSessions(userId);
        }
    }, [userId, isInitialized, refreshSessions]);

    const checkTokenExpiry = () => {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                const now = Math.floor(Date.now() / 1000);
                if (payload.exp && payload.exp < now) {
                    handleTokenExpiry();
                }
            } catch (error) {
                console.error('Invalid token format:', error);
            }
        }
    };

    const handleTokenExpiry = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('userId');
        dispatch({ type: 'CLEAR_CHAT' });
        navigate('/login');
    };

    const determineErrorType = (error) => {
        if (!error) return 'network';
        const message = error.message || error.toString().toLowerCase();
        
        if (message.includes('connection') || message.includes('network') || message.includes('fetch')) {
            return 'connection';
        }
        if (message.includes('timeout') || message.includes('timed out')) {
            return 'timeout';
        }
        if (message.includes('token') || message.includes('401') || message.includes('unauthorized') || message.includes('expired')) {
            return 'token';
        }
        if (message.includes('stream') || message.includes('sse')) {
            return 'streaming';
        }
        return 'network';
    };

    const handleError = (error) => {
        const type = determineErrorType(error);
        
        if (type === 'token') {
            handleTokenExpiry();
            return;
        }

        setErrorType(type);
        setErrorMessage(error.message || 'An unexpected error occurred');
        setShowError(true);
        setIsStreaming(false);
        setStreamingMessageId(null);

        dispatch({ type: 'SET_ERROR', payload: error.message });
        dispatch({ type: 'SET_LOADING', payload: false });
        setAbortController(null);
    };

    const handleRetry = async () => {
        if (retryCount >= MAX_RETRIES) {
            setErrorMessage('Maximum retries reached. Please refresh the page.');
            return;
        }

        const backoff = Math.pow(2, retryCount) * 1000;
        setRetryCount(prev => prev + 1);
        setReconnecting(true);
        
        await new Promise(resolve => setTimeout(resolve, backoff));
        
        try {
            if (lastFailedMessage) {
                setReconnecting(false);
                handleSendMessage(lastFailedMessage);
                setShowError(false);
            }
        } catch (error) {
            setReconnecting(false);
            handleError(error);
        }
    };

    const handleConnectionLost = () => {
        setConnectionLost(true);
        setReconnecting(true);
        
        setTimeout(async () => {
            setReconnecting(false);
            if (lastFailedMessage) {
                handleRetry();
            }
        }, 2000);
    };

    const handleConnectionRestored = () => {
        setConnectionLost(false);
        setShowError(false);
    };

    const handleSelectSession = async (sessionId) => {
        try {
            await loadSession(sessionId);
            setSidebarOpen(false);
        } catch (error) {
            console.error('Failed to load session:', error);
        }
    };

    const handleCreateSession = async (userId, title = '') => {
        try {
            const newSession = await createSession(userId);
            return newSession;
        } catch (error) {
            console.error('Failed to create session:', error);
            throw error;
        }
    };

    const handleStreamingMessage = (messageContent) => {
        if (!currentSession) {
            return handleCreateSession(userId, messageContent);
        }

        if (!authStatus.isAuthenticated) {
            return handleSendMessageFallback(messageContent);
        }

        setIsStreaming(true);
        setPendingPatentUrls([]);

        const controller = chatbotAPI.streamChatMessage(
            messageContent,
            currentSession.id,
            {
                onMessage: (data) => {
                    if (streamingMessageId) {
                        dispatch({
                            type: 'ADD_MESSAGE',
                            payload: {
                                id: streamingMessageId,
                                content: data.partial,
                                role: 'assistant',
                                timestamp: new Date().toISOString(),
                                pending: true
                            }
                        });
                    }
                },

                onMetadata: (data) => {
                    setPendingPatentUrls(data.patentUrls || []);
                },

                onComplete: (data) => {
                    setIsStreaming(false);
                    setStreamingMessageId(null);
                    setRetryCount(0);

                    dispatch({
                        type: 'ADD_MESSAGE',
                        payload: {
                            id: Date.now().toString(),
                            content: data.response,
                            role: 'assistant',
                            timestamp: new Date().toISOString(),
                            pending: false,
                            patent_urls: pendingPatentUrls
                        }
                    });

                    dispatch({ type: 'SET_LOADING', payload: false });
                    setAbortController(null);
                },

                onError: (error) => {
                    if (error.message && error.message.includes('stream')) {
                        handleConnectionLost();
                    }
                    handleError(error);
                }
            }
        );

        setAbortController(controller);
    };

    const handleSendMessageFallback = async (messageContent) => {
        if (!currentSession) {
            try {
                const newSession = await handleCreateSession(userId);
                setLastFailedMessage(messageContent);
                return await sendMessage(messageContent, newSession.id);
            } catch (error) {
                console.error('Failed to create session and send message:', error);
                throw error;
            }
        }

        setLastFailedMessage(messageContent);
        return await sendMessage(messageContent, currentSession.id);
    };

    const handleSendMessage = async (messageContent) => {
        checkTokenExpiry();

        const userMessage = {
            id: Date.now().toString(),
            content: messageContent,
            role: 'user',
            timestamp: new Date().toISOString(),
            pending: false
        };

        dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
        dispatch({ type: 'SET_LOADING', payload: true });

        if (!currentSession) {
            try {
                const newSession = await handleCreateSession(userId);
                setLastFailedMessage(messageContent);

                const messageId = Date.now().toString() + '_assistant';
                setStreamingMessageId(messageId);
                return handleStreamingMessage(messageContent);
            } catch (error) {
                console.error('Failed to create session and send message:', error);
                dispatch({ type: 'SET_LOADING', payload: false });
                throw error;
            }
        }

        setLastFailedMessage(messageContent);

        const messageId = Date.now().toString() + '_assistant';
        setStreamingMessageId(messageId);

        return handleStreamingMessage(messageContent);
    };

    const handleAbortStream = () => {
        if (abortController) {
            abortController.abort();
            setIsStreaming(false);
            setStreamingMessageId(null);
            dispatch({ type: 'SET_LOADING', payload: false });
            setAbortController(null);
        }
    };

    const handleRetryMessage = async () => {
        if (lastFailedMessage && currentSession) {
            try {
                setRetryCount(0);
                if (authStatus.isAuthenticated) {
                    const messageId = Date.now().toString() + '_assistant';
                    setStreamingMessageId(messageId);
                    return handleStreamingMessage(lastFailedMessage);
                } else {
                    await sendMessage(lastFailedMessage, currentSession.id);
                }
                setLastFailedMessage(null);
            } catch (error) {
                console.error('Failed to retry message:', error);
            }
        }
    };

    const renderErrorBanner = () => {
        if (!showError || !errorMessage) return null;

        const getErrorConfig = () => {
            switch (errorType) {
                case 'connection':
                    return {
                        icon: 'bi-wifi-off',
                        title: 'Connection Error',
                        message: errorMessage || 'Unable to connect to the chat service. Please check your internet connection.',
                        buttons: [
                            { text: 'Retry', onClick: handleRetry, variant: 'primary', icon: 'bi-arrow-clockwise' },
                            { text: 'Refresh', onClick: () => window.location.reload(), variant: 'outline-secondary', icon: 'bi-arrow-clockwise' }
                        ]
                    };
                case 'timeout':
                    return {
                        icon: 'bi-hourglass-split',
                        title: 'Request Timeout',
                        message: errorMessage || 'The request took too long to complete.',
                        buttons: [
                            { text: 'Retry', onClick: handleRetry, variant: 'primary', icon: 'bi-arrow-clockwise' }
                        ]
                    };
                case 'token':
                    return {
                        icon: 'bi-key',
                        title: 'Session Expired',
                        message: errorMessage || 'Your session has expired. Please log in again.',
                        buttons: [
                            { text: 'Re-login', onClick: () => navigate('/login'), variant: 'primary', icon: 'bi-box-arrow-right' }
                        ]
                    };
                case 'streaming':
                    return {
                        icon: 'bi-cloud-slash',
                        title: 'Connection Lost',
                        message: errorMessage || 'Lost connection to the server. Attempting to reconnect...',
                        buttons: reconnecting ? [] : [
                            { text: 'Reconnect', onClick: handleRetry, variant: 'primary', icon: 'bi-arrow-clockwise' }
                        ]
                    };
                default:
                    return {
                        icon: 'bi-exclamation-triangle',
                        title: 'Error',
                        message: errorMessage || 'An unexpected error occurred.',
                        buttons: [
                            { text: 'Retry', onClick: handleRetry, variant: 'primary', icon: 'bi-arrow-clockwise' }
                        ]
                    };
            }
        };

        const config = getErrorConfig();

        return (
            <div className="error-banner bg-rose-50 border border-rose-200 p-4 mb-4 rounded-lg shadow-sm">
                <div className="d-flex align-items-start gap-3">
                    <div className="text-rose-600 flex-shrink-0">
                        <i className={`bi ${config.icon} fs-2`}></i>
                    </div>
                    <div className="flex-grow-1">
                        <h5 className="fw-bold text-rose-900 mb-1">{config.title}</h5>
                        <p className="text-rose-800 small mb-3">{config.message}</p>
                        <div className="d-flex gap-2">
                            {config.buttons.map((btn, idx) => (
                                <button
                                    key={idx}
                                    onClick={btn.onClick}
                                    disabled={retryCount >= MAX_RETRIES && btn.text === 'Retry'}
                                    className={`btn btn-sm btn-${btn.variant}`}
                                >
                                    <i className={`bi ${btn.icon} me-1`}></i>
                                    {btn.text}
                                    {reconnecting && btn.text === 'Retry' && '...'}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderLoadingOverlay = () => {
        if (!isLoading && !isStreaming) return null;

        return (
            <div className="loading-overlay position-fixed top-0 start-0 w-100 h-100 bg-white bg-opacity-50 d-flex align-items-center justify-content-center" style={{ zIndex: 9999 }}>
                <div className="text-center">
                    <div className="spinner-border text-primary mb-3" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="text-secondary">
                        {isStreaming ? 'AI is processing your request...' : 'Processing...'}
                    </p>
                </div>
            </div>
        );
    };

    const renderConnectionIndicator = () => {
        if (connectionLost) {
            return (
                <div className="connection-lost-indicator bg-warning bg-opacity-10 border border-warning text-warning px-3 py-2 mb-3 rounded shadow-sm">
                    <div className="d-flex align-items-center gap-2">
                        <i className="bi bi-wifi-off fs-5"></i>
                        <span className="small">
                            {reconnecting ? 'Reconnecting...' : 'Connection lost. Trying to reconnect...'}
                        </span>
                    </div>
                </div>
            );
        }
        return null;
    };

    const renderLayout = () => {
        if (layout === 'full') {
            return (
                <div className="chatbot-full-layout h-100">
                    <div className="chatbot-header mb-3">
                        <div className="d-flex justify-content-between align-items-center">
                            <div className="chatbot-title">
                                <h4 className="mb-0">
                                    <i className="bi bi-robot me-2"></i>
                                    Patent Analysis Assistant
                                </h4>
                                <small className="text-muted">
                                    {isConnected ? (
                                        <>
                                            <i className="bi bi-circle-fill text-success me-1"></i>
                                            Connected to LangGraph service
                                        </>
                                    ) : (
                                        <>
                                            <i className="bi bi-circle-fill text-danger me-1"></i>
                                            Disconnected
                                        </>
                                    )}
                                </small>
                            </div>
                            <div className="chatbot-actions">
                                {currentSession && (
                                    <button
                                        className="btn btn-sm btn-outline-danger me-2"
                                        onClick={clearChat}
                                        title="Clear conversation"
                                    >
                                        <i className="bi bi-trash me-1"></i>
                                        Clear
                                    </button>
                                )}
                                <button
                                    className="btn btn-sm btn-outline-primary"
                                    onClick={() => setSidebarOpen(!sidebarOpen)}
                                    title={sidebarOpen ? 'Hide sessions' : 'Show sessions'}
                                >
                                    <i className={`bi ${sidebarOpen ? 'bi-chevron-left' : 'bi-chevron-right'}`}></i>
                                </button>
                            </div>
                        </div>
                    </div>

                    {renderErrorBanner()}
                    {renderConnectionIndicator()}

                    <ConversationHistory
                        messages={messages}
                        isLoading={isLoading}
                        error={error}
                        onRetry={handleRetryMessage}
                        retryMessage={lastFailedMessage}
                        showSkeleton={isLoading && messages.length === 0}
                    />

                        <div className="input-area">
                            {(isStreaming || isLoading) && (
                                <div className="typing-indicator-container text-muted mb-3 flex items-center gap-3">
                                    <TypingIndicator isStreaming={isStreaming} />
                                    {isStreaming && (
                                        <button
                                            className="btn btn-sm btn-outline-danger"
                                            onClick={handleAbortStream}
                                            title="Stop generating"
                                        >
                                            <i className="bi bi-stop-circle"></i> Stop
                                        </button>
                                    )}
                                </div>
                            )}
                        <ChatInput
                            onSendMessage={handleSendMessage}
                            disabled={!isConnected || !isInitialized || isLoading || isStreaming || reconnecting}
                            placeholder={
                                !isConnected ? 'Chat service unavailable' :
                                    !isInitialized ? 'Initializing...' :
                                        isStreaming ? 'Typing...' :
                                            isLoading ? 'Processing...' :
                                                reconnecting ? 'Reconnecting...' :
                                                    'Ask about patents, analysis, or reports...'
                            }
                        />
                    </div>

                    {renderLoadingOverlay()}
                </div>
            );
        }

        return (
            <div className="chatbot-split-layout h-100">
                <div className={`row h-100 ${sidebarOpen ? '' : 'sidebar-closed'}`}>
                    {sidebarOpen && (
                        <div className="col-md-4 col-lg-3 sidebar">
                            <SessionList
                                sessions={sessions}
                                currentSessionId={currentSession?.id}
                                onSelectSession={handleSelectSession}
                                onCreateSession={handleCreateSession}
                                onRefreshSessions={() => refreshSessions(userId)}
                                userId={userId}
                                isLoading={isLoading}
                            />
                        </div>
                    )}

                    <div className={`col-md-8 col-lg-9 main-chat ${sidebarOpen ? '' : 'col-12'}`}>
                        <div className="chatbot-header mb-3">
                            <div className="d-flex justify-content-between align-items-center">
                                <div className="chatbot-title">
                                    <h4 className="mb-0">
                                        <i className="bi bi-robot me-2"></i>
                                        Patent Analysis Assistant
                                    </h4>
                                    <small className="text-muted">
                                        {isConnected ? (
                                            <>
                                                <i className="bi bi-circle-fill text-success me-1"></i>
                                                Connected to LangGraph service
                                            </>
                                        ) : (
                                            <>
                                                <i className="bi bi-circle-fill text-danger me-1"></i>
                                                Disconnected
                                            </>
                                        )}
                                        {currentSession && (
                                            <span className="ms-2">
                                                Current: {currentSession.title || `Session ${currentSession.id}`}
                                            </span>
                                        )}
                                    </small>
                                </div>
                                <div className="chatbot-actions">
                                    {currentSession && (
                                        <button
                                            className="btn btn-sm btn-outline-danger me-2"
                                            onClick={clearChat}
                                            title="Clear conversation"
                                        >
                                            <i className="bi bi-trash me-1"></i>
                                            Clear
                                        </button>
                                    )}
                                    <button
                                        className="btn btn-sm btn-outline-primary"
                                        onClick={() => setSidebarOpen(!sidebarOpen)}
                                        title={sidebarOpen ? 'Hide sessions' : 'Show sessions'}
                                    >
                                        <i className={`bi ${sidebarOpen ? 'bi-chevron-right' : 'bi-chevron-left'}`}></i>
                                    </button>
                                </div>
                            </div>
                        </div>

                        {renderErrorBanner()}
                        {renderConnectionIndicator()}

                        <ConversationHistory
                            messages={messages}
                            isLoading={isLoading}
                            error={error}
                            onRetry={handleRetryMessage}
                            retryMessage={lastFailedMessage}
                            showSkeleton={isLoading && messages.length === 0}
                        />

                        <div className="input-area">
                            {(isStreaming || isLoading) && (
                                <div className="typing-indicator-container text-muted mb-3 flex items-center gap-3">
                                    <TypingIndicator isStreaming={isStreaming} />
                                    {isStreaming && (
                                        <button
                                            className="btn btn-sm btn-outline-danger"
                                            onClick={handleAbortStream}
                                            title="Stop generating"
                                        >
                                            <i className="bi bi-stop-circle"></i> Stop
                                        </button>
                                    )}
                                </div>
                            )}
                            <ChatInput
                                onSendMessage={handleSendMessage}
                                disabled={!isConnected || !isInitialized || isLoading || isStreaming || reconnecting}
                                placeholder={
                                    !isConnected ? 'Chat service unavailable' :
                                        !isInitialized ? 'Initializing...' :
                                            isStreaming ? 'Typing...' :
                                                isLoading ? 'Processing...' :
                                                    reconnecting ? 'Reconnecting...' :
                                                        'Ask about patents, analysis, or reports...'
                                }
                            />
                        </div>

                        {renderLoadingOverlay()}
                    </div>
                </div>
            </div>
        );
    };

    if (!isInitialized) {
        return (
            <div className="chatbot-loading h-100 d-flex flex-column justify-content-center align-items-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                </div>
                <p className="text-muted mt-3">Initializing chat service...</p>
            </div>
        );
    }

    return (
        <div className={`chatbot-container ${layout} h-100`}>
            {renderLayout()}
        </div>
    );
}

Chatbot.propTypes = {
    userId: PropTypes.string.isRequired,
    layout: PropTypes.oneOf(['split', 'full'])
};

export default Chatbot;
