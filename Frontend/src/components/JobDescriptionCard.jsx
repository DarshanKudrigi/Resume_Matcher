import React, { useState } from 'react';
import { Briefcase, Link as LinkIcon, FileText, CheckCircle, Sparkles, ArrowRight, MapPin } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { sampleJobPostings } from '../data/mockData';

export default function JobDescriptionCard({ className = "" }) {
  const { currentJob, loadJobByUrl, setJobText, showToast } = useApp();
  const [activeTab, setActiveTab] = useState('url'); // 'url' | 'paste'
  const [urlInput, setUrlInput] = useState(currentJob?.url || "https://careers.apexcloud.io/jobs/frontend-engineer-react");
  const [textInput, setTextInput] = useState(currentJob?.description || "");
  const [isLoading, setIsLoading] = useState(false);

  const handleLoadJob = (e) => {
    e.preventDefault();
    if (!urlInput.trim()) {
      showToast("Please enter a job URL", "info");
      return;
    }
    setIsLoading(true);
    setTimeout(() => {
      loadJobByUrl(urlInput);
      setIsLoading(false);
    }, 450);
  };

  const handleUseDescription = (e) => {
    e.preventDefault();
    if (!textInput.trim()) {
      showToast("Please paste or type a job description", "info");
      return;
    }
    setIsLoading(true);
    setTimeout(() => {
      setJobText(textInput);
      setIsLoading(false);
    }, 450);
  };

  const handleQuickSample = (sample) => {
    setUrlInput(sample.url);
    setTextInput(sample.description);
    loadJobByUrl(sample.url);
  };

  return (
    <div className={`rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 sm:p-6 shadow-warm-sm transition-colors duration-200 ${className}`}>
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#E7E0D8] dark:border-[#413B34]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] flex items-center justify-center text-[#7C5C3B] dark:text-[#C49A6C]">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Job Description
            </h2>
            <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5]">
              Add the job you want to apply for.
            </p>
          </div>
        </div>

        {/* Quick Sample Selector for Demo */}
        <div className="flex items-center gap-1.5 self-start sm:self-auto">
          <span className="text-[11px] font-medium text-[#77716B] dark:text-[#B9B0A5] hidden sm:inline">
            Quick Demos:
          </span>
          {sampleJobPostings.map((sample, idx) => (
            <button
              key={sample.id}
              type="button"
              onClick={() => handleQuickSample(sample)}
              className={`text-xs px-2.5 py-1 rounded-md border font-medium transition-colors ${
                currentJob?.id === sample.id
                  ? 'bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] border-transparent'
                  : 'bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#77716B] dark:text-[#B9B0A5] border-[#E7E0D8] dark:border-[#413B34] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]'
              }`}
            >
              Demo {idx + 1}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 mt-4 mb-4 border-b border-[#E7E0D8] dark:border-[#413B34]">
        <button
          type="button"
          onClick={() => setActiveTab('url')}
          className={`flex items-center gap-2 pb-2.5 px-3 text-xs sm:text-sm font-semibold border-b-2 transition-colors ${
            activeTab === 'url'
              ? 'border-[#7C5C3B] dark:border-[#C49A6C] text-[#7C5C3B] dark:text-[#C49A6C]'
              : 'border-transparent text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]'
          }`}
        >
          <LinkIcon className="w-3.5 h-3.5" />
          <span>Job URL</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('paste')}
          className={`flex items-center gap-2 pb-2.5 px-3 text-xs sm:text-sm font-semibold border-b-2 transition-colors ${
            activeTab === 'paste'
              ? 'border-[#7C5C3B] dark:border-[#C49A6C] text-[#7C5C3B] dark:text-[#C49A6C]'
              : 'border-transparent text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Paste Description</span>
        </button>
      </div>

      {/* Tab 1: Job URL Input */}
      {activeTab === 'url' && (
        <form onSubmit={handleLoadJob} className="space-y-3">
          <div className="flex flex-col sm:flex-row gap-2.5">
            <div className="relative flex-1">
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="Paste job posting URL"
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/70 text-[#2F2A26] dark:text-[#F4EFE8] placeholder-[#77716B]/60 focus:outline-none focus:ring-2 focus:ring-[#7C5C3B]/20 dark:focus:ring-[#C49A6C]/20 focus:border-[#7C5C3B] dark:focus:border-[#C49A6C] transition-all"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="px-5 py-2.5 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] dark:hover:bg-[#B38757] text-xs sm:text-sm font-semibold transition-all shadow-warm-sm flex items-center justify-center gap-2 shrink-0 disabled:opacity-50"
            >
              {isLoading ? (
                <span>Loading...</span>
              ) : (
                <>
                  <span>Load Job</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
          <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
            Paste any LinkedIn, Indeed, or company careers link to auto-extract skills.
          </p>
        </form>
      )}

      {/* Tab 2: Paste Description */}
      {activeTab === 'paste' && (
        <form onSubmit={handleUseDescription} className="space-y-3">
          <textarea
            rows={4}
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Paste job description here..."
            className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/70 text-[#2F2A26] dark:text-[#F4EFE8] placeholder-[#77716B]/60 focus:outline-none focus:ring-2 focus:ring-[#7C5C3B]/20 dark:focus:ring-[#C49A6C]/20 focus:border-[#7C5C3B] dark:focus:border-[#C49A6C] transition-all resize-none"
          />
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isLoading}
              className="px-5 py-2 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] dark:hover:bg-[#B38757] text-xs sm:text-sm font-semibold transition-all shadow-warm-sm flex items-center gap-2 disabled:opacity-50"
            >
              {isLoading ? <span>Processing...</span> : <span>Use Job Description</span>}
            </button>
          </div>
        </form>
      )}

      {/* Active Job Details Badge */}
      {currentJob && (
        <div className="mt-4 p-3.5 rounded-lg bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] text-xs">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="font-bold text-[#2F2A26] dark:text-[#F4EFE8] text-sm">
                {currentJob.title}
              </span>
              <span className="text-[#77716B] dark:text-[#B9B0A5]">•</span>
              <span className="font-medium text-[#7C5C3B] dark:text-[#C49A6C]">
                {currentJob.company}
              </span>
            </div>
            {currentJob.location && (
              <span className="text-[11px] text-[#77716B] dark:text-[#B9B0A5] flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                {currentJob.location}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Extracted Mock Requirements Section */}
      <div className="mt-5 pt-4 border-t border-[#E7E0D8] dark:border-[#413B34] space-y-3.5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5] flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-[#7C5C3B] dark:text-[#C49A6C]" />
            Extracted Requirements
          </span>
          <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#6B8E6B]/15 text-[#6B8E6B] font-medium">
            5 Required • 3 Preferred
          </span>
        </div>

        {/* Required Skills */}
        <div>
          <span className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] block mb-2">
            Required Skills:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {currentJob?.requiredSkills?.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] border border-[#E7E0D8] dark:border-[#413B34] shadow-warm-sm"
              >
                <CheckCircle className="w-3 h-3 text-[#6B8E6B]" />
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Preferred Skills */}
        <div>
          <span className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5] block mb-2">
            Preferred Skills:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {currentJob?.preferredSkills?.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-[#F7F5F0]/80 dark:bg-[#1F1D1A]/80 text-[#77716B] dark:text-[#B9B0A5] border border-[#E7E0D8]/60 dark:border-[#413B34]/60"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-[#C99545]" />
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
}
