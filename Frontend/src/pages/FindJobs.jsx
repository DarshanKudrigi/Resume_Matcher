import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Briefcase, 
  MapPin, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  ExternalLink, 
  BookOpen, 
  Target, 
  FileText, 
  ArrowRight, 
  ChevronRight, 
  Filter, 
  SlidersHorizontal, 
  RefreshCw, 
  X,
  DollarSign,
  Calendar,
  Building2,
  Layers,
  ArrowUpDown
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ResumeUpload from '../components/ResumeUpload';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';

const QUICK_ROLES = [
  "Software Engineer",
  "Frontend Developer",
  "Full Stack Developer",
  "Backend Developer",
  "Data Analyst",
  "AI Engineer"
];

const resolveDocUrl = (rec) => {
  if (!rec) return "https://devdocs.io";
  const url = rec.docUrl || rec.url || rec.link;
  if (url && typeof url === 'string' && url !== '#' && (url.startsWith('http://') || url.startsWith('https://'))) {
    return url;
  }
  const query = encodeURIComponent(rec.skill || 'documentation');
  return `https://devdocs.io/#q=${query}`;
};

const QUICK_LOCATIONS = [
  "Bangalore, Karnataka",
  "Remote",
  "Hyderabad",
  "Mumbai",
  "Pune",
  "Delhi NCR"
];

const INITIAL_STEPS = [
  { id: 1, name: "Resume Received", key: "resume", description: "Validate candidate resume profile and initialize competencies", status: "pending", message: "" },
  { id: 2, name: "LinkedIn Search Started", key: "linkedin_start", description: "Query LinkedIn Jobs for up to 10 matching openings", status: "pending", message: "" },
  { id: 3, name: "LinkedIn Search Completed", key: "linkedin_complete", description: "Parse and sanitize discovered LinkedIn postings", status: "pending", message: "" },
  { id: 4, name: "Naukri Search Started", key: "naukri_start", description: "Query Naukri for up to 10 matching openings", status: "pending", message: "" },
  { id: 5, name: "Naukri Search Completed", key: "naukri_complete", description: "Extract job descriptions and qualifications from Naukri", status: "pending", message: "" },
  { id: 6, name: "Groq AI Matching Started", key: "matching_start", description: "Evaluate resume competencies using Groq AI Llama 3.3", status: "pending", message: "" },
  { id: 7, name: "Job Results Processed", key: "processing_complete", description: "Score, rank, and extract matched/missing skill gaps", status: "pending", message: "" },
  { id: 8, name: "Google Sheets Updated", key: "sheets_complete", description: "Log qualifying opportunities to Google Sheets Tracker", status: "pending", message: "" },
  { id: 9, name: "Search Completed", key: "search_completed", description: "Compile final opportunities and render matched cards", status: "pending", message: "" },
];

export default function FindJobs() {
  const { uploadedFile, activeResume, handleFileUpload, setCurrentJob, showToast } = useApp();

  // Search parameters
  const [desiredRole, setDesiredRole] = useState("Software Engineer");
  const [location, setLocation] = useState("Bangalore, Karnataka");
  const [includeLinkedIn, setIncludeLinkedIn] = useState(true);
  const [includeNaukri, setIncludeNaukri] = useState(true);

  // Search execution & progress states
  const [isSearching, setIsSearching] = useState(false);
  const [progressSteps, setProgressSteps] = useState(INITIAL_STEPS);
  const [searchResults, setSearchResults] = useState(null);
  const [searchError, setSearchError] = useState(null);

  // Active platform tab: 'all' | 'linkedin' | 'naukri'
  const [activeTab, setActiveTab] = useState('all');

  // Client-side Filters & Sorting
  const [minMatchFilter, setMinMatchFilter] = useState(0); // 0, 40, 60, 80
  const [companyFilter, setCompanyFilter] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [sortBy, setSortBy] = useState('match'); // 'match' | 'latest'

  // Modal detailed view state
  const [selectedJobModal, setSelectedJobModal] = useState(null);

  // Candidate resume reference
  const candidateName = activeResume?.personalInfo?.fullName || uploadedFile?.name || "Target Resume Profile";

  const handleStartSearch = async (e) => {
    if (e) e.preventDefault();
    if (!desiredRole.trim()) {
      showToast("Please enter a desired job role", "error");
      return;
    }
    if (!location.trim()) {
      showToast("Please enter a preferred location", "error");
      return;
    }

    const platforms = [];
    if (includeLinkedIn) platforms.push("linkedin");
    if (includeNaukri) platforms.push("naukri");

    if (platforms.length === 0) {
      showToast("Please select at least one platform (LinkedIn or Naukri)", "error");
      return;
    }

    // Reset progress steps
    const freshSteps = INITIAL_STEPS.map(s => ({
      ...s,
      status: s.id === 1 ? "processing" : "pending",
      message: s.id === 1 ? "Validating candidate resume and extracting competencies..." : ""
    }));
    setProgressSteps(freshSteps);
    setIsSearching(true);
    setSearchError(null);
    setSearchResults(null);

    const payload = {
      desired_role: desiredRole.trim(),
      location: location.trim(),
      platforms,
      limit: 10, // up to 10 per platform (max 20 total)
      resume_data: activeResume || {},
      resume_text: uploadedFile?.extractedText || "",
      uploaded_file_id: uploadedFile?.id || null
    };

    try {
      await api.streamJobRecommendations(
        payload,
        // On each real-time backend event
        (event) => {
          handleStreamEvent(event);
        },
        // On stream error
        (err) => {
          console.error("Stream connection error:", err);
          setSearchError(err.message || "Failed to complete job search.");
          setIsSearching(false);
          showToast("Search process encountered an issue", "error");
        }
      );
    } catch (err) {
      console.error("Job search error:", err);
      setSearchError(err.message || "Network error while searching jobs.");
      setIsSearching(false);
      showToast("Search failed. Please check backend connection.", "error");
    }
  };

  const handleStreamEvent = (event) => {
    const { step, type, status, message, data } = event;

    setProgressSteps(prevSteps => {
      return prevSteps.map(s => {
        if (s.id === step) {
          return {
            ...s,
            status,
            message: message || s.message,
            data: data || s.data
          };
        }
        // If current step is completed, set next step to processing (if still pending)
        if (s.id === step + 1 && status === 'completed' && s.status === 'pending') {
          return {
            ...s,
            status: 'processing'
          };
        }
        return s;
      });
    });

    // When step 9 completes (or search_completed event received), finalize results
    if ((step === 9 || type === 'search_completed') && data) {
      setSearchResults(data);
      setIsSearching(false);
      if (status === 'completed') {
        showToast(`Search completed! Found ${data.total_found || 0} job opportunities.`, "success");
      } else {
        showToast(message || "Search completed with warnings.", "info");
      }
    }
  };

  // Filter and sort the fetched results in-memory
  const filteredJobs = useMemo(() => {
    if (!searchResults?.jobs) return [];
    let list = [...searchResults.jobs];

    // Platform Tab Filter
    if (activeTab === 'linkedin') {
      list = list.filter(j => j.source?.toLowerCase().includes('linkedin'));
    } else if (activeTab === 'naukri') {
      list = list.filter(j => j.source?.toLowerCase().includes('naukri'));
    }

    // Match percentage filter
    if (minMatchFilter > 0) {
      list = list.filter(j => (j.matchScore || 0) >= minMatchFilter);
    }

    // Company filter
    if (companyFilter.trim()) {
      const q = companyFilter.toLowerCase().trim();
      list = list.filter(j => (j.company || '').toLowerCase().includes(q));
    }

    // Location filter
    if (locationFilter.trim()) {
      const q = locationFilter.toLowerCase().trim();
      list = list.filter(j => (j.location || '').toLowerCase().includes(q));
    }

    // Sorting
    if (sortBy === 'match') {
      list.sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
    } else if (sortBy === 'latest') {
      list.sort((a, b) => new Date(b.scraped_at || 0) - new Date(a.scraped_at || 0));
    }

    return list;
  }, [searchResults, activeTab, minMatchFilter, companyFilter, locationFilter, sortBy]);

  // Counts for tabs
  const linkedinCount = searchResults?.jobs?.filter(j => j.source?.toLowerCase().includes('linkedin')).length || 0;
  const naukriCount = searchResults?.jobs?.filter(j => j.source?.toLowerCase().includes('naukri')).length || 0;
  const totalCount = searchResults?.jobs?.length || 0;

  const handleSelectAsTarget = (job) => {
    const jobData = {
      id: job.id,
      title: job.title,
      company: job.company,
      location: job.location,
      url: job.url,
      description: job.description || `${job.title} at ${job.company}`,
      requiredSkills: job.matchedSkills?.concat(job.missingSkills || []) || [],
      preferredSkills: job.matchedPreferredSkills?.concat(job.missingPreferredSkills || []) || [],
      source: job.source,
      scraped_at: job.scraped_at
    };
    setCurrentJob(jobData);
    showToast(`"${job.title}" set as active target job for Analyzer!`, "success");
    setSelectedJobModal(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#2F2A26] dark:text-[#F4EFE8] transition-colors">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
        
        {/* Page Header */}
        <div className="pb-3 border-b border-[#E7E0D8]/80 dark:border-[#413B34]/80 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="p-1.5 rounded-lg bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/15 text-[#7C5C3B] dark:text-[#C49A6C]">
                <Search className="w-4 h-4" />
              </span>
              <span className="text-xs font-semibold text-[#7C5C3B] dark:text-[#C49A6C] uppercase tracking-wider">
                Automated Job Discovery
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#6B8E6B]/15 text-[#6B8E6B] font-bold">
                Playwright + AI Scraper
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-[#2F2A26] dark:text-[#F4EFE8]">
              Find Jobs for Me
            </h1>
            <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5] mt-1">
              Search real-time job openings on LinkedIn & Naukri (up to 10 each, max 20) and match against your resume.
            </p>
          </div>

          {/* Active Target Resume Card */}
          <div className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-xs">
            <FileText className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C] shrink-0" />
            <div className="flex flex-col text-xs">
              <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5] uppercase font-bold tracking-wider">
                Active Resume:
              </span>
              <span className="font-semibold text-[#2F2A26] dark:text-[#F4EFE8] truncate max-w-[200px]" title={candidateName}>
                {candidateName}
              </span>
            </div>
            {uploadedFile ? (
              <span className="w-2.5 h-2.5 rounded-full bg-[#6B8E6B] shrink-0" title="Uploaded Resume Verified" />
            ) : (
              <span className="w-2.5 h-2.5 rounded-full bg-[#C99545] shrink-0" title="Template Profile Active" />
            )}
          </div>
        </div>

        {/* Top Grid: Resume Upload & Extracted Sections (Left) & Job Search Parameters (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          {/* Resume Upload Card with Parsed Skills & Section Counters */}
          <ResumeUpload readyText="Ready to match against job openings" />

          {/* Job Search Criteria Card */}
          <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 sm:p-6 shadow-warm-sm transition-colors duration-200 space-y-5">
            {/* Card Header matching ResumeUpload */}
            <div className="flex items-center justify-between pb-4 border-b border-[#E7E0D8] dark:border-[#413B34]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] flex items-center justify-center text-[#7C5C3B] dark:text-[#C49A6C]">
                  <Search className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-base sm:text-lg font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                    Job Search Criteria
                  </h2>
                  <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5]">
                    Discover top matching openings on LinkedIn & Naukri
                  </p>
                </div>
              </div>
              <span className="text-[11px] font-semibold text-[#7C5C3B] dark:text-[#C49A6C] px-2.5 py-1 rounded-full bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/15 border border-[#7C5C3B]/20 dark:border-[#C49A6C]/30">
                Top 10 Each
              </span>
            </div>

            <form onSubmit={handleStartSearch} className="space-y-4">
              <div className="space-y-4">
                
                {/* Desired Job Role */}
                <div className="space-y-2">
                  <label className="block text-xs font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5]">
                    Desired Job Role
                  </label>
                  <div className="relative">
                    <Briefcase className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#77716B] dark:text-[#B9B0A5]" />
                    <input
                      type="text"
                      value={desiredRole}
                      onChange={(e) => setDesiredRole(e.target.value)}
                      placeholder="e.g. Software Engineer, React Developer"
                      disabled={isSearching}
                      className="w-full pl-10 pr-3 py-2.5 text-xs rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/40 dark:bg-[#1F1D1A]/40 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:ring-1 focus:ring-[#7C5C3B] dark:focus:ring-[#C49A6C] disabled:opacity-50"
                    />
                  </div>
                  {/* Quick Roles */}
                  <div className="flex flex-wrap gap-1.5 pt-0.5">
                    {QUICK_ROLES.map((r) => (
                      <button
                        key={r}
                        type="button"
                        disabled={isSearching}
                        onClick={() => setDesiredRole(r)}
                        className={`text-[10px] px-2.5 py-0.5 rounded-md border transition-colors ${
                          desiredRole === r
                            ? 'bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] border-transparent font-semibold'
                            : 'border-[#E7E0D8] dark:border-[#413B34] text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]'
                        }`}
                      >
                        {r}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Preferred Location */}
                <div className="space-y-2">
                  <label className="block text-xs font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5]">
                    Preferred Location
                  </label>
                  <div className="relative">
                    <MapPin className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#77716B] dark:text-[#B9B0A5]" />
                    <input
                      type="text"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      placeholder="e.g. Bengaluru, Remote, Hyderabad"
                      disabled={isSearching}
                      className="w-full pl-10 pr-3 py-2.5 text-xs rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/40 dark:bg-[#1F1D1A]/40 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:ring-1 focus:ring-[#7C5C3B] dark:focus:ring-[#C49A6C] disabled:opacity-50"
                    />
                  </div>
                  {/* Quick Locations */}
                  <div className="flex flex-wrap gap-1.5 pt-0.5">
                    {QUICK_LOCATIONS.map((loc) => (
                      <button
                        key={loc}
                        type="button"
                        disabled={isSearching}
                        onClick={() => setLocation(loc)}
                        className={`text-[10px] px-2.5 py-0.5 rounded-md border transition-colors ${
                          location === loc
                            ? 'bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] border-transparent font-semibold'
                            : 'border-[#E7E0D8] dark:border-[#413B34] text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]'
                        }`}
                      >
                        {loc}
                      </button>
                    ))}
                  </div>
                </div>

              </div>

              {/* Bottom Bar: Platform Selection & Search Button */}
              <div className="flex flex-wrap items-center justify-between gap-4 pt-3 border-t border-[#E7E0D8]/80 dark:border-[#413B34]/80">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5]">
                    Platforms:
                  </span>

                  <label className="flex items-center gap-1.5 text-xs font-medium cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={includeLinkedIn}
                      disabled={isSearching}
                      onChange={(e) => setIncludeLinkedIn(e.target.checked)}
                      className="rounded border-[#E7E0D8] text-[#0A66C2] focus:ring-[#0A66C2]"
                    />
                    <span className="px-2 py-0.5 rounded bg-[#0A66C2]/10 text-[#0A66C2] font-semibold text-[11px]">
                      LinkedIn
                    </span>
                  </label>

                  <label className="flex items-center gap-1.5 text-xs font-medium cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={includeNaukri}
                      disabled={isSearching}
                      onChange={(e) => setIncludeNaukri(e.target.checked)}
                      className="rounded border-[#E7E0D8] text-[#FF7555] focus:ring-[#FF7555]"
                    />
                    <span className="px-2 py-0.5 rounded bg-[#FF7555]/10 text-[#E0502E] dark:text-[#FF8D73] font-semibold text-[11px]">
                      Naukri
                    </span>
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={isSearching}
                  className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] dark:hover:bg-[#B38757] text-xs sm:text-sm font-bold shadow-warm-sm transition-all duration-200 flex items-center justify-center gap-2.5 disabled:opacity-50"
                >
                  {isSearching ? (
                    <>
                      <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      <span>Executing Search...</span>
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      <span>Search Jobs for Me</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Live Search Progress Timeline (Section 3 & 4) */}
        {isSearching && (
          <div className="rounded-2xl border border-[#7C5C3B]/30 dark:border-[#C49A6C]/30 bg-[#FFFFFF] dark:bg-[#292622] p-6 sm:p-7 shadow-warm-md space-y-5 animate-fadeIn">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#E7E0D8] dark:border-[#413B34]">
              <div>
                <h3 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8] flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#7C5C3B] dark:bg-[#C49A6C] animate-ping" />
                  Live Backend Processing Timeline
                </h3>
                <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] mt-0.5">
                  Real-time events streamed directly from FastAPI Playwright scraping & resume matcher
                </p>
              </div>

              <span className="text-xs font-semibold px-3 py-1 rounded-full bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/15 text-[#7C5C3B] dark:text-[#C49A6C]">
                Connected via SSE Stream
              </span>
            </div>

            {/* 6-Step Visual Timeline */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5 pt-1">
              {progressSteps.map((step) => {
                const isCompleted = step.status === 'completed';
                const isProcessing = step.status === 'processing';
                const isError = step.status === 'error';

                return (
                  <div
                    key={step.id}
                    className={`p-3.5 rounded-xl border transition-all duration-200 ${
                      isProcessing
                        ? 'border-[#7C5C3B] dark:border-[#C49A6C] bg-[#7C5C3B]/5 dark:bg-[#C49A6C]/5 shadow-warm-xs'
                        : isCompleted
                        ? 'border-[#6B8E6B]/30 bg-[#6B8E6B]/5'
                        : isError
                        ? 'border-[#C99545]/40 bg-[#C99545]/5'
                        : 'border-[#E7E0D8] dark:border-[#413B34] opacity-50 bg-[#F7F5F0]/20 dark:bg-[#1F1D1A]/20'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className={`w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center ${
                          isCompleted
                            ? 'bg-[#6B8E6B] text-[#F7F5F0]'
                            : isProcessing
                            ? 'bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] animate-pulse'
                            : isError
                            ? 'bg-[#C99545] text-[#F7F5F0]'
                            : 'bg-[#E7E0D8] dark:bg-[#413B34] text-[#77716B]'
                        }`}>
                          {isCompleted ? '✓' : step.id}
                        </span>
                        <h4 className="text-xs font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                          {step.name}
                        </h4>
                      </div>

                      {isProcessing && (
                        <span className="w-3.5 h-3.5 border-2 border-[#7C5C3B] dark:border-[#C49A6C] border-t-transparent rounded-full animate-spin" />
                      )}
                      {isCompleted && (
                        <CheckCircle2 className="w-4 h-4 text-[#6B8E6B]" />
                      )}
                      {isError && (
                        <AlertCircle className="w-4 h-4 text-[#C99545]" />
                      )}
                    </div>

                    <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5] leading-relaxed">
                      {step.message || step.description}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Search Error Notice */}
        {searchError && (
          <div className="p-4 rounded-xl border border-[#B96A63]/30 bg-[#B96A63]/10 text-[#B96A63] text-xs flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <div className="space-y-0.5">
              <p className="font-bold">Search Encountered an Error</p>
              <p>{searchError}</p>
            </div>
          </div>
        )}

        {/* Search Results Area */}
        {searchResults && (
          <div className="space-y-6 animate-fadeIn">
            
            {/* Results Header: Tabs & Filter Bar */}
            <div className="rounded-2xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 shadow-warm-sm space-y-4">
              
              {/* Platform Tabs */}
              <div className="flex flex-wrap items-center justify-between gap-4 pb-3 border-b border-[#E7E0D8] dark:border-[#413B34]">
                <div className="flex items-center gap-2 p-1 rounded-xl bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34]">
                  <button
                    type="button"
                    onClick={() => setActiveTab('all')}
                    className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5 ${
                      activeTab === 'all'
                        ? 'bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A]'
                        : 'text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]'
                    }`}
                  >
                    <span>All Opportunities</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-black/10 dark:bg-white/10">
                      {totalCount}
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab('linkedin')}
                    className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5 ${
                      activeTab === 'linkedin'
                        ? 'bg-[#0A66C2] text-[#FFFFFF]'
                        : 'text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]'
                    }`}
                  >
                    <span>LinkedIn</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-white/20">
                      {linkedinCount}
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab('naukri')}
                    className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5 ${
                      activeTab === 'naukri'
                        ? 'bg-[#FF7555] text-[#FFFFFF]'
                        : 'text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]'
                    }`}
                  >
                    <span>Naukri</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-white/20">
                      {naukriCount}
                    </span>
                  </button>
                </div>

                {/* Spreadsheet status */}
                {searchResults.spreadsheet_status && (
                  <div className="flex items-center gap-1.5 text-xs text-[#6B8E6B] font-semibold bg-[#6B8E6B]/10 px-3 py-1.5 rounded-lg border border-[#6B8E6B]/20">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{searchResults.spreadsheet_status}</span>
                  </div>
                )}
              </div>

              {/* Client-side Filters & Sort */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                
                {/* Minimum Match Filter */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5]">
                    Match Threshold
                  </label>
                  <select
                    value={minMatchFilter}
                    onChange={(e) => setMinMatchFilter(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none"
                  >
                    <option value={0}>All Matches (0%+)</option>
                    <option value={40}>40%+ Match</option>
                    <option value={60}>60%+ Match</option>
                    <option value={80}>80%+ Strong Match</option>
                  </select>
                </div>

                {/* Company Search Filter */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5]">
                    Filter Company
                  </label>
                  <div className="relative">
                    <Building2 className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-[#77716B]" />
                    <input
                      type="text"
                      value={companyFilter}
                      onChange={(e) => setCompanyFilter(e.target.value)}
                      placeholder="e.g. Google, Amazon"
                      className="w-full pl-9 pr-3 py-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none"
                    />
                  </div>
                </div>

                {/* Location Filter */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5]">
                    Filter Location
                  </label>
                  <div className="relative">
                    <MapPin className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-[#77716B]" />
                    <input
                      type="text"
                      value={locationFilter}
                      onChange={(e) => setLocationFilter(e.target.value)}
                      placeholder="e.g. Remote, Bengaluru"
                      className="w-full pl-9 pr-3 py-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none"
                    />
                  </div>
                </div>

                {/* Sort By */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5]">
                    Sort Order
                  </label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none"
                  >
                    <option value="match">Highest Match % First</option>
                    <option value="latest">Latest Discovered</option>
                  </select>
                </div>

              </div>

            </div>

            {/* Job Cards Grid */}
            {filteredJobs.length === 0 ? (
              <div className="p-10 text-center rounded-2xl border border-dashed border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-xs text-[#77716B] dark:text-[#B9B0A5] space-y-2">
                <p className="text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                  No job openings match the selected filters.
                </p>
                <p>
                  Try clearing the company/location search or lowering the match threshold.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredJobs.map((job) => {
                  const isLinkedIn = job.source?.toLowerCase().includes("linkedin");
                  const matchPct = job.matchScore || 0;

                  return (
                    <div
                      key={job.id}
                      className="p-5 rounded-2xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] hover:border-[#7C5C3B]/50 dark:hover:border-[#C49A6C]/50 hover:shadow-warm-md transition-all flex flex-col justify-between space-y-4"
                    >
                      {/* Top Info */}
                      <div className="space-y-2.5">
                        <div className="flex items-start justify-between gap-3">
                          <div className="space-y-1">
                            <h4 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8] leading-snug">
                              {job.title}
                            </h4>
                            <div className="flex flex-wrap items-center gap-x-2.5 gap-y-1 text-xs text-[#77716B] dark:text-[#B9B0A5]">
                              <span className="font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                                {job.company}
                              </span>
                              <span>•</span>
                              <span className="flex items-center gap-1">
                                <MapPin className="w-3 h-3 text-[#7C5C3B] dark:text-[#C49A6C]" />
                                {job.location}
                              </span>
                            </div>
                          </div>

                          {/* Match Badge */}
                          <div className={`px-3 py-1.5 rounded-xl text-xs font-extrabold flex items-center gap-1.5 shrink-0 ${
                            matchPct >= 80
                              ? 'bg-[#6B8E6B]/15 text-[#6B8E6B] border border-[#6B8E6B]/30'
                              : matchPct >= 60
                              ? 'bg-[#C99545]/15 text-[#C99545] border border-[#C99545]/30'
                              : 'bg-[#B96A63]/15 text-[#B96A63] border border-[#B96A63]/30'
                          }`}>
                            <Sparkles className="w-3 h-3" />
                            <span>{matchPct}% Match</span>
                          </div>
                        </div>

                        {/* Metadata Pills: Platform, Recommendation, Experience, Salary */}
                        <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
                          <span className={`font-bold px-2.5 py-0.5 rounded-full ${
                            isLinkedIn
                              ? 'bg-[#0A66C2]/15 text-[#0A66C2]'
                              : 'bg-[#FF7555]/15 text-[#E0502E] dark:text-[#FF8D73]'
                          }`}>
                            {isLinkedIn ? "LinkedIn" : "Naukri"}
                          </span>

                          {job.recommendation && (
                            <span className={`font-bold px-2.5 py-0.5 rounded-md border ${
                              job.recommendation === 'apply'
                                ? 'bg-[#6B8E6B]/15 text-[#6B8E6B] border-[#6B8E6B]/30'
                                : job.recommendation === 'maybe'
                                ? 'bg-[#C99545]/15 text-[#C99545] border-[#C99545]/30'
                                : 'bg-[#77716B]/15 text-[#77716B] dark:text-[#B9B0A5] border-[#77716B]/30'
                            }`}>
                              {job.recommendation === 'apply' ? '★ Highly Recommended' : job.recommendation === 'maybe' ? '? Potential Fit' : '✕ Lower Fit'}
                            </span>
                          )}

                          {job.experience && job.experience !== "Not specified" && (
                            <span className="px-2 py-0.5 rounded-md bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#77716B] dark:text-[#B9B0A5] border border-[#E7E0D8] dark:border-[#413B34]">
                              Exp: {job.experience}
                            </span>
                          )}

                          {job.salary && job.salary !== "Not disclosed" && (
                            <span className="px-2 py-0.5 rounded-md bg-[#6B8E6B]/10 text-[#6B8E6B] font-medium border border-[#6B8E6B]/20">
                              {job.salary}
                            </span>
                          )}
                        </div>

                        {/* Groq AI Assessment Reason */}
                        {job.reason && (
                          <div className="p-2.5 rounded-xl bg-[#F7F5F0]/70 dark:bg-[#1F1D1A]/70 border border-[#E7E0D8] dark:border-[#413B34] text-xs text-[#5B554E] dark:text-[#D5CEC5]">
                            <span className="font-semibold text-[#7C5C3B] dark:text-[#C49A6C]">AI Analysis: </span>
                            <span>{job.reason}</span>
                          </div>
                        )}

                        {/* Short Description */}
                        {job.description && (
                          <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] line-clamp-2 leading-relaxed">
                            {job.description}
                          </p>
                        )}

                        {/* Matched & Missing Skills Preview */}
                        <div className="space-y-1.5 pt-1">
                          {job.matchedSkills?.length > 0 && (
                            <div className="flex flex-wrap items-center gap-1 text-[11px]">
                              <span className="font-bold text-[#6B8E6B] mr-1">Matched:</span>
                              {job.matchedSkills.slice(0, 4).map((s, idx) => (
                                <span key={idx} className="px-2 py-0.5 rounded-md bg-[#6B8E6B]/10 text-[#6B8E6B] font-semibold border border-[#6B8E6B]/20">
                                  ✓ {s}
                                </span>
                              ))}
                              {job.matchedSkills.length > 4 && (
                                <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5]">
                                  +{job.matchedSkills.length - 4} more
                                </span>
                              )}
                            </div>
                          )}

                          {job.missingSkills?.length > 0 && (
                            <div className="flex flex-wrap items-center gap-1 text-[11px]">
                              <span className="font-bold text-[#C99545] mr-1">Missing:</span>
                              {job.missingSkills.slice(0, 3).map((s, idx) => (
                                <span key={idx} className="px-2 py-0.5 rounded-md bg-[#C99545]/10 text-[#C99545] font-semibold border border-[#C99545]/20">
                                  • {s}
                                </span>
                              ))}
                              {job.missingSkills.length > 3 && (
                                <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5]">
                                  +{job.missingSkills.length - 3} more
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Card Actions: View Job & Apply Link */}
                      <div className="flex items-center justify-between gap-2 pt-3 border-t border-[#E7E0D8]/70 dark:border-[#413B34]/70">
                        <button
                          type="button"
                          onClick={() => setSelectedJobModal(job)}
                          className="px-3.5 py-2 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 hover:bg-[#F7F5F0] dark:hover:bg-[#1F1D1A] text-xs font-bold text-[#7C5C3B] dark:text-[#C49A6C] transition-colors flex items-center gap-1.5"
                        >
                          <BookOpen className="w-3.5 h-3.5" />
                          <span>View Job Details</span>
                        </button>

                        {job.url && (
                          <a
                            href={job.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3.5 py-2 rounded-xl bg-[#2F2A26] dark:bg-[#F4EFE8] text-[#F7F5F0] dark:text-[#1F1D1A] hover:opacity-90 text-xs font-bold shadow-warm-xs transition-opacity flex items-center gap-1.5"
                          >
                            <span>Apply / View Original</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

      </main>

      {/* Detailed Job Information Modal (Section 5) */}
      {selectedJobModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-2xl max-h-[90vh] flex flex-col rounded-2xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-lg overflow-hidden">
            
            {/* Modal Header */}
            <div className="flex items-start justify-between p-5 sm:p-6 border-b border-[#E7E0D8] dark:border-[#413B34]">
              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-lg font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                    {selectedJobModal.title}
                  </h3>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    selectedJobModal.source?.toLowerCase().includes("linkedin")
                      ? 'bg-[#0A66C2]/15 text-[#0A66C2]'
                      : 'bg-[#FF7555]/15 text-[#E0502E] dark:text-[#FF8D73]'
                  }`}>
                    {selectedJobModal.source?.toLowerCase().includes("linkedin") ? "LinkedIn" : "Naukri"}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-x-2 text-xs text-[#77716B] dark:text-[#B9B0A5]">
                  <span className="font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                    {selectedJobModal.company}
                  </span>
                  <span>•</span>
                  <span>{selectedJobModal.location}</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setSelectedJobModal(null)}
                className="p-1.5 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] text-[#77716B] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Scrollable Body */}
            <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-5 text-xs">
              
              {/* Match Score & Summary */}
              <div className="p-4 rounded-xl border border-[#7C5C3B]/20 dark:border-[#C49A6C]/20 bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 flex items-center justify-between gap-4">
                <div className="space-y-0.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#7C5C3B] dark:text-[#C49A6C]">
                    Candidate Match Score
                  </span>
                  <p className="font-bold text-sm text-[#2F2A26] dark:text-[#F4EFE8]">
                    {selectedJobModal.status || "Evaluated Match"}
                  </p>
                  <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
                    Scored against {candidateName}
                  </p>
                </div>
                <div className="text-2xl font-black text-[#7C5C3B] dark:text-[#C49A6C]">
                  {selectedJobModal.matchScore}%
                </div>
              </div>

              {/* Skills Analysis */}
              <div className="space-y-3">
                <h4 className="font-bold text-sm text-[#2F2A26] dark:text-[#F4EFE8]">
                  Skill Alignment Breakdown
                </h4>

                {/* Matched Skills */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-bold text-[#6B8E6B] flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Matching Skills ({selectedJobModal.matchedSkills?.length || 0}):
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedJobModal.matchedSkills?.map((s, idx) => (
                      <span key={idx} className="px-2.5 py-1 rounded-md bg-[#6B8E6B]/10 text-[#6B8E6B] font-semibold border border-[#6B8E6B]/20">
                        ✓ {s}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Missing Skills */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-bold text-[#C99545] flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5" />
                    Missing Skills ({selectedJobModal.missingSkills?.length || 0}):
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedJobModal.missingSkills?.map((s, idx) => (
                      <span key={idx} className="px-2.5 py-1 rounded-md bg-[#C99545]/10 text-[#C99545] font-semibold border border-[#C99545]/20">
                        • {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Official Documentation Learning Resources (New tab verified) */}
              {selectedJobModal.learningRecommendations?.length > 0 && (
                <div className="space-y-2.5 pt-2">
                  <h4 className="font-bold text-sm text-[#2F2A26] dark:text-[#F4EFE8] flex items-center gap-1.5">
                    <BookOpen className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C]" />
                    Official Documentation Learning Roadmaps
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {selectedJobModal.learningRecommendations.map((rec, i) => {
                      const safeDocUrl = resolveDocUrl(rec);
                      return (
                        <a
                          key={i}
                          href={safeDocUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-3 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/40 dark:bg-[#1F1D1A]/40 hover:border-[#7C5C3B] dark:hover:border-[#C49A6C] transition-colors flex items-center justify-between group"
                        >
                          <div className="space-y-0.5">
                            <span className="font-bold text-xs text-[#2F2A26] dark:text-[#F4EFE8]">
                              {rec.skill}
                            </span>
                            <p className="text-[10px] text-[#77716B] dark:text-[#B9B0A5] line-clamp-1">
                              {rec.sourceName || "Official Documentation Guide"}
                            </p>
                          </div>
                          <ExternalLink className="w-3.5 h-3.5 text-[#77716B] group-hover:text-[#7C5C3B] dark:group-hover:text-[#C49A6C] shrink-0 ml-2" />
                        </a>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Full Job Description */}
              <div className="space-y-1.5 pt-2">
                <h4 className="font-bold text-sm text-[#2F2A26] dark:text-[#F4EFE8]">
                  Job Description & Overview
                </h4>
                <div className="p-4 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/30 dark:bg-[#1F1D1A]/30 text-xs leading-relaxed text-[#2F2A26]/90 dark:text-[#F4EFE8]/90 whitespace-pre-line max-h-52 overflow-y-auto">
                  {selectedJobModal.description || "No full job description provided by platform."}
                </div>
              </div>

            </div>

            {/* Modal Footer Actions */}
            <div className="p-4 sm:p-5 border-t border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 flex flex-wrap items-center justify-between gap-3">
              <button
                type="button"
                onClick={() => handleSelectAsTarget(selectedJobModal)}
                className="px-4 py-2.5 rounded-xl border border-[#7C5C3B]/30 dark:border-[#C49A6C]/30 bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/10 text-[#7C5C3B] dark:text-[#C49A6C] hover:bg-[#7C5C3B]/20 text-xs font-bold transition-colors flex items-center gap-1.5"
              >
                <Target className="w-3.5 h-3.5" />
                <span>Set as Active Job for Analyzer</span>
              </button>

              {selectedJobModal.url && (
                <a
                  href={selectedJobModal.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-5 py-2.5 rounded-xl bg-[#2F2A26] dark:bg-[#F4EFE8] text-[#F7F5F0] dark:text-[#1F1D1A] hover:opacity-90 text-xs font-bold shadow-warm-sm transition-opacity flex items-center gap-1.5"
                >
                  <span>Apply on Original Posting</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>

          </div>
        </div>
      )}

      <Footer />
    </div>
  );
}

