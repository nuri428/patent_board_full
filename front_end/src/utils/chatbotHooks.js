import { useState, useEffect, useCallback } from 'react';
import { useChatbot } from '../context/ChatbotContext';

// Hook for managing chatbot input state
export function useChatInput() {
    const [inputValue, setInputValue] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleInputChange = useCallback((e) => {
        setInputValue(e.target.value);
    }, []);

    const handleKeyDown = useCallback((e, handleSubmit) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    }, []);

    const clearInput = useCallback(() => {
        setInputValue('');
    }, []);

    const setInput = useCallback((value) => {
        setInputValue(value);
    }, []);

    return {
        inputValue,
        setInputValue,
        isSubmitting,
        setIsSubmitting,
        handleInputChange,
        handleKeyDown,
        clearInput,
        setInput
    };
}

// Hook for managing chat sessions
export function useChatSessions(userId) {
    const { 
        sessions, 
        currentSession, 
        createSession, 
        loadSession, 
        refreshSessions,
        isLoading 
    } = useChatbot();

    const [isCreating, setIsCreating] = useState(false);

    const createNewSession = useCallback(async (title = '') => {
        setIsCreating(true);
        try {
            const newSession = await createSession(userId, title);
            return newSession;
        } catch (error) {
            console.error('Failed to create session:', error);
            throw error;
        } finally {
            setIsCreating(false);
        }
    }, [createSession, userId]);

    const switchToSession = useCallback(async (sessionId) => {
        try {
            await loadSession(sessionId);
        } catch (error) {
            console.error('Failed to load session:', error);
            throw error;
        }
    }, [loadSession]);

    const refreshUserSessions = useCallback(async () => {
        try {
            await refreshSessions(userId);
        } catch (error) {
            console.error('Failed to refresh sessions:', error);
            throw error;
        }
    }, [refreshSessions, userId]);

    return {
        sessions,
        currentSession,
        isLoading,
        isCreating,
        createNewSession,
        switchToSession,
        refreshUserSessions
    };
}

// Hook for managing conversation state
export function useConversation(sessionId) {
    const { 
        messages, 
        sendMessage, 
        isLoading: isSending,
        clearChat,
        error 
    } = useChatbot();

    const [isRetrying, setIsRetrying] = useState(false);
    const [lastMessage, setLastMessage] = useState(null);

    const sendMessageToSession = useCallback(async (content) => {
        if (!sessionId) {
            throw new Error('No active session');
        }

        setLastMessage(content);
        setIsRetrying(false);
        
        try {
            const response = await sendMessage(content, sessionId);
            return response;
        } catch (error) {
            console.error('Failed to send message:', error);
            throw error;
        }
    }, [sendMessage, sessionId]);

    const retryLastMessage = useCallback(async () => {
        if (!lastMessage || !sessionId) return;
        
        setIsRetrying(true);
        try {
            const response = await sendMessage(lastMessage, sessionId);
            setLastMessage(null);
            return response;
        } catch (error) {
            console.error('Failed to retry message:', error);
            throw error;
        } finally {
            setIsRetrying(false);
        }
    }, [sendMessage, lastMessage, sessionId]);

    const clearCurrentConversation = useCallback(() => {
        clearChat();
        setLastMessage(null);
    }, [clearChat]);

    const getConversationStats = useCallback(() => {
        const userMessages = messages.filter(m => m.role === 'user').length;
        const assistantMessages = messages.filter(m => m.role === 'assistant').length;
        return {
            total: messages.length,
            user: userMessages,
            assistant: assistantMessages,
            hasMessages: messages.length > 0
        };
    }, [messages]);

    return {
        messages,
        isSending,
        isRetrying,
        error,
        lastMessage,
        sendMessageToSession,
        retryLastMessage,
        clearCurrentConversation,
        getConversationStats
    };
}

// Hook for chatbot connection status
export function useChatbotConnection() {
    const { isConnected, isInitialized, error } = useChatbot();

    const [connectionStatus, setConnectionStatus] = useState('connecting');

    useEffect(() => {
        if (!isInitialized) {
            setConnectionStatus('initializing');
        } else if (isConnected) {
            setConnectionStatus('connected');
        } else {
            setConnectionStatus('disconnected');
        }
    }, [isConnected, isInitialized, error]);

    const getStatusColor = useCallback(() => {
        switch (connectionStatus) {
            case 'connected':
                return 'success';
            case 'disconnected':
                return 'danger';
            case 'initializing':
            case 'connecting':
                return 'warning';
            default:
                return 'secondary';
        }
    }, [connectionStatus]);

    const getStatusText = useCallback(() => {
        switch (connectionStatus) {
            case 'connected':
                return 'Connected';
            case 'disconnected':
                return 'Disconnected';
            case 'initializing':
                return 'Initializing...';
            case 'connecting':
                return 'Connecting...';
            default:
                return 'Unknown';
        }
    }, [connectionStatus]);

    return {
        connectionStatus,
        isConnected,
        isInitialized,
        error,
        getStatusColor,
        getStatusText
    };
}

// Hook for chatbot shortcuts and quick actions
export function useChatShortcuts() {
    const { sendMessage } = useChatbot();

    const quickActions = [
        {
            id: 'greeting',
            label: 'Quick Start',
            icon: 'bi-chat-dots',
            message: 'Hello! Can you help me with patent analysis?',
            description: 'Start with a greeting'
        },
        {
            id: 'ai_healthcare',
            label: 'AI + Healthcare',
            icon: 'bi-lightbulb',
            message: 'What patents are related to artificial intelligence in healthcare?',
            description: 'Ask about AI in healthcare patents'
        },
        {
            id: 'market_analysis',
            label: 'Market Analysis',
            icon: 'bi-graph-up',
            message: 'Analyze the competitive landscape for machine learning patents',
            description: 'Request competitive analysis'
        },
        {
            id: 'patent_search',
            label: 'Patent Search',
            icon: 'bi-search',
            message: 'Search for patents related to renewable energy technology',
            description: 'General patent search'
        }
    ];

    const executeQuickAction = useCallback(async (actionId, sessionId) => {
        const action = quickActions.find(a => a.id === actionId);
        if (!action) return;

        try {
            await sendMessage(action.message, sessionId);
        } catch (error) {
            console.error('Failed to execute quick action:', error);
            throw error;
        }
    }, [sendMessage, quickActions]);

    return {
        quickActions,
        executeQuickAction
    };
}

// Hook for debugging and development
export function useChatbotDebug() {
    const { 
        currentSession, 
        sessions, 
        messages, 
        isConnected, 
        isInitialized,
        error 
    } = useChatbot();

    const [debugInfo, setDebugInfo] = useState({});

    const generateDebugInfo = useCallback(() => {
        const stats = {
            sessions: {
                count: sessions.length,
                current: currentSession?.id || null,
                oldest: sessions.length > 0 ? sessions[sessions.length - 1]?.created_at : null,
                newest: sessions.length > 0 ? sessions[0]?.created_at : null
            },
            messages: {
                count: messages.length,
                user: messages.filter(m => m.role === 'user').length,
                assistant: messages.filter(m => m.role === 'assistant').length,
                errors: messages.filter(m => m.error).length
            },
            connection: {
                isConnected,
                isInitialized,
                error: error || null
            }
        };

        setDebugInfo(stats);
        return stats;
    }, [sessions, currentSession, messages, isConnected, isInitialized, error]);

    const exportData = useCallback(() => {
        const exportData = {
            timestamp: new Date().toISOString(),
            session: currentSession,
            sessions,
            messages,
            connection: {
                isConnected,
                isInitialized,
                error
            }
        };

        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `chatbot-data-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }, [currentSession, sessions, messages, isConnected, isInitialized, error]);

    return {
        debugInfo,
        generateDebugInfo,
        exportData
    };
}