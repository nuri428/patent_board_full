import React, { createContext, useContext, useReducer, useEffect, useState } from 'react';
import { getChatbotAPI, checkAuthStatus } from '../api/chatbot_modes';

// Initial state
const initialState = {
    currentSession: null,
    sessions: [],
    messages: [],
    isLoading: false,
    error: null,
    userProperties: {},
    isConnected: false,
    isInitialized: false,
    authStatus: {
        isAuthenticated: false,
        userId: null,
        mode: 'limited'
    }
};

// Action types
const ActionTypes = {
    SET_CURRENT_SESSION: 'SET_CURRENT_SESSION',
    SET_SESSIONS: 'SET_SESSIONS',
    SET_MESSAGES: 'SET_MESSAGES',
    ADD_MESSAGE: 'ADD_MESSAGE',
    SET_LOADING: 'SET_LOADING',
    SET_ERROR: 'SET_ERROR',
    SET_USER_PROPERTIES: 'SET_USER_PROPERTIES',
    SET_CONNECTED: 'SET_CONNECTED',
    SET_INITIALIZED: 'SET_INITIALIZED',
    CLEAR_CHAT: 'CLEAR_CHAT',
    SET_AUTH_STATUS: 'SET_AUTH_STATUS'
};

// Reducer
function chatbotReducer(state, action) {
    switch (action.type) {
        case ActionTypes.SET_CURRENT_SESSION:
            return {
                ...state,
                currentSession: action.payload,
                error: null
            };
        case ActionTypes.SET_SESSIONS:
            return {
                ...state,
                sessions: action.payload
            };
        case ActionTypes.SET_MESSAGES:
            return {
                ...state,
                messages: action.payload
            };
        case ActionTypes.ADD_MESSAGE:
            return {
                ...state,
                messages: [...state.messages, action.payload]
            };
        case ActionTypes.SET_LOADING:
            return {
                ...state,
                isLoading: action.payload
            };
        case ActionTypes.SET_ERROR:
            return {
                ...state,
                error: action.payload,
                isLoading: false
            };
        case ActionTypes.SET_USER_PROPERTIES:
            return {
                ...state,
                userProperties: action.payload
            };
        case ActionTypes.SET_CONNECTED:
            return {
                ...state,
                isConnected: action.payload
            };
        case ActionTypes.SET_INITIALIZED:
            return {
                ...state,
                isInitialized: action.payload
            };
        case ActionTypes.CLEAR_CHAT:
            return {
                ...state,
                messages: [],
                currentSession: null,
                error: null
            };
        case ActionTypes.SET_AUTH_STATUS:
            return {
                ...state,
                authStatus: action.payload
            };
        default:
            return state;
    }
}

// Context
const ChatbotContext = createContext();

// Provider component
export function ChatbotProvider({ children }) {
    const [state, dispatch] = useReducer(chatbotReducer, initialState);
    const [api, setApi] = useState(null);

    // Check authentication status and set appropriate API
    useEffect(() => {
        const { isAuthenticated, userId, mode } = checkAuthStatus();
        dispatch({
            type: ActionTypes.SET_AUTH_STATUS,
            payload: { isAuthenticated, userId, mode }
        });

        // Set the appropriate API based on auth status
        setApi(getChatbotAPI());
    }, []);

    // Initialize chatbot
    useEffect(() => {
        if (api) {
            initializeChatbot();
        }
    }, [api]);

    const initializeChatbot = async () => {
        try {
            dispatch({ type: ActionTypes.SET_LOADING, payload: true });

            // Check if LangGraph service is healthy
            const health = await api.health();
            dispatch({ type: ActionTypes.SET_CONNECTED, payload: true });

            // Get authentication status and load user data if authenticated
            const { isAuthenticated, userId } = state.authStatus;
            if (isAuthenticated && userId) {
                try {
                    // Load user's sessions
                    const sessions = await api.getUserSessions(userId);
                    dispatch({ type: ActionTypes.SET_SESSIONS, payload: sessions });

                    // Load user properties
                    const properties = await api.getUserProperties(userId);
                    dispatch({ type: ActionTypes.SET_USER_PROPERTIES, payload: properties });

                    // If no current session and there are existing sessions, use the most recent one
                    if (sessions.length > 0 && !state.currentSession) {
                        await loadSession(sessions[0].id);
                    }
                } catch (error) {
                    console.error('Failed to load user data:', error);
                    // Continue with limited mode if user data loading fails
                }
            }

            dispatch({ type: ActionTypes.SET_INITIALIZED, payload: true });
        } catch (error) {
            console.error('Failed to initialize chatbot:', error);
            dispatch({
                type: ActionTypes.SET_ERROR,
                payload: 'Failed to connect to chat service. Please try again later.'
            });
            dispatch({ type: ActionTypes.SET_CONNECTED, payload: false });
        } finally {
            dispatch({ type: ActionTypes.SET_LOADING, payload: false });
        }
    };

    const createSession = async (userId) => {
        try {
            dispatch({ type: ActionTypes.SET_LOADING, payload: true });

            const newSessionData = await api.createSession(userId);
            const newSession = {
                id: newSessionData.session_id,
                user_id: userId,
                title: "New Conversation",
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                message_count: 0,
                context: {}
            };
            dispatch({ type: ActionTypes.SET_CURRENT_SESSION, payload: newSession });
            dispatch({ type: ActionTypes.SET_SESSIONS, payload: [newSession, ...state.sessions] });

            return newSession;
        } catch (error) {
            console.error('Failed to create session:', error);
            dispatch({
                type: ActionTypes.SET_ERROR,
                payload: 'Failed to create new chat session.'
            });
            throw error;
        } finally {
            dispatch({ type: ActionTypes.SET_LOADING, payload: false });
        }
    };

    const loadSession = async (sessionId) => {
        try {
            dispatch({ type: ActionTypes.SET_LOADING, payload: true });

            const session = await api.getSession(sessionId);
            dispatch({ type: ActionTypes.SET_CURRENT_SESSION, payload: session });

            // Load messages for this session (this would need to be implemented in the backend)
            // For now, we'll start with empty messages
            dispatch({ type: ActionTypes.SET_MESSAGES, payload: [] });

            return session;
        } catch (error) {
            console.error('Failed to load session:', error);
            dispatch({
                type: ActionTypes.SET_ERROR,
                payload: 'Failed to load chat session.'
            });
            throw error;
        } finally {
            dispatch({ type: ActionTypes.SET_LOADING, payload: false });
        }
    };

    const sendMessage = async (message, sessionId = null) => {
        const currentSessionId = sessionId || state.currentSession?.id;

        if (!currentSessionId) {
            throw new Error('No active session');
        }

        try {
            dispatch({ type: ActionTypes.SET_LOADING, payload: true });

            // Add user message to UI immediately
            const userMessage = {
                id: Date.now().toString(),
                content: message,
                role: 'user',
                timestamp: new Date().toISOString(),
                pending: true
            };

            dispatch({ type: ActionTypes.ADD_MESSAGE, payload: userMessage });

            // Send message to LangGraph service
            const response = await api.chat(message, currentSessionId);

            // Remove pending flag and update with AI response
            const updatedUserMessage = {
                ...userMessage,
                pending: false
            };

            const aiMessage = {
                id: response.session_id || Date.now().toString(),
                content: response.response?.content || response.response || 'I apologize, but I had trouble processing your request.',
                role: 'assistant',
                timestamp: new Date().toISOString(),
                sources: response.sources || [],
                metadata: response.metadata || response.context || {},
                patent_urls: response.response?.patent_urls || []
            };

            dispatch({ type: ActionTypes.SET_MESSAGES, payload: [...state.messages.filter(msg => msg.id !== userMessage.id), updatedUserMessage, aiMessage] });

            return aiMessage;
        } catch (error) {
            console.error('Failed to send message:', error);

            // Update user message to show error
            const errorMessage = {
                ...state.messages[state.messages.length - 1],
                pending: false,
                content: 'Sorry, I encountered an error. Please try again.',
                error: true
            };

            dispatch({
                type: ActionTypes.SET_MESSAGES,
                payload: [...state.messages.slice(0, -1), errorMessage]
            });

            dispatch({
                type: ActionTypes.SET_ERROR,
                payload: 'Failed to send message. Please try again.'
            });

            throw error;
        } finally {
            dispatch({ type: ActionTypes.SET_LOADING, payload: false });
        }
    };

    const setUserProperties = async (userId, properties) => {
        try {
            await api.setUserProperties(userId, properties);
            dispatch({ type: ActionTypes.SET_USER_PROPERTIES, payload: properties });
        } catch (error) {
            console.error('Failed to set user properties:', error);
            throw error;
        }
    };

    const clearChat = () => {
        dispatch({ type: ActionTypes.CLEAR_CHAT });
    };

    const refreshSessions = async (userId) => {
        try {
            const sessions = await api.getUserSessions(userId);
            dispatch({ type: ActionTypes.SET_SESSIONS, payload: sessions });
            return sessions;
        } catch (error) {
            console.error('Failed to refresh sessions:', error);
            throw error;
        }
    };

    // Re-initialize when auth status changes
    const value = {
        ...state,
        createSession,
        loadSession,
        sendMessage,
        setUserProperties,
        clearChat,
        refreshSessions,
        initializeChatbot,
        api
    };

    return (
        <ChatbotContext.Provider value={value}>
            {children}
        </ChatbotContext.Provider>
    );
}

// Hook to use the chatbot context
export function useChatbot() {
    const context = useContext(ChatbotContext);
    if (!context) {
        throw new Error('useChatbot must be used within a ChatbotProvider');
    }
    return context;
}

export default ChatbotContext;