import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  ArrowRight, 
  CheckCircle2, 
  FileText, 
  Target, 
  BookOpen, 
  ShieldCheck 
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import JobDescriptionCard from '../components/JobDescriptionCard';
import ResumeUpload from '../components/ResumeUpload';
import ChatBox from '../components/ChatBox';
import { useApp } from '../context/AppContext';

export default function Dashboard() {
  const { user, currentJob, uploadedFile, triggerAnalysis, showToast } = useApp();
  const navigate = useNavigate();
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyzeClick = () => {
    if (!uploadedFile) {
      showToast("Please select or upload a resume file first!", "info");
      return;
    }
    setIsAnalyzing(true);
    triggerAnalysis();

    setTimeout(() => {
      setIsAnalyzing(false);
      navigate('/results');
    }, 700);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#2F2A26] dark:text-[#F4EFE8] transition-colors">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
        
        {/* Welcome Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-[#E7E0D8]/80 dark:border-[#413B34]/80">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/20 text-[#7C5C3B] dark:text-[#C49A6C] border border-[#7C5C3B]/20 dark:border-[#C49A6C]/30 inline-flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                AI-Powered Matching Engine
              </span>
              <span className="text-xs text-[#77716B] dark:text-[#B9B0A5]">
                v1.0 (Frontend Demo)
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#2F2A26] dark:text-[#F4EFE8]">
              Welcome back, {user.name.split(' ')[0]}
            </h1>
            <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5] mt-1">
              Compare your resume with a job description and understand where you stand.
            </p>
          </div>

          {/* Quick Metrics Bar */}
          <div className="flex items-center gap-3">
            <div className="px-4 py-2.5 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-sm">
              <span className="text-[10px] uppercase font-bold text-[#77716B] dark:text-[#B9B0A5] block">
                Target Role
              </span>
              <span className="text-xs font-bold text-[#2F2A26] dark:text-[#F4EFE8] truncate max-w-[140px] block">
                {currentJob?.title || "Frontend Engineer"}
              </span>
            </div>
            <div className="px-4 py-2.5 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-sm text-center">
              <span className="text-[10px] uppercase font-bold text-[#77716B] dark:text-[#B9B0A5] block">
                Avg Match
              </span>
              <span className="text-sm font-extrabold text-[#6B8E6B]">
                82%
              </span>
            </div>
          </div>
        </div>

        {/* Two Column Grid: Job Description Card (Left) & Resume Upload Card (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          <JobDescriptionCard />
          <ResumeUpload />
        </div>

        {/* Primary Action: ANALYZE RESUME BUTTON */}
        <div className="rounded-2xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-6 sm:p-8 shadow-warm-sm text-center space-y-4">
          <div className="max-w-xl mx-auto space-y-2">
            <h3 className="text-lg sm:text-xl font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Ready to calculate match & analyze skill gaps?
            </h3>
            <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5]">
              Our client-side matching algorithm parses candidate competencies, identifies missing skills against the job posting, and generates personalized learning roadmaps.
            </p>
          </div>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
            <button
              type="button"
              disabled={isAnalyzing}
              onClick={handleAnalyzeClick}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] dark:hover:bg-[#B38757] text-sm font-bold shadow-warm-md hover:shadow-warm-lg transition-all duration-200 flex items-center justify-center gap-2.5 group disabled:opacity-50"
            >
              {isAnalyzing ? (
                <>
                  <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  <span>Analyzing Resume...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-[#D8A48F] dark:text-[#1F1D1A]" />
                  <span>Analyze Resume</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => navigate('/builder')}
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 hover:bg-[#F7F5F0] dark:hover:bg-[#1F1D1A] text-xs sm:text-sm font-semibold text-[#2F2A26] dark:text-[#F4EFE8] transition-colors flex items-center justify-center gap-2"
            >
              <FileText className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C]" />
              <span>Open Resume Builder</span>
            </button>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 pt-2 text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#6B8E6B]" /> Instant Match Scoring
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#6B8E6B]" /> Detailed Skill Gap Breakdown
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#6B8E6B]" /> ATS Readability Check
            </span>
          </div>
        </div>

        {/* Feature Cards Grid (College Project Showcase) */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <div className="p-5 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-sm">
            <div className="w-8 h-8 rounded-lg bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/15 text-[#7C5C3B] dark:text-[#C49A6C] flex items-center justify-center mb-3">
              <Target className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8] mb-1">
              Skill Gap Detection
            </h4>
            <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] leading-relaxed">
              Find exact mismatches like Docker and AWS before recruiters review your application.
            </p>
          </div>

          <div className="p-5 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-sm">
            <div className="w-8 h-8 rounded-lg bg-[#6B8E6B]/10 text-[#6B8E6B] flex items-center justify-center mb-3">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8] mb-1">
              ATS Compatibility Check
            </h4>
            <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] leading-relaxed">
              Automated audit of section headers, contact points, formatting, and keyword densities.
            </p>
          </div>

          <div className="p-5 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-sm">
            <div className="w-8 h-8 rounded-lg bg-[#C99545]/10 text-[#C99545] flex items-center justify-center mb-3">
              <BookOpen className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8] mb-1">
              Learning Roadmaps
            </h4>
            <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] leading-relaxed">
              Curated study courses, tutorials, and time estimates to quickly bridge your gap areas.
            </p>
          </div>
        </div>

      </main>

      <Footer />
      <ChatBox />
    </div>
  );
}
