import React, { useState } from 'react';
import { 
  Briefcase, 
  Link as LinkIcon, 
  CheckCircle, 
  Sparkles, 
  ArrowRight, 
  MapPin, 
  Clock, 
  GraduationCap,
  AlertTriangle, 
  RotateCcw, 
  ChevronDown, 
  ChevronUp, 
  Globe, 
  HelpCircle,
  FileText,
  Edit3
} from 'lucide-react';
import { useApp } from '../context/AppContext';

export default function JobDescriptionCard({ className = "" }) {
  const { currentJob, loadJobByUrl, setJobText, showToast } = useApp();
  
  const [activeTab, setActiveTab] = useState('url'); // 'url' | 'text'
  const [urlInput, setUrlInput] = useState(currentJob?.url || "");
  const [textInput, setTextInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [errorMsg, setErrorMsg] = useState(null);
  const [showFullDesc, setShowFullDesc] = useState(false);
  const [showDetails, setShowDetails] = useState(true);

  const loadingMessages = [
    "Identifying platform and validating URL...",
    "Extracting page content...",
    "Consulting Gemini AI to classify skills...",
    "Finalizing structured requirements..."
  ];

  const handleExtractJob = async (e) => {
    if (e) e.preventDefault();
    const targetUrl = urlInput.trim();
    if (!targetUrl) {
      showToast("Please enter a job URL", "info");
      return;
    }

    setIsLoading(true);
    setErrorMsg(null);
    setLoadingStep(0);

    const interval = setInterval(() => {
      setLoadingStep((prev) => (prev < loadingMessages.length - 1 ? prev + 1 : prev));
    }, 2200);

    try {
      await loadJobByUrl(targetUrl);
      setErrorMsg(null);
    } catch (err) {
      const msg = err.message || "Failed to extract job posting. Please verify the URL or paste manually.";
      setErrorMsg(msg);
    } finally {
      clearInterval(interval);
      setIsLoading(false);
      setLoadingStep(0);
    }
  };

  const handleParseText = async (e) => {
    if (e) e.preventDefault();
    const targetText = textInput.trim();
    if (!targetText || targetText.length < 30) {
      showToast("Please paste at least 30 characters of job description", "info");
      return;
    }

    setIsLoading(true);
    setErrorMsg(null);
    setLoadingStep(2); // AI structuring step

    try {
      await setJobText(targetText);
      setErrorMsg(null);
    } catch (err) {
      const msg = err.message || "Failed to parse job description text.";
      setErrorMsg(msg);
    } finally {
      setIsLoading(false);
      setLoadingStep(0);
    }
  };

  // Helper to extract skill name and metadata whether object or string
  const formatSkill = (item) => {
    if (typeof item === 'object' && item !== null) {
      return {
        name: item.name || '',
        evidence: item.evidence || '',
        category: item.category || ''
      };
    }
    return { name: String(item), evidence: '', category: '' };
  };

  const rawReq = currentJob?.required_skills || currentJob?.requiredSkills || [];
  const rawPref = currentJob?.preferred_skills || currentJob?.preferredSkills || [];
  const rawAdd = currentJob?.additional_mentioned_skills || currentJob?.unclassifiedSkills || [];

  const requiredSkills = rawReq.map(formatSkill).filter(s => s.name);
  const preferredSkills = rawPref.map(formatSkill).filter(s => s.name);
  const additionalSkills = rawAdd.map(formatSkill).filter(s => s.name);

  const unavailableFields = currentJob?.unavailableFields || [];
  const warnings = currentJob?.warnings || [];
  const responsibilities = currentJob?.responsibilities || [];
  const qualifications = currentJob?.qualifications || [];
  const expReqs = currentJob?.experience_requirements || [];
  const eduReqs = currentJob?.education_requirements || [];

  return (
    <div className={`rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 sm:p-6 shadow-warm-sm transition-colors duration-200 ${className}`}>
      
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-[#E7E0D8] dark:border-[#413B34]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] flex items-center justify-center text-[#7C5C3B] dark:text-[#C49A6C]">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Target Job Posting
            </h2>
            <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5]">
              AI-assisted extraction from URL or pasted text
            </p>
          </div>
        </div>

        {currentJob?.source_platform || currentJob?.source ? (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/20 text-[#7C5C3B] dark:text-[#C49A6C] border border-[#7C5C3B]/20 dark:border-[#C49A6C]/30">
            <Globe className="w-3 h-3" />
            {currentJob.source_platform || currentJob.source}
          </span>
        ) : null}
      </div>

      {/* Mode Switcher Tabs */}
      <div className="flex items-center gap-2 mt-4 p-1 rounded-lg bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8]/60 dark:border-[#413B34]/60">
        <button
          type="button"
          onClick={() => { setActiveTab('url'); setErrorMsg(null); }}
          className={`flex-1 py-1.5 px-3 rounded-md text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
            activeTab === 'url'
              ? 'bg-[#FFFFFF] dark:bg-[#292622] text-[#7C5C3B] dark:text-[#C49A6C] shadow-warm-sm'
              : 'text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26]'
          }`}
        >
          <LinkIcon className="w-3.5 h-3.5" />
          <span>Job URL</span>
        </button>
        <button
          type="button"
          onClick={() => { setActiveTab('text'); setErrorMsg(null); }}
          className={`flex-1 py-1.5 px-3 rounded-md text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
            activeTab === 'text'
              ? 'bg-[#FFFFFF] dark:bg-[#292622] text-[#7C5C3B] dark:text-[#C49A6C] shadow-warm-sm'
              : 'text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26]'
          }`}
        >
          <Edit3 className="w-3.5 h-3.5" />
          <span>Paste Job Description</span>
        </button>
      </div>

      {/* URL Tab Content */}
      {activeTab === 'url' && (
        <form onSubmit={handleExtractJob} className="mt-3 space-y-3">
          <div className="flex flex-col sm:flex-row gap-2.5">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#77716B]">
                <LinkIcon className="w-4 h-4" />
              </div>
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="e.g. Amazon, Lever, Microsoft, LinkedIn, or Naukri URL"
                disabled={isLoading}
                className="w-full pl-9 pr-3.5 py-2.5 text-xs sm:text-sm rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/70 text-[#2F2A26] dark:text-[#F4EFE8] placeholder-[#77716B]/60 focus:outline-none focus:ring-2 focus:ring-[#7C5C3B]/20 dark:focus:ring-[#C49A6C]/20 focus:border-[#7C5C3B] dark:focus:border-[#C49A6C] transition-all disabled:opacity-60"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="px-5 py-2.5 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] dark:hover:bg-[#B38757] text-xs sm:text-sm font-semibold transition-all shadow-warm-sm flex items-center justify-center gap-2 shrink-0 disabled:opacity-50"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  <span>Extracting...</span>
                </span>
              ) : (
                <>
                  <span>Extract Job</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>

          <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
            Supports LinkedIn, Naukri, Amazon Jobs, Lever, Microsoft, and general company career pages.
          </p>
        </form>
      )}

      {/* Manual Text Tab Content */}
      {activeTab === 'text' && (
        <form onSubmit={handleParseText} className="mt-3 space-y-3">
          <div className="relative">
            <textarea
              rows={4}
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste the target job description text here (responsibilities, required qualifications, nice-to-haves)..."
              disabled={isLoading}
              className="w-full p-3 text-xs sm:text-sm rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/70 text-[#2F2A26] dark:text-[#F4EFE8] placeholder-[#77716B]/60 focus:outline-none focus:ring-2 focus:ring-[#7C5C3B]/20 dark:focus:ring-[#C49A6C]/20 focus:border-[#7C5C3B] dark:focus:border-[#C49A6C] transition-all disabled:opacity-60 resize-y"
            />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
              {textInput.length > 0 ? `${textInput.length} characters` : 'Paste any JD text to parse skills directly.'}
            </span>
            <button
              type="submit"
              disabled={isLoading || textInput.trim().length < 30}
              className="px-5 py-2 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] dark:hover:bg-[#B38757] text-xs sm:text-sm font-semibold transition-all shadow-warm-sm flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  <span>Structuring...</span>
                </span>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 text-[#D8A48F] dark:text-[#1F1D1A]" />
                  <span>Parse with AI</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}

      {/* Progress Feedback */}
      {isLoading && (
        <div className="mt-3 p-3 rounded-lg bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#7C5C3B]/20 dark:border-[#C49A6C]/30 flex items-center gap-3 animate-pulse">
          <span className="w-4 h-4 border-2 border-[#7C5C3B] dark:border-[#C49A6C] border-t-transparent rounded-full animate-spin shrink-0" />
          <span className="text-xs font-medium text-[#7C5C3B] dark:text-[#C49A6C]">
            {loadingMessages[loadingStep]}
          </span>
        </div>
      )}

      {/* Error Banner with Quick Fallback Action */}
      {errorMsg && (
        <div className="mt-4 p-4 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 text-red-800 dark:text-red-200 space-y-2.5">
          <div className="flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
            <div className="flex-1 text-xs">
              <p className="font-bold">Extraction Blocked or Incomplete</p>
              <p className="mt-0.5 text-red-700 dark:text-red-300">{errorMsg}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 pt-1 border-t border-red-200/60 dark:border-red-900/40">
            <button
              type="button"
              onClick={() => { setActiveTab('text'); setErrorMsg(null); }}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] text-xs font-semibold hover:opacity-90 transition-opacity"
            >
              <FileText className="w-3 h-3" />
              <span>Paste Job Description Manually</span>
            </button>
            {activeTab === 'url' && (
              <button
                type="button"
                onClick={handleExtractJob}
                disabled={isLoading}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-red-100 dark:bg-red-900/60 hover:bg-red-200 dark:hover:bg-red-800 text-xs font-semibold text-red-900 dark:text-red-100 transition-colors"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Retry</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Active Extracted Job Details */}
      {currentJob && (
        <div className="mt-5 space-y-4">
          
          {/* Main Job Card */}
          <div className="p-4 rounded-xl bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] space-y-2.5">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <h3 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                  {currentJob.title || "Untitled Position"}
                </h3>
                <p className="text-xs font-semibold text-[#7C5C3B] dark:text-[#C49A6C] mt-0.5">
                  {currentJob.company || "Company not specified"}
                </p>
              </div>

              {(currentJob.extraction_status || currentJob.status) && (
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                  (currentJob.extraction_status || currentJob.status) === 'success'
                    ? 'bg-[#6B8E6B]/15 text-[#6B8E6B]'
                    : 'bg-[#C99545]/15 text-[#C99545]'
                }`}>
                  {(currentJob.extraction_status || currentJob.status) === 'success' ? 'Structured with AI' : 'Partial Extraction'}
                </span>
              )}
            </div>

            {/* Badges metadata */}
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-[#77716B] dark:text-[#B9B0A5] pt-1 border-t border-[#E7E0D8]/60 dark:border-[#413B34]/60">
              {currentJob.location ? (
                <span className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-[#7C5C3B] dark:text-[#C49A6C]" />
                  <span>{currentJob.location}</span>
                </span>
              ) : (
                <span className="text-[11px] italic opacity-60">Location not specified</span>
              )}

              {currentJob.experience ? (
                <span className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-[#7C5C3B] dark:text-[#C49A6C]" />
                  <span>{currentJob.experience}</span>
                </span>
              ) : null}

              {(currentJob.employment_type || currentJob.employmentType) ? (
                <span className="px-2 py-0.5 rounded bg-[#FFFFFF] dark:bg-[#292622] border border-[#E7E0D8] dark:border-[#413B34] text-[11px] font-medium">
                  {currentJob.employment_type || currentJob.employmentType}
                </span>
              ) : null}
            </div>

            {/* Summary description preview if structured */}
            {currentJob.description_summary && (
              <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] leading-relaxed pt-1 border-t border-[#E7E0D8]/40 dark:border-[#413B34]/40">
                {currentJob.description_summary}
              </p>
            )}

            {/* Experience / Education details if extracted */}
            {(expReqs.length > 0 || eduReqs.length > 0) && (
              <div className="pt-2 border-t border-[#E7E0D8]/40 dark:border-[#413B34]/40 space-y-1.5 text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
                {expReqs.length > 0 && (
                  <div className="flex items-start gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-[#7C5C3B] dark:text-[#C49A6C] shrink-0 mt-0.5" />
                    <span><strong>Experience:</strong> {expReqs.join("; ")}</span>
                  </div>
                )}
                {eduReqs.length > 0 && (
                  <div className="flex items-start gap-1.5">
                    <GraduationCap className="w-3.5 h-3.5 text-[#7C5C3B] dark:text-[#C49A6C] shrink-0 mt-0.5" />
                    <span><strong>Education:</strong> {eduReqs.join("; ")}</span>
                  </div>
                )}
              </div>
            )}

            {/* Unavailable fields notice */}
            {unavailableFields.length > 0 && (
              <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5] pt-1">
                <span className="font-semibold text-amber-600 dark:text-amber-400">Notice:</span> Some fields ({unavailableFields.join(", ")}) could not be extracted automatically.
              </p>
            )}
          </div>

          {/* Extracted Skills Section */}
          <div className="pt-2 space-y-4">
            
            {/* Header with counts */}
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5] flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-[#7C5C3B] dark:text-[#C49A6C]" />
                Technical Competencies
              </span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#6B8E6B]/15 text-[#6B8E6B] font-semibold">
                {requiredSkills.length} Required • {preferredSkills.length} Preferred
              </span>
            </div>

            {/* Required Skills */}
            <div>
              <span className="text-xs font-bold text-[#2F2A26] dark:text-[#F4EFE8] block mb-2">
                Required Qualifications:
              </span>
              {requiredSkills.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {requiredSkills.map((skill) => (
                    <span
                      key={skill.name}
                      title={skill.evidence ? `Evidence: ${skill.evidence}` : ''}
                      className="group relative inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] border border-[#E7E0D8] dark:border-[#413B34] shadow-warm-sm"
                    >
                      <CheckCircle className="w-3 h-3 text-[#6B8E6B]" />
                      <span>{skill.name}</span>
                      {skill.category && (
                        <span className="text-[10px] opacity-60">({skill.category})</span>
                      )}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs italic text-[#77716B]">No required skills explicitly demarcated.</p>
              )}
            </div>

            {/* Preferred Skills */}
            <div>
              <span className="text-xs font-bold text-[#77716B] dark:text-[#B9B0A5] block mb-2">
                Preferred / Nice-to-Have:
              </span>
              {preferredSkills.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {preferredSkills.map((skill) => (
                    <span
                      key={skill.name}
                      title={skill.evidence ? `Evidence: ${skill.evidence}` : ''}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-[#F7F5F0]/80 dark:bg-[#1F1D1A]/80 text-[#77716B] dark:text-[#B9B0A5] border border-[#E7E0D8]/60 dark:border-[#413B34]/60"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-[#C99545]" />
                      <span>{skill.name}</span>
                      {skill.category && (
                        <span className="text-[10px] opacity-60">({skill.category})</span>
                      )}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs italic text-[#77716B]">No preferred skills explicitly listed.</p>
              )}
            </div>

            {/* Additional Mentioned Skills */}
            {additionalSkills.length > 0 && (
              <div>
                <span className="text-xs font-bold text-[#77716B] dark:text-[#B9B0A5] block mb-2 flex items-center gap-1">
                  <HelpCircle className="w-3 h-3" />
                  Additional Mentioned Skills:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {additionalSkills.map((skill) => (
                    <span
                      key={skill.name}
                      title={skill.evidence ? `Evidence: ${skill.evidence}` : ''}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-transparent text-[#77716B] border border-dashed border-[#E7E0D8] dark:border-[#413B34]"
                    >
                      <span>{skill.name}</span>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Structured Responsibilities & Qualifications (Collapsible) */}
            {(responsibilities.length > 0 || qualifications.length > 0) && (
              <div className="pt-2 border-t border-[#E7E0D8]/60 dark:border-[#413B34]/60">
                <button
                  type="button"
                  onClick={() => setShowDetails(!showDetails)}
                  className="w-full flex items-center justify-between py-2 text-xs font-bold text-[#7C5C3B] dark:text-[#C49A6C] hover:opacity-80 transition-opacity"
                >
                  <span>Key Responsibilities & Qualifications</span>
                  {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>

                {showDetails && (
                  <div className="mt-2 space-y-3 text-xs text-[#2F2A26] dark:text-[#F4EFE8]">
                    {responsibilities.length > 0 && (
                      <div>
                        <p className="font-semibold text-[#77716B] dark:text-[#B9B0A5] mb-1">Responsibilities:</p>
                        <ul className="list-disc pl-4 space-y-1 text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
                          {responsibilities.slice(0, 6).map((r, i) => (
                            <li key={i}>{r}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {qualifications.length > 0 && (
                      <div>
                        <p className="font-semibold text-[#77716B] dark:text-[#B9B0A5] mb-1">Qualifications:</p>
                        <ul className="list-disc pl-4 space-y-1 text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
                          {qualifications.slice(0, 6).map((q, i) => (
                            <li key={i}>{q}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Full Job Description Preview Toggle */}
            {(currentJob.raw_extracted_text || currentJob.description) && (
              <div className="pt-2 border-t border-[#E7E0D8]/60 dark:border-[#413B34]/60">
                <button
                  type="button"
                  onClick={() => setShowFullDesc(!showFullDesc)}
                  className="text-xs font-semibold text-[#7C5C3B] dark:text-[#C49A6C] hover:underline flex items-center gap-1"
                >
                  <span>{showFullDesc ? "Hide Full Description" : "View Full Extracted Description"}</span>
                  {showFullDesc ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </button>
                {showFullDesc && (
                  <div className="mt-2 p-3 rounded-lg bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 border border-[#E7E0D8]/60 dark:border-[#413B34]/60 text-[11px] text-[#77716B] dark:text-[#B9B0A5] max-h-60 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                    {currentJob.raw_extracted_text || currentJob.description}
                  </div>
                )}
              </div>
            )}

          </div>

        </div>
      )}

    </div>
  );
}
