import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AppProvider } from './context/AppContext';

// Pages
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Analyzer from './pages/Analyzer';
import AnalysisResults from './pages/AnalysisResults';
import ResumeBuilder from './pages/ResumeBuilder';
import MyResumes from './pages/MyResumes';
import History from './pages/History';
import Settings from './pages/Settings';

export default function App() {
  return (
    <ThemeProvider>
      <AppProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/analyzer" element={<Analyzer />} />
            <Route path="/results" element={<AnalysisResults />} />
            <Route path="/builder" element={<ResumeBuilder />} />
            <Route path="/my-resumes" element={<MyResumes />} />
            <Route path="/history" element={<History />} />
            <Route path="/settings" element={<Settings />} />
            
            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AppProvider>
    </ThemeProvider>
  );
}
