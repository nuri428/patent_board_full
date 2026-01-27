import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import PatentSearch from './pages/PatentSearch';
import Settings from './pages/Settings';
import Login from './pages/Login';
import GraphAnalysis from './pages/GraphAnalysis';
import AnalysisWorkbench from './pages/AnalysisWorkbench';
import { AuthProvider } from './context/AuthContext';
import ProtectedLayout from './components/Layout/ProtectedLayout';

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />

          {/* Protected Routes */}
          <Route element={<ProtectedLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/search" element={<PatentSearch />} />
            <Route path="/graph" element={<GraphAnalysis />} />
            <Route path="/analysis" element={<AnalysisWorkbench />} />
            <Route path="/settings" element={<Settings />} />

            {/* Placeholders for future routes */}
            <Route path="/reports" element={<div className="p-6">Reports Page (Coming Soon)</div>} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
