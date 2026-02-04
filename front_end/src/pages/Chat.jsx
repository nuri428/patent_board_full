import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatbotProvider, useChatbot } from '../context/ChatbotContext';
import Chatbot from '../components/Chatbot/Chatbot';
import LimitedChat from '../components/Chatbot/LimitedChat';

// Main chat page component
function ChatPage() {
    const { authStatus, reinitializeOnAuthChange } = useChatbot();
    const [isAuthChecking, setIsAuthChecking] = useState(true);
    const navigate = useNavigate();

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
                    // Redirect to login page instead of using demo token
                    navigate('/login');
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
