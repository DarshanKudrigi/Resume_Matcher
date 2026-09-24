import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  ArrowRight, 
  CheckCircle2, 
  Cpu 
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ChatBox from '../components/ChatBox';
import JobDescriptionCard from '../components/JobDescriptionCard';
import ResumeUpload from '../components/ResumeUpload';
import { useApp } from '../context/AppContext';

export default function Analyzer() {
  const { currentJob, uploadedFile, triggerAnalysis, showToast } = useApp();
  const navigate = useNavigate();
  const [analyzingState, setAnalyzingState] = useState('idle'); // 'idle' | 'running' | 'completed'
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { title: "Parsing Candidate Resume", desc: "Extracting skills, experience timelines, and metrics..." },
    { title: "Analyzing Target Job Description", desc: "Extracting required vs preferred technical competencies..." },
    { title: "Computing Semantic Match Index", desc: "Calculating multi-vector alignment and weighting scores..." },
    { title: "Generating Skill Gap Report", desc: "Compiling missing technologies and learning roadmaps..." }
  ];

  const handleStartAnalysis = () => {
    if (!uploadedFile) {
      showToast("Please upload or keep a resume file active", "info");
      return;
    }

    setAnalyzingState('running');
    setCurrentStep(0);

    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        } else {
          clearInterval(stepInterval);
          setAnalyzingState('completed');
          triggerAnalysis();
          setTimeout(() => {
            navigate('/results');
          }, 900);
          return prev;
        }
      });
    }, 600);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#2F2A26] dark:text-[#F4EFE8] transition-colors">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E7E0D8] dark:border-[#413B34] gap-4">
          <div>
            <span className="text-xs font-semibold text-[#7C5C3B] dark:text-[#C49A6C] uppercase tracking-wider block mb-1">
              Resume Matching Engine
            </span>
            <h1 className="text-2xl sm:text-3xl font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Resume Analyzer
            </h1>
            <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5] mt-1">
              Evaluate your resume against real-world job requirements with automated skill gap detection.
            </p>
          </div>

          <button
            type="button"
            onClick={() => navigate('/results')}
            className="px-4 py-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] hover:border-[#7C5C3B] text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] transition-colors shadow-warm-sm self-start sm:self-auto"
          >
            View Latest Results (82%)
          </button>
        </div>

        {/* Input Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          <JobDescriptionCard />
          <ResumeUpload />
        </div>

        {/* Analysis Status or Action Area */}
        <div className="rounded-2xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-6 sm:p-8 shadow-warm-sm">
          
          {analyzingState === 'idle' && (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="space-y-1 text-center sm:text-left">
                <h3 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                  Ready to benchmark candidate profile?
                </h3>
                <p className="text-xs text-[#77716B] dark:text-[#B9B0A5]">
                  Analysis will compare your extracted frontend skills against "{currentJob?.title || 'Target Job'}".
                </p>
              </div>

              <button
                type="button"
                onClick={handleStartAnalysis}
                className="w-full sm:w-auto px-7 py-3 rounded-xl bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] dark:hover:bg-[#B38757] text-sm font-bold shadow-warm-md flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4 text-[#D8A48F] dark:text-[#1F1D1A]" />
                <span>Run Deep Match Analysis</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}

          {analyzingState === 'running' && (
            <div className="space-y-6 py-4 max-w-xl mx-auto">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-full bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/20 text-[#7C5C3B] dark:text-[#C49A6C] flex items-center justify-center mx-auto animate-pulse">
                  <Cpu className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                  Running AI Matching Pipeline...
                </h3>
                <p className="text-xs text-[#77716B] dark:text-[#B9B0A5]">
                  Synthesizing skill vectors and calculating ATS benchmark scores
                </p>
              </div>

              {/* Steps Progress */}
              <div className="space-y-3">
                {steps.map((step, idx) => (
                  <div
                    key={idx}
                    className={`p-3.5 rounded-xl border transition-all duration-300 flex items-center justify-between gap-3 ${
                      idx < currentStep
                        ? 'bg-[#6B8E6B]/10 border-[#6B8E6B]/30 text-[#2F2A26] dark:text-[#F4EFE8]'
                        : idx === currentStep
                        ? 'bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/15 border-[#7C5C3B] dark:border-[#C49A6C] text-[#2F2A26] dark:text-[#F4EFE8]'
                        : 'bg-[#F7F5F0]/40 dark:bg-[#1F1D1A]/40 border-[#E7E0D8]/60 dark:border-[#413B34]/60 opacity-50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {idx < currentStep ? (
                        <CheckCircle2 className="w-4 h-4 text-[#6B8E6B] shrink-0" />
                      ) : idx === currentStep ? (
                        <span className="w-4 h-4 border-2 border-[#7C5C3B] dark:border-[#C49A6C] border-t-transparent rounded-full animate-spin shrink-0" />
                      ) : (
                        <span className="w-4 h-4 rounded-full border border-[#77716B] text-[10px] flex items-center justify-center shrink-0">
                          {idx + 1}
                        </span>
                      )}
                      <div>
                        <p className="text-xs font-semibold">{step.title}</p>
                        <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">{step.desc}</p>
                      </div>
                    </div>

                    <span className="text-[10px] font-mono font-medium text-[#77716B]">
                      {idx < currentStep ? 'Done' : idx === currentStep ? 'Processing...' : 'Waiting'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {analyzingState === 'completed' && (
            <div className="text-center py-6 space-y-3">
              <div className="w-12 h-12 rounded-full bg-[#6B8E6B]/15 text-[#6B8E6B] flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                Analysis Complete! Match Score: 82%
              </h3>
              <p className="text-xs text-[#77716B] dark:text-[#B9B0A5]">
                Redirecting to comprehensive results dashboard...
              </p>
            </div>
          )}

        </div>

      </main>

      <Footer />
      <ChatBox />
    </div>
  );
}
