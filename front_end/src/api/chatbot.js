import api from './axios';

// LangGraph Chatbot API configuration
const CHATBOT_BASE_URL = import.meta.env.VITE_CHATBOT_API_URL || 'http://localhost:8001';

// Chatbot API instance - separate from main API to handle different port
const chatbotApi = api.create({
    baseURL: CHATBOT_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth interceptor for chatbot API
chatbotApi.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Chatbot API functions
export const chatbotAPI = {
    // Send chat message
    chat: async (message, sessionId = null) => {
        try {
            const response = await chatbotApi.post('/chat', {
                message,
                session_id: sessionId
            });
            return response.data;
        } catch (error) {
            console.error('Chat API error:', error);
            throw error;
        }
    },

    // Create new session
    createSession: async (userId) => {
        try {
            const response = await chatbotApi.post('/sessions', {
                user_id: userId
            });
            return response.data;
        } catch (error) {
            console.error('Create session error:', error);
            throw error;
        }
    },

    // Get session information
    getSession: async (sessionId) => {
        try {
            const response = await chatbotApi.get(`/sessions/${sessionId}`);
            return response.data;
        } catch (error) {
            console.error('Get session error:', error);
            throw error;
        }
    },

    // Get user's sessions
    getUserSessions: async (userId) => {
        try {
            const response = await chatbotApi.get(`/users/${userId}/sessions`);
            return response.data;
        } catch (error) {
            console.error('Get user sessions error:', error);
            throw error;
        }
    },

    // Set user properties
    setUserProperties: async (userId, properties) => {
        try {
            const response = await chatbotApi.post(`/users/${userId}/properties`, properties);
            return response.data;
        } catch (error) {
            console.error('Set user properties error:', error);
            throw error;
        }
    },

    // Get user properties
    getUserProperties: async (userId) => {
        try {
            const response = await chatbotApi.get(`/users/${userId}/properties`);
            return response.data;
        } catch (error) {
            console.error('Get user properties error:', error);
            throw error;
        }
    },

    // Health check
    health: async () => {
        try {
            const response = await chatbotApi.get('/health');
            return response.data;
        } catch (error) {
            console.error('Health check error:', error);
            throw error;
        }
    }
};

export default chatbotApi;