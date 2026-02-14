import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useChatbot } from '../../context/ChatbotContext';
import { chatbotAPI } from '../../api/chatbot_modes';
import SessionList from './SessionList';
import ConversationHistory from './ConversationHistory';
import ChatInput from './ChatInput';

function Chatbot({ userId, layout = 'split' }) {
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

    // Streaming state
    const [isStreaming, setIsStreaming] = useState(false);
    const [streamingMessageId, setStreamingMessageId] = useState(null);
    const [abortController, setAbortController] = useState(null);
    const [pendingPatentUrls, setPendingPatentUrls] = useState([]);

    useEffect(() => {
        if (userId && isInitialized) {
            refreshSessions(userId);
        }
    }, [userId, isInitialized, refreshSessions]);

    const handleSelectSession = async (sessionId) => {
        try {
            await loadSession(sessionId);
            setSidebarOpen(false); // Close sidebar on mobile after selection
        } catch (error) {
            console.error('Failed to load session:', error);
        }
    };

    const handleCreateSession = async (userId, title = '') => {
        try {
            const newSession = await createSession(userId);
            // The context will automatically set this as current session
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
                    setIsStreaming(false);
                    setStreamingMessageId(null);

                    dispatch({
                        type: 'SET_ERROR',
                        payload: error.message
                    });
                    dispatch({ type: 'SET_LOADING', payload: false });
                    setAbortController(null);
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
        // Add user message to messages
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

    const handleSendMessage = async (messageContent) => {
        if (!currentSession) {
            // Create a new session if none exists
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

    const handleRetryMessage = async () => {
        if (lastFailedMessage && currentSession) {
            try {
                await sendMessage(lastFailedMessage, currentSession.id);
                setLastFailedMessage(null);
            } catch (error) {
                console.error('Failed to retry message:', error);
            }
        }
    };

    const renderLayout = () => {
        if (layout === 'full') {
            return (
                <div className="chatbot-full-layout h-100">
                    {/* Header */}
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

                    {/* Conversation */}
                    <ConversationHistory
                        messages={messages}
                        isLoading={isLoading}
                        error={error}
                        onRetry={handleRetryMessage}
                        retryMessage={lastFailedMessage}
                    />

                    {/* Input */}
                    <div className="input-area">
                        {(isStreaming || isLoading) && (
                            <div className="typing-indicator text-muted mb-3">
                                <span>AI is typing</span>
                                <div className="typing-dots ms-2 d-inline-block">
                                    <span>.</span>
                                    <span>.</span>
                                    <span>.</span>
                                </div>
                                {isStreaming && (
                                    <button
                                        className="btn btn-sm btn-outline-danger ms-3"
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
                            disabled={!isConnected || !isInitialized || isLoading || isStreaming}
                            placeholder={
                                !isConnected ? 'Chat service unavailable' :
                                    !isInitialized ? 'Initializing...' :
                                        isStreaming ? 'Typing...' :
                                            isLoading ? 'Processing...' :
                                                'Ask about patents, analysis, or reports...'
                            }
                        />
                    </div>
                </div>
            );
        }

        // Split layout (default)
        return (
            <div className="chatbot-split-layout h-100">
                <div className={`row h-100 ${sidebarOpen ? '' : 'sidebar-closed'}`}>
                    {/* Sidebar - Sessions list */}
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

                    {/* Main chat area */}
                    <div className={`col-md-8 col-lg-9 main-chat ${sidebarOpen ? '' : 'col-12'}`}>
                        {/* Header */}
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

                        {/* Conversation */}
                        <ConversationHistory
                            messages={messages}
                            isLoading={isLoading}
                            error={error}
                            onRetry={handleRetryMessage}
                            retryMessage={lastFailedMessage}
                        />

                        {/* Input */}
                        <div className="input-area">
                            {(isStreaming || isLoading) && (
                                <div className="typing-indicator text-muted mb-3">
                                    <span>AI is typing</span>
                                    <div className="typing-dots ms-2 d-inline-block">
                                        <span>.</span>
                                        <span>.</span>
                                        <span>.</span>
                                    </div>
                                    {isStreaming && (
                                        <button
                                            className="btn btn-sm btn-outline-danger ms-3"
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
                                disabled={!isConnected || !isInitialized || isLoading || isStreaming}
                                placeholder={
                                    !isConnected ? 'Chat service unavailable' :
                                        !isInitialized ? 'Initializing...' :
                                            isStreaming ? 'Typing...' :
                                                isLoading ? 'Processing...' :
                                                    'Ask about patents, analysis, or reports...'
                                }
                            />
                        </div>
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