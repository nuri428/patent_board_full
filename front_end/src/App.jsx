// React 19 — JSX transform 자동, explicit import 불필요
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import PatentSearch from './pages/PatentSearch';
import Settings from './pages/Settings';
import Login from './pages/Login';
import GraphAnalysis from './pages/GraphAnalysis';
import AnalysisWorkbench from './pages/AnalysisWorkbench';
import ChatPage from './pages/Chat';
import Reports from './pages/Reports';
import Admin from './pages/Admin';
import TGIPLanding from './pages/tgip/TGIPLanding';
import { AuthProvider, useAuth } from './context/AuthContext';
import { NotificationsProvider } from './context/NotificationsContext';
import { ToastContainer } from './components/Notifications';
import ProtectedLayout from './components/Layout/ProtectedLayout';
// TGIP
import TGIPPublicLayout from './components/tgip/Layout/TGIPPublicLayout';
import TGIPAppLayout from './components/tgip/Layout/TGIPAppLayout';
import TGIPOverview from './pages/tgip/TGIPOverview';
import TGIPFeatures from './pages/tgip/TGIPFeatures';
import TGIPDemo from './pages/tgip/TGIPDemo';
import TGIPDocs from './pages/tgip/TGIPDocs';
import TGIPAbout from './pages/tgip/TGIPAbout';
import TGIPWorkspace from './pages/tgip/TGIPWorkspace';
import RunDetail from './pages/tgip/RunDetail';
import Library from './pages/tgip/Library';

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
        {/* TGIP 공개 라우트 (인증 무관) */}
        <Route element={<TGIPPublicLayout />}>
          <Route path="/overview" element={<TGIPOverview />} />
          <Route path="/features" element={<TGIPFeatures />} />
          <Route path="/features/:view" element={<TGIPFeatures />} />
          <Route path="/demo" element={<TGIPDemo />} />
          <Route path="/docs" element={<TGIPDocs />} />
          <Route path="/about" element={<TGIPAbout />} />
        </Route>

        {/* TGIP 앱 라우트 (인증 선택적) */}
        <Route path="/app" element={<Navigate to="/app/tech/solid-state-battery" replace />} />
        <Route element={<TGIPAppLayout />}>
          <Route path="/app/tech/:technology_id" element={<TGIPWorkspace />} />
          <Route path="/app/runs/:run_id" element={<RunDetail />} />
          <Route path="/app/library" element={<Library />} />
        </Route>

        {/* 기존 Patent Board 라우트 */}
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
              <Route path="/admin" element={<Admin />} />
            </Route>
          </>
        ) : (
          <>
            <Route path="/" element={<TGIPLanding />} />
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
