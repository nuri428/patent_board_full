import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import PatentSearch from './pages/PatentSearch';
import Settings from './pages/Settings';
import Login from './pages/Login';
import GraphAnalysis from './pages/GraphAnalysis';
import AnalysisWorkbench from './pages/AnalysisWorkbench';
import ChatPage from './pages/Chat';
import LandingPage from './pages/LandingPage';
import { AuthProvider } from './context/AuthContext';
import ProtectedLayout from './components/Layout/ProtectedLayout';

const App = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      const userId = localStorage.getItem('userId');
      setIsAuthenticated(!!token && !!userId);
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const handleGetStarted = () => {
    setIsAuthenticated(true);
    localStorage.setItem('token', 'demo_token');
    localStorage.setItem('userId', `user_${Date.now()}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3 text-muted">Initializing application...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthProvider>
      <Router>
        <Routes>
          {isAuthenticated ? (
            <>
              <Route path="/" element={<Navigate to="/chat" replace />} />
              <Route element={<ProtectedLayout />}>
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/search" element={<PatentSearch />} />
                <Route path="/graph" element={<GraphAnalysis />} />
                <Route path="/analysis" element={<AnalysisWorkbench />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/reports" element={<div className="p-6">Reports Page (Coming Soon)</div>} />
              </Route>
            </>
          ) : (
            <>
              <Route path="/" element={<LandingPage onGetStarted={handleGetStarted} />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </>
          )}
          <Route path="/login" element={<Login />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
