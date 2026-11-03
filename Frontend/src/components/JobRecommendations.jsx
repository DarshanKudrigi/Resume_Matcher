import React, { useState } from 'react';
import { 
  Briefcase, 
  MapPin, 
  Search, 
  Sparkles, 
  ExternalLink, 
  CheckCircle2, 
  AlertCircle, 
  BookOpen, 
  Target, 
  Check, 
  FileText,
  Clock,
  Layers,
  ChevronDown,
  ChevronUp,
  Table
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';

const QUICK_ROLES = [
  "Software Engineer",
  "Frontend Developer",
  "Full Stack Developer",
  "Backend Developer",
  "Data Analyst"
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
  "Bengaluru",
  "Remote",
  "Hyderabad",
  "Mumbai",
  "Pune"
];

export default function JobRecommendations() {
  const { uploadedFile, activeResume, setCurrentJob, showToast } = useApp();

  const [desiredRole, setDesiredRole] = useState("Software Engineer");
  const [location, setLocation] = useState("Bengaluru");
  const [includeLinkedIn, setIncludeLinkedIn] = useState(true);
  const [includeNaukri, setIncludeNaukri] = useState(true);
  
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [expandedDocsJobId, setExpandedDocsJobId] = useState(null);

  const handleSearch = async (e) => {
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
      showToast("Please select at least one search platform (LinkedIn or Naukri)", "error");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        desired_role: desiredRole.trim(),
        location: location.trim(),
        platforms,
        limit: 8,
        resume_data: activeResume || {},
        resume_text: uploadedFile?.extractedText || "",
        uploaded_file_id: uploadedFile?.id || null
      };

      const response = await api.searchJobRecommendations(payload);
      setResults(response);
      showToast(`Found ${response.total_found || 0} job recommendations!`, "success");
    } catch (err) {
      console.error("Job recommendations error:", err);
      setError(err.message || "Failed to search job recommendations. Please try again.");
      showToast("Job recommendation search failed", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectJob = (job) => {
    const jobData = {
      id: job.id,
      title: job.title,
      company: job.company,
      location: job.location,
      url: job.url,
      description: job.description || `${job.title} at ${job.company}`,
      requiredSkills: job.matchedSkills.concat(job.missingSkills),
      preferredSkills: job.matchedPreferredSkills.concat(job.missingPreferredSkills),
      source: job.source,
      scraped_at: job.scraped_at
    };
    setCurrentJob(jobData);
    showToast(`"${job.title}" set as active target job for analyzer!`, "success");
  };

  const toggleDocs = (jobId) => {
    setExpandedDocsJobId(expandedDocsJobId === jobId ? null : jobId);
  };

  const candidateName = activeResume?.personalInfo?.fullName || uploadedFile?.name || "Uploaded Resume";

  return (
    <div className="rounded-2xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-6 sm:p-7 shadow-warm-sm space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#E7E0D8] dark:border-[#413B34]">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/15 text-[#7C5C3B] dark:text-[#C49A6C]">
              <Sparkles className="w-4 h-4" />
            </span>
            <h3 className="text-xl font-bold tracking-tight text-[#2F2A26] dark:text-[#F4EFE8]">
              Find Jobs for Me
            </h3>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#6B8E6B]/15 text-[#6B8E6B]">
              AI Scraper & Matcher
            </span>
          </div>
          <p className="text-xs text-[#77716B] dark:text-[#B9B0A5]">
            Search real-time openings across LinkedIn and Naukri tailored to your resume, role, and preferred city.
          </p>
        </div>

        {/* Active Resume Status Badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 text-xs">
          <FileText className="w-3.5 h-3.5 text-[#7C5C3B] dark:text-[#C49A6C]" />
          <span className="text-[#77716B] dark:text-[#B9B0A5]">Target Resume:</span>
          <span className="font-semibold text-[#2F2A26] dark:text-[#F4EFE8] truncate max-w-[160px]" title={candidateName}>
            {candidateName}
          </span>
          {uploadedFile ? (
            <span className="w-2 h-2 rounded-full bg-[#6B8E6B]" title="Uploaded Resume Active" />
          ) : (
            <span className="w-2 h-2 rounded-full bg-[#C99545]" title="Template Profile Active" />
          )}
        </div>
      </div>

      {/* Search Criteria Form */}
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
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
                className="w-full pl-10 pr-3 py-2.5 text-xs rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/40 dark:bg-[#1F1D1A]/40 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:ring-1 focus:ring-[#7C5C3B] dark:focus:ring-[#C49A6C]"
              />
            </div>
            {/* Quick Suggestions */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              {QUICK_ROLES.map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setDesiredRole(r)}
                  className={`text-[10px] px-2 py-0.5 rounded-md border transition-colors ${
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
                className="w-full pl-10 pr-3 py-2.5 text-xs rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/40 dark:bg-[#1F1D1A]/40 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:ring-1 focus:ring-[#7C5C3B] dark:focus:ring-[#C49A6C]"
              />
            </div>
            {/* Quick Suggestions */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              {QUICK_LOCATIONS.map((loc) => (
                <button
                  key={loc}
                  type="button"
                  onClick={() => setLocation(loc)}
                  className={`text-[10px] px-2 py-0.5 rounded-md border transition-colors ${
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

        {/* Platform Selection & Submit Action */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
          <div className="flex items-center gap-3">
            <span className="text-xs font-medium text-[#77716B] dark:text-[#B9B0A5]">
              Platforms:
            </span>
            
            <label className="flex items-center gap-1.5 text-xs font-medium cursor-pointer select-none">
              <input
                type="checkbox"
                checked={includeLinkedIn}
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
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] dark:hover:bg-[#B38757] text-xs font-bold shadow-warm-sm transition-all duration-200 flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                <span>Scraping & Matching Jobs...</span>
              </>
            ) : (
              <>
                <Search className="w-3.5 h-3.5" />
                <span>Search Jobs for Me</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Error Notice */}
      {error && (
        <div className="p-3.5 rounded-xl border border-[#B96A63]/30 bg-[#B96A63]/10 text-[#B96A63] text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Warnings & Diagnostics Banner */}
      {results?.warnings?.length > 0 && (
        <div className="p-3 rounded-xl border border-[#C99545]/30 bg-[#C99545]/10 text-[#C99545] text-xs space-y-1">
          {results.warnings.map((w, idx) => (
            <div key={idx} className="flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5 shrink-0" />
              <span>{w}</span>
            </div>
          ))}
        </div>
      )}

      {/* Spreadsheet Tracking Status Banner */}
      {results?.spreadsheet_status && (
        <div className="flex items-center justify-between px-3.5 py-2 rounded-xl border border-[#6B8E6B]/30 bg-[#6B8E6B]/10 text-[#6B8E6B] text-xs">
          <span className="flex items-center gap-1.5 font-medium">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{results.spreadsheet_status}</span>
          </span>
          <span className="text-[11px] opacity-80 flex items-center gap-1">
            <Table className="w-3 h-3" /> Auto-tracked without duplicates
          </span>
        </div>
      )}

      {/* Results List */}
      {results && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5]">
              Recommended Openings ({results.jobs?.length || 0})
            </h4>
            <span className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
              Sorted by highest resume match
            </span>
          </div>

          {results.jobs?.length === 0 ? (
            <div className="p-8 text-center rounded-xl border border-dashed border-[#E7E0D8] dark:border-[#413B34] text-xs text-[#77716B] dark:text-[#B9B0A5] space-y-2">
              <p className="font-semibold text-sm text-[#2F2A26] dark:text-[#F4EFE8]">
                No jobs matched the current criteria.
              </p>
              <p>
                Try broadening the role (e.g. "Software Engineer" or "Developer") or checking both LinkedIn and Naukri.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3.5">
              {results.jobs.map((job) => {
                const isLinkedIn = job.source?.toLowerCase().includes("linkedin");
                const isExpanded = expandedDocsJobId === job.id;
                const matchPct = job.matchScore || 0;

                return (
                  <div 
                    key={job.id}
                    className="p-4 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/30 dark:bg-[#1F1D1A]/30 hover:border-[#7C5C3B]/40 dark:hover:border-[#C49A6C]/40 transition-all space-y-3"
                  >
                    {/* Header Row: Title, Company, Location, Match Score & Platform */}
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <h5 className="text-sm sm:text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                            {job.title}
                          </h5>
                          
                          {/* Platform Badge */}
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            isLinkedIn 
                              ? 'bg-[#0A66C2]/15 text-[#0A66C2]' 
                              : 'bg-[#FF7555]/15 text-[#E0502E] dark:text-[#FF8D73]'
                          }`}>
                            {isLinkedIn ? "LinkedIn" : "Naukri"}
                          </span>
                        </div>

                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[#77716B] dark:text-[#B9B0A5]">
                          <span className="font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                            {job.company}
                          </span>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <MapPin className="w-3 h-3 text-[#7C5C3B] dark:text-[#C49A6C]" />
                            {job.location}
                          </span>
                          {job.scraped_at && (
                            <>
                              <span>•</span>
                              <span className="flex items-center gap-1 text-[11px]">
                                <Clock className="w-3 h-3" />
                                {new Date(job.scraped_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                              </span>
                            </>
                          )}
                        </div>
                      </div>

                      {/* Match Score Badge */}
                      <div className="flex sm:flex-col items-center sm:items-end justify-between gap-1 shrink-0">
                        <div className={`px-3 py-1 rounded-xl text-xs font-extrabold flex items-center gap-1.5 shadow-warm-xs ${
                          matchPct >= 70
                            ? 'bg-[#6B8E6B]/15 text-[#6B8E6B] border border-[#6B8E6B]/30'
                            : matchPct >= 50
                            ? 'bg-[#C99545]/15 text-[#C99545] border border-[#C99545]/30'
                            : 'bg-[#B96A63]/15 text-[#B96A63] border border-[#B96A63]/30'
                        }`}>
                          <Sparkles className="w-3 h-3" />
                          <span>{matchPct}% Match</span>
                        </div>
                        <span className="text-[10px] font-semibold text-[#77716B] dark:text-[#B9B0A5]">
                          {job.status}
                        </span>
                      </div>
                    </div>

                    {/* Skill Breakdown Badges */}
                    <div className="space-y-1.5 pt-1">
                      {/* Matched Skills */}
                      {job.matchedSkills?.length > 0 && (
                        <div className="flex flex-wrap items-center gap-1 text-xs">
                          <span className="text-[10px] font-bold text-[#6B8E6B] mr-1">
                            Matched:
                          </span>
                          {job.matchedSkills.slice(0, 6).map((skill, idx) => (
                            <span 
                              key={idx}
                              className="px-2 py-0.5 rounded-md bg-[#6B8E6B]/10 text-[#6B8E6B] text-[10px] font-semibold border border-[#6B8E6B]/20"
                            >
                              ✓ {skill}
                            </span>
                          ))}
                          {job.matchedSkills.length > 6 && (
                            <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5]">
                              +{job.matchedSkills.length - 6} more
                            </span>
                          )}
                        </div>
                      )}

                      {/* Missing Required Skills */}
                      {job.missingSkills?.length > 0 && (
                        <div className="flex flex-wrap items-center gap-1 text-xs">
                          <span className="text-[10px] font-bold text-[#C99545] mr-1">
                            Missing Skills:
                          </span>
                          {job.missingSkills.slice(0, 5).map((skill, idx) => (
                            <span 
                              key={idx}
                              className="px-2 py-0.5 rounded-md bg-[#C99545]/10 text-[#C99545] text-[10px] font-semibold border border-[#C99545]/20"
                            >
                              • {skill}
                            </span>
                          ))}
                          {job.missingSkills.length > 5 && (
                            <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5]">
                              +{job.missingSkills.length - 5} more
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Action Bar */}
                    <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-[#E7E0D8]/60 dark:border-[#413B34]/60">
                      <div className="flex flex-wrap items-center gap-2">
                        {/* Official Documentation Toggle */}
                        {job.learningRecommendations?.length > 0 && (
                          <button
                            type="button"
                            onClick={() => toggleDocs(job.id)}
                            className="px-2.5 py-1.5 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] hover:bg-[#F7F5F0] dark:hover:bg-[#1F1D1A] text-[11px] font-semibold text-[#7C5C3B] dark:text-[#C49A6C] transition-colors flex items-center gap-1"
                          >
                            <BookOpen className="w-3 h-3" />
                            <span>Official Docs ({job.learningRecommendations.length})</span>
                            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                          </button>
                        )}

                        {/* Set as Target Job for In-depth Analyzer */}
                        <button
                          type="button"
                          onClick={() => handleSelectJob(job)}
                          className="px-2.5 py-1.5 rounded-lg border border-[#7C5C3B]/30 dark:border-[#C49A6C]/30 bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/10 text-[#7C5C3B] dark:text-[#C49A6C] hover:bg-[#7C5C3B]/20 dark:hover:bg-[#C49A6C]/20 text-[11px] font-bold transition-colors flex items-center gap-1"
                        >
                          <Target className="w-3 h-3" />
                          <span>Set as Target Job</span>
                        </button>
                      </div>

                      {/* View Original Job Posting (External Link with new tab) */}
                      {job.url && (
                        <a
                          href={job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-3 py-1.5 rounded-lg bg-[#2F2A26] dark:bg-[#F4EFE8] text-[#F7F5F0] dark:text-[#1F1D1A] hover:opacity-90 text-[11px] font-bold shadow-warm-xs transition-opacity flex items-center gap-1.5"
                        >
                          <span>Open Posting</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>

                    {/* Expanded Official Learning Documentation Section */}
                    {isExpanded && job.learningRecommendations?.length > 0 && (
                      <div className="mt-3 p-3.5 rounded-xl border border-[#7C5C3B]/20 dark:border-[#C49A6C]/20 bg-[#FFFFFF] dark:bg-[#292622] space-y-2.5 animate-fadeIn">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-[#7C5C3B] dark:text-[#C49A6C] flex items-center gap-1.5">
                            <BookOpen className="w-3.5 h-3.5" />
                            <span>Recommended Documentation for Missing Skills:</span>
                          </span>
                          <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5]">
                            Links open official doc portals in new tab
                          </span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {job.learningRecommendations.map((rec, i) => {
                            const safeDocUrl = resolveDocUrl(rec);
                            return (
                              <a
                                key={i}
                                href={safeDocUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="p-2.5 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 hover:border-[#7C5C3B] dark:hover:border-[#C49A6C] transition-colors flex items-center justify-between group"
                              >
                                <div className="space-y-0.5">
                                  <div className="flex items-center gap-1.5">
                                    <span className="text-xs font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                                      {rec.skill}
                                    </span>
                                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#7C5C3B]/10 text-[#7C5C3B] dark:text-[#C49A6C] font-semibold">
                                      Official
                                    </span>
                                  </div>
                                  <p className="text-[10px] text-[#77716B] dark:text-[#B9B0A5] line-clamp-1">
                                    {rec.topic || rec.sourceName || "Official Documentation & API Guide"}
                                  </p>
                                </div>
                                <ExternalLink className="w-3.5 h-3.5 text-[#77716B] group-hover:text-[#7C5C3B] dark:group-hover:text-[#C49A6C] shrink-0 ml-2" />
                              </a>
                            );
                          })}
                        </div>
                      </div>
                    )}

                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

    </div>
  );
}

