import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import PatentSearch from './pages/PatentSearch';
import Settings from './pages/Settings';
import Login from './pages/Login';
import GraphAnalysis from './pages/GraphAnalysis';
import AnalysisWorkbench from './pages/AnalysisWorkbench';
import ChatPage from './pages/Chat';
import Reports from './pages/Reports';
import LandingPage from './pages/LandingPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import { NotificationsProvider } from './context/NotificationsContext';
import { ToastContainer } from './components/Notifications';
import ProtectedLayout from './components/Layout/ProtectedLayout';

// Inner component that uses auth context
const AppContent = () => {
  const { user, loading } = useAuth();
  const isAuthenticated = !!user;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-3 text-gray-600">Initializing application...</p>
        </div>
      </div>
    );
  }

  return (
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
              <Route path="/reports" element={<Reports />} />
            </Route>
          </>
        ) : (
          <>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </>
        )}
      </Routes>
    </Router>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <NotificationsProvider>
        <AppContent />
        <ToastContainer position="top-right" duration={5000} />
      </NotificationsProvider>
    </AuthProvider>
  );
}

export default App;
