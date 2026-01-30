import React, { useEffect, useState } from 'react';
import { ChatbotProvider, useChatbot } from '../context/ChatbotContext';
import Chatbot from '../components/Chatbot/Chatbot';
import LimitedChat from '../components/Chatbot/LimitedChat';

// Main chat page component
function ChatPage() {
    const { authStatus, reinitializeOnAuthChange } = useChatbot();
    const [isAuthChecking, setIsAuthChecking] = useState(true);

    useEffect(() => {
        // Simulate auth checking delay
        const timer = setTimeout(() => {
            setIsAuthChecking(false);
        }, 1000);

        return () => clearTimeout(timer);
    }, []);

    useEffect(() => {
        // Re-initialize when auth status changes
        reinitializeOnAuthChange();
    }, [authStatus, reinitializeOnAuthChange]);

    if (isAuthChecking) {
        return (
            <div className="chat-loading d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
                <div className="text-center">
                    <div className="spinner-border text-primary" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="mt-3 text-muted">Checking authentication status...</p>
                </div>
            </div>
        );
    }

    // Show LimitedChat for unauthenticated users
    if (!authStatus.isAuthenticated) {
        return (
            <LimitedChat 
                onGetStarted={() => {
                    // Demo login - create demo credentials
                    const demoUserId = `demo_user_${Date.now()}`;
                    localStorage.setItem('userId', demoUserId);
                    localStorage.setItem('token', 'demo_token');
                    // Trigger re-initialization
                    reinitializeOnAuthChange();
                }}
            />
        );
    }

    // Show full Chatbot for authenticated users
    return (
        <div className="chat-page h-100">
            <Chatbot userId={authStatus.userId} layout="split" />
        </div>
    );
}

// Wrapper component with provider
function ChatPageWithProvider() {
    return (
        <ChatbotProvider>
            <ChatPage />
        </ChatbotProvider>
    );
}

export default ChatPageWithProvider;