import api from './axios';

// Limited chatbot API for unauthenticated users
const LIMITED_CHATBOT_BASE_URL = import.meta.env.VITE_CHATBOT_API_URL || 'http://localhost:8001';

// Limited chatbot API instance - no auth required
const limitedChatbotApi = api.create({
    baseURL: LIMITED_CHATBOT_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'X-Mode': 'limited' // Flag to indicate limited mode
    },
});

// Authenticated chatbot API instance - with auth
const chatbotApi = api.create({
    baseURL: LIMITED_CHATBOT_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth interceptor for authenticated chatbot API
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

// Limited responses for demo mode
const LIMITED_RESPONSES = {
    welcome: {
        content: "안녕하세요! 특허 분석 챗봇 데모입니다. 로그인 후 완전한 기능을 이용할 수 있습니다.",
        patent_urls: []
    },
    features: {
        content: "저희 서비스는 AI 기반 특허 분석을 제공합니다. 로그인 후에는 다음과 같은 기능을 이용할 수 있습니다:\n\n• 전체 특허 데이터베이스 검색\n• AI 기반 특허 분석\n• 상세 분석 보고서 생성\n• 맞춤형 추천 기능\n• 다중 에이전트 워크플로우\n• 실시간 데이터 처리\n\n로그인하면 모든 기능을 이용해보세요!",
        patent_urls: []
    },
    pricing: {
        content: "현재 무료 체험 기간을 제공하고 있습니다. 로그인 후 모든 기능을 무료로 이용해보실 수 있습니다.\n\n추가 문의가 필요하시면 contact@patent-board.com으로 연락주세요.",
        patent_urls: []
    },
    login_prompt: {
        content: "로그인 후에는 실제 특허 데이터 분석, AI 기반 검색, 상세 보고서 생성 등 모든 기능을 이용하실 수 있습니다.\n\n지금 로그인해서 완전한 체험을 시작해보세요!",
        patent_urls: []
    }
};

// Check if user is authenticated
const isAuthenticated = () => {
    return !!localStorage.getItem('token');
};

// Get user ID from localStorage or generate demo ID
const getUserId = () => {
    let userId = localStorage.getItem('userId');
    if (!userId) {
        userId = `demo_user_${Date.now()}`;
        localStorage.setItem('userId', userId);
    }
    return userId;
};

// Limited Chatbot API functions
export const limitedChatbotAPI = {
    // Send limited chat message
    chat: async (message, sessionId = null) => {
        try {
            // Simple keyword matching for demo responses
            const lowerMessage = message.toLowerCase();
            
            let response = LIMITED_RESPONSES.welcome;
            
            if (lowerMessage.includes('안녕') || lowerMessage.includes('hello')) {
                response = LIMITED_RESPONSES.welcome;
            } else if (lowerMessage.includes('기능') || lowerMessage.includes('무엇') || lowerMessage.includes('what')) {
                response = LIMITED_RESPONSES.features;
            } else if (lowerMessage.includes('가격') || lowerMessage.includes('비용') || lowerMessage.includes('price')) {
                response = LIMITED_RESPONSES.pricing;
            } else if (lowerMessage.includes('로그인') || lowerMessage.includes('login')) {
                response = LIMITED_RESPONSES.login_prompt;
            } else if (lowerMessage.includes('특허') || lowerMessage.includes('patent')) {
                response = {
                    content: "특허 분석 기능은 로그인 후에 사용 가능합니다. 지금 로그인해서 전체 특허 데이터베이스에 접근해보세요!",
                    patent_urls: []
                };
            } else {
                response = {
                    content: "기본 안내 기능만 제공됩니다. 로그인 후에는 실제 특허 분석, AI 검색, 보고서 생성 등 모든 기능을 이용할 수 있습니다.",
                    patent_urls: []
                };
            }

            return {
                success: true,
                session_id: sessionId || `limited_session_${Date.now()}`,
                response: response,
                context: {
                    mode: 'limited',
                    message_count: 1,
                    demo_mode: true
                },
                user_properties: {},
                total_messages: 1
            };
        } catch (error) {
            console.error('Limited chat API error:', error);
            // Return fallback response
            return {
                success: false,
                session_id: sessionId || `limited_session_${Date.now()}`,
                response: {
                    content: "죄송합니다. 현재 기능 제한 모드입니다. 로그인 후 다시 시도해주세요.",
                    patent_urls: []
                },
                context: {},
                user_properties: {},
                total_messages: 0
            };
        }
    },

    // Health check
    health: async () => {
        try {
            const response = await limitedChatbotApi.get('/health');
            return {
                ...response.data,
                mode: 'limited',
                authenticated: false
            };
        } catch (error) {
            console.error('Limited health check error:', error);
            return {
                status: 'limited_mode',
                timestamp: new Date().toISOString(),
                service: "langgraph-chatbot-limited",
                mode: 'limited',
                authenticated: false
            };
        }
    },

    // Create demo session
    createSession: async (userId) => {
        try {
            return {
                session_id: `limited_demo_session_${Date.now()}`,
                message: "Limited mode session created"
            };
        } catch (error) {
            console.error('Limited create session error:', error);
            return {
                session_id: `limited_demo_session_${Date.now()}`,
                message: "Session created in limited mode"
            };
        }
    },

    // Get session info (limited)
    getSession: async (sessionId) => {
        return {
            session_id,
            user_id: getUserId(),
            title: "데모 세션",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            message_count: 0,
            context: {
                mode: 'limited',
                authenticated: false
            }
        };
    },

    // Get user sessions (limited)
    getUserSessions: async (userId) => {
        return [];
    },

    // User properties (limited - read-only)
    getUserProperties: async (userId) => {
        return {
            mode: 'limited',
            authenticated: false,
            features: ['basic_info', 'demo_chat'],
            restrictions: ['full_analysis', 'patent_search', 'report_generation']
        };
    },

    // Set user properties (limited - not allowed)
    setUserProperties: async (userId, properties) => {
        throw new Error('User properties can only be set in authenticated mode');
    }
};

// Full Chatbot API functions (for authenticated users)
export const chatbotAPI = {
    // Send chat message - uses authenticated API
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

    // Create new session - uses authenticated API
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

    // Get session info - uses authenticated API
    getSession: async (sessionId) => {
        try {
            const response = await chatbotApi.get(`/sessions/${sessionId}`);
            return response.data;
        } catch (error) {
            console.error('Get session error:', error);
            throw error;
        }
    },

    // Get user sessions - uses authenticated API
    getUserSessions: async (userId) => {
        try {
            const response = await chatbotApi.get(`/users/${userId}/sessions`);
            return response.data;
        } catch (error) {
            console.error('Get user sessions error:', error);
            throw error;
        }
    },

    // Set user properties - uses authenticated API
    setUserProperties: async (userId, properties) => {
        try {
            const response = await chatbotApi.post(`/users/${userId}/properties`, properties);
            return response.data;
        } catch (error) {
            console.error('Set user properties error:', error);
            throw error;
        }
    },

    // Get user properties - uses authenticated API
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
            return {
                ...response.data,
                mode: 'full',
                authenticated: true
            };
        } catch (error) {
            console.error('Health check error:', error);
            throw error;
        }
    }
};

// Export the appropriate API based on authentication status
export const getChatbotAPI = () => {
    if (isAuthenticated()) {
        return chatbotAPI;
    } else {
        return limitedChatbotAPI;
    }
};

// Utility function to check authentication status
export const checkAuthStatus = () => {
    return {
        isAuthenticated: isAuthenticated(),
        userId: getUserId(),
        mode: isAuthenticated() ? 'full' : 'limited'
    };
};