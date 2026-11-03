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
import { useApp } from '../context/AppContext';

export default function AnalysisResults() {
  const { currentJob, analysisResult } = useApp();
  const navigate = useNavigate();

  const handlePrint = () => {
    window.print();
  };

  const matchScore = analysisResult?.matchScore ?? 0;
  const atsScore = analysisResult?.atsScore ?? (analysisResult?.atsBreakdown?.score ?? 0);
  const status = analysisResult?.status || "Candidate Assessment";
  const matchedCount = analysisResult?.matchedSkills?.length || 0;
  const missingCount = analysisResult?.missingSkills?.length || 0;
  const totalTargetCount = matchedCount + missingCount;

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
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                matchScore >= 75 
                  ? 'bg-[#6B8E6B]/15 text-[#6B8E6B]'
                  : (matchScore >= 50 ? 'bg-[#C99545]/15 text-[#C99545]' : 'bg-red-500/15 text-red-500')
              }`}>
                {matchScore}% Match
              </span>
            </div>
            <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5] mt-1 flex items-center gap-2">
              <span>Target Role: <strong className="text-[#2F2A26] dark:text-[#F4EFE8]">{currentJob?.title || "Target Position"}</strong></span>
              <span>•</span>
              <span>Company: <strong className="text-[#2F2A26] dark:text-[#F4EFE8]">{currentJob?.company || "Target Company"}</strong></span>
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
              <span className={`text-[11px] px-2 py-0.5 rounded font-semibold ${
                matchScore >= 75 ? 'bg-[#6B8E6B]/15 text-[#6B8E6B]' : 'bg-[#C99545]/15 text-[#C99545]'
              }`}>
                {status}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-[#2F2A26] dark:text-[#F4EFE8] leading-relaxed">
              {analysisResult?.summary || "Analysis completed based on extracted competencies."}
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0 self-stretch sm:self-auto justify-end">
            <div className="p-3 rounded-lg bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] text-center">
              <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5] uppercase font-bold block">
                ATS Pass Rate
              </span>
              <span className="text-base font-extrabold text-[#6B8E6B]">
                {atsScore}%
              </span>
            </div>
            <div className="p-3 rounded-lg bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] text-center">
              <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5] uppercase font-bold block">
                Skills Matched
              </span>
              <span className="text-base font-extrabold text-[#7C5C3B] dark:text-[#C49A6C]">
                {matchedCount} / {totalTargetCount || matchedCount}
              </span>
            </div>
          </div>
        </div>

        {/* Row 1: Match Score Circular Indicator (Left) & Skills Breakdown (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
          <div className="lg:col-span-1">
            <MatchScore 
              score={matchScore} 
              title="Match Score" 
              subtitle={`Comparison against ${currentJob?.company || 'Target Company'} Requirements`}
            />
          </div>

          <div className="lg:col-span-2">
            <SkillCard 
              matchedSkills={analysisResult?.matchedSkills || []}
              missingSkills={analysisResult?.missingSkills || []}
              partialSkills={analysisResult?.partialSkills || []}
            />
          </div>
        </div>

        {/* Row 2: Skill Gap Visual Comparison & ATS Checker */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          <div className="lg:col-span-2">
            <SkillGap skillGaps={analysisResult?.skillGaps || []} />
          </div>

          <div className="lg:col-span-1">
            <ATSChecker atsBreakdown={analysisResult?.atsBreakdown} />
          </div>
        </div>

        {/* Row 3: Personalized Learning Recommendations */}
        <LearningRecommendations recommendations={analysisResult?.learningRecommendations || []} />

      </main>

      <Footer />
    </div>
  );
}
