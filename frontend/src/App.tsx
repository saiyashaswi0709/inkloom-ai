import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/layout/Layout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { BrandKnowledgeBase } from './pages/BrandKnowledgeBase';
import { GuidelineManagement } from './pages/GuidelineManagement';
import { ApprovedFacts } from './pages/ApprovedFacts';
import { BrandRules } from './pages/BrandRules';
import { ContentAnalysisWorkspace } from './pages/ContentAnalysisWorkspace';
import { AnalysisResults } from './pages/AnalysisResults';
import { SmartCorrectionEditor } from './pages/SmartCorrectionEditor';
import { SubmissionHistory } from './pages/SubmissionHistory';
import { ReviewCentre } from './pages/ReviewCentre';
import { GovernanceAnalytics } from './pages/GovernanceAnalytics';
import { OrganisationSettings } from './pages/OrganisationSettings';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center text-slate-400 text-sm">
        Initializing Inkloom AI...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="analysis" element={<ContentAnalysisWorkspace />} />
            <Route path="analysis/results/:id" element={<AnalysisResults />} />
            <Route path="analysis/editor/:id" element={<SmartCorrectionEditor />} />
            <Route path="submissions" element={<SubmissionHistory />} />
            <Route path="reviews" element={<ReviewCentre />} />
            <Route path="analytics" element={<GovernanceAnalytics />} />
            <Route path="knowledge" element={<BrandKnowledgeBase />} />
            <Route path="guidelines" element={<GuidelineManagement />} />
            <Route path="facts" element={<ApprovedFacts />} />
            <Route path="rules" element={<BrandRules />} />
            <Route path="settings" element={<OrganisationSettings />} />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
