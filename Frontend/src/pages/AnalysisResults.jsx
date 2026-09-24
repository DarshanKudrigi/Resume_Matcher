import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  FileText, 
  RotateCcw, 
  Printer 
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import MatchScore from '../components/MatchScore';
import SkillCard from '../components/SkillCard';
import SkillGap from '../components/SkillGap';
import LearningRecommendations from '../components/LearningRecommendations';
import ATSChecker from '../components/ATSChecker';
import ChatBox from '../components/ChatBox';
import { useApp } from '../context/AppContext';

export default function AnalysisResults() {
  const { currentJob, analysisResult } = useApp();
  const navigate = useNavigate();

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#2F2A26] dark:text-[#F4EFE8] transition-colors">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Top Header & Breadcrumb */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#E7E0D8] dark:border-[#413B34] no-print">
          <div>
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-1.5 text-xs text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] mb-2 font-medium"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Dashboard</span>
            </Link>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#2F2A26] dark:text-[#F4EFE8]">
                Resume Analysis
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#6B8E6B]/15 text-[#6B8E6B]">
                82% Match
              </span>
            </div>
            <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5] mt-1 flex items-center gap-2">
              <span>Target Role: <strong className="text-[#2F2A26] dark:text-[#F4EFE8]">{currentJob?.title || "Frontend Engineer"}</strong></span>
              <span>•</span>
              <span>Company: <strong className="text-[#2F2A26] dark:text-[#F4EFE8]">{currentJob?.company || "Apex Cloud Technologies"}</strong></span>
            </p>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              type="button"
              onClick={() => navigate('/builder')}
              className="px-4 py-2 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] text-xs font-semibold shadow-warm-sm transition-colors flex items-center gap-1.5"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Edit in Builder</span>
            </button>
            <button
              type="button"
              onClick={handlePrint}
              className="px-3 py-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] hover:border-[#7C5C3B] text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] transition-colors flex items-center gap-1.5"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print Report</span>
            </button>
            <button
              type="button"
              onClick={() => navigate('/analyzer')}
              className="px-3 py-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] hover:border-[#7C5C3B] text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] transition-colors flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Re-Analyze</span>
            </button>
          </div>
        </div>

        {/* Top Summary Banner */}
        <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 sm:p-6 shadow-warm-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1 max-w-3xl">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#7C5C3B] dark:text-[#C49A6C]">
                Executive Assessment
              </span>
              <span className="text-[11px] px-2 py-0.5 rounded bg-[#6B8E6B]/15 text-[#6B8E6B] font-semibold">
                Strong Candidate Profile
              </span>
            </div>
            <p className="text-xs sm:text-sm text-[#2F2A26] dark:text-[#F4EFE8] leading-relaxed">
              {analysisResult.summary}
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0 self-stretch sm:self-auto justify-end">
            <div className="p-3 rounded-lg bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] text-center">
              <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5] uppercase font-bold block">
                ATS Pass Rate
              </span>
              <span className="text-base font-extrabold text-[#6B8E6B]">
                86%
              </span>
            </div>
            <div className="p-3 rounded-lg bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] text-center">
              <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5] uppercase font-bold block">
                Skills Matched
              </span>
              <span className="text-base font-extrabold text-[#7C5C3B] dark:text-[#C49A6C]">
                5 / 8
              </span>
            </div>
          </div>
        </div>

        {/* Row 1: Match Score Circular Indicator (Left) & Skills Breakdown (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
          <div className="lg:col-span-1">
            <MatchScore 
              score={analysisResult.matchScore || 82} 
              title="Match Score" 
              subtitle="Comparison against Apex Cloud Requirements"
            />
          </div>

          <div className="lg:col-span-2">
            <SkillCard 
              matchedSkills={analysisResult.matchedSkills}
              missingSkills={analysisResult.missingSkills}
              partialSkills={analysisResult.partialSkills}
            />
          </div>
        </div>

        {/* Row 2: Skill Gap Visual Comparison & ATS Checker */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          <div className="lg:col-span-2">
            <SkillGap skillGaps={analysisResult.skillGaps} />
          </div>

          <div className="lg:col-span-1">
            <ATSChecker score={analysisResult.atsScore || 86} />
          </div>
        </div>

        {/* Row 3: Recommended Learning Cards */}
        <LearningRecommendations recommendations={analysisResult.learningRecommendations} />

        {/* Bottom CTA for Builder */}
        <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-6 text-center space-y-3 shadow-warm-sm no-print">
          <h4 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
            Want to boost your match score to 90%+?
          </h4>
          <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] max-w-xl mx-auto">
            Use our built-in Resume Builder to inject suggested containerization and cloud keywords directly into your project bullet points.
          </p>
          <div className="pt-2">
            <button
              type="button"
              onClick={() => navigate('/builder')}
              className="px-6 py-2.5 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] font-bold text-xs shadow-warm-sm transition-colors hover:bg-[#66492C]"
            >
              Update Resume in Builder
            </button>
          </div>
        </div>

      </main>

      <Footer />
      <ChatBox />
    </div>
  );
}
