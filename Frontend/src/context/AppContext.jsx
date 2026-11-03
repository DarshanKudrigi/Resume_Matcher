import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import {
  initialUser,
  sampleJobPostings,
  initialAnalysisResult,
  defaultResumeData,
  initialSavedResumes,
  initialHistory
} from '../data/mockData';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [backendOnline, setBackendOnline] = useState(false);

  // User profile
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('resumemate_user');
      return saved ? JSON.parse(saved) : initialUser;
    } catch (e) {
      return initialUser;
    }
  });

  // Current Job Description for matching
  const [currentJob, setCurrentJob] = useState(() => {
    try {
      const saved = localStorage.getItem('resumemate_current_job');
      return saved ? JSON.parse(saved) : sampleJobPostings[0];
    } catch (e) {
      return sampleJobPostings[0];
    }
  });

  // Uploaded resume file state - strictly single use, defaults to null when not uploaded
  const [uploadedFile, setUploadedFile] = useState(() => {
    try {
      const saved = localStorage.getItem('resumemate_uploaded_file');
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      return null;
    }
  });

  // Active analysis results - strictly tied to active resume session
  const [analysisResult, setAnalysisResult] = useState(() => {
    try {
      const saved = localStorage.getItem('resumemate_analysis');
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      return null;
    }
  });

  // Saved resumes in My Resumes
  const [savedResumes, setSavedResumes] = useState(() => {
    try {
      const saved = localStorage.getItem('resumemate_saved_resumes');
      return saved ? JSON.parse(saved) : initialSavedResumes;
    } catch (e) {
      return initialSavedResumes;
    }
  });

  // Analysis History
  const [history, setHistory] = useState(() => {
    try {
      const saved = localStorage.getItem('resumemate_history');
      return saved ? JSON.parse(saved) : initialHistory;
    } catch (e) {
      return initialHistory;
    }
  });

  // Active resume being edited in Builder
  const [activeResume, setActiveResume] = useState(() => {
    try {
      const saved = localStorage.getItem('resumemate_active_builder_resume');
      if (saved) {
        const parsed = JSON.parse(saved);
        // Clean out any corrupted single-word projects from previous parsing
        if (parsed?.projects && Array.isArray(parsed.projects)) {
          const stopWords = ["including", "to", "and", "or", "in", "with", "etc", "etc.", "also", "live", "browse", "vm", "vcloud", "azure", "fixed", "for", "by", "from", "on", "at", "as", "recent", "present"];
          parsed.projects = parsed.projects.filter(p => {
            const name = (p.name || "").trim().toLowerCase();
            return !stopWords.includes(name) && name.length > 2 && (p.bullets?.length > 0 || p.tech?.trim() || name.split(/\s+/).length >= 2);
          });
        }
        return parsed;
      }
    } catch (e) {}
    return defaultResumeData;
  });

  // Upload loading and error states
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  // Simple Toast notification system
  const [toast, setToast] = useState(null);

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 3500);
  }, []);

  // Check backend health & sync data on initial mount
  useEffect(() => {
    let isMounted = true;
    async function syncWithBackend() {
      try {
        const health = await api.checkHealth();
        if (health?.status === 'ok' && isMounted) {
          setBackendOnline(true);
          console.info(`[ResumeMate] Connected to FastAPI backend (${health.database})`);

          // Sync resumes from DB if available
          try {
            const dbResumes = await api.getResumes();
            if (dbResumes && dbResumes.length > 0 && isMounted) {
              setSavedResumes(dbResumes);
            }
          } catch (e) {}
        }
      } catch (e) {
        if (isMounted) {
          setBackendOnline(false);
          console.info('[ResumeMate] Running in standalone frontend mode (backend offline)');
        }
      }
    }
    syncWithBackend();
    return () => {
      isMounted = false;
    };
  }, []);

  // Sync to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('resumemate_user', JSON.stringify(user));
    } catch (e) {}
  }, [user]);

  useEffect(() => {
    try {
      localStorage.setItem('resumemate_current_job', JSON.stringify(currentJob));
    } catch (e) {}
  }, [currentJob]);

  useEffect(() => {
    try {
      if (uploadedFile) {
        localStorage.setItem('resumemate_uploaded_file', JSON.stringify(uploadedFile));
      } else {
        localStorage.removeItem('resumemate_uploaded_file');
      }
    } catch (e) {}
  }, [uploadedFile]);

  useEffect(() => {
    try {
      if (analysisResult) {
        localStorage.setItem('resumemate_analysis', JSON.stringify(analysisResult));
      } else {
        localStorage.removeItem('resumemate_analysis');
      }
    } catch (e) {}
  }, [analysisResult]);

  useEffect(() => {
    try {
      localStorage.setItem('resumemate_saved_resumes', JSON.stringify(savedResumes));
    } catch (e) {}
  }, [savedResumes]);

  useEffect(() => {
    try {
      localStorage.setItem('resumemate_history', JSON.stringify(history));
    } catch (e) {}
  }, [history]);

  useEffect(() => {
    try {
      localStorage.setItem('resumemate_active_builder_resume', JSON.stringify(activeResume));
    } catch (e) {}
  }, [activeResume]);

  // Actions
  const updateActiveResume = (updatedFields) => {
    setActiveResume((prev) => ({
      ...prev,
      ...updatedFields,
      updatedAt: "Just now"
    }));
  };

  const saveResumeFromBuilder = async (resumeData) => {
    const existingIndex = savedResumes.findIndex((r) => r.id === resumeData.id);
    let updated;
    if (existingIndex >= 0) {
      updated = savedResumes.map((r) => (r.id === resumeData.id ? { ...resumeData, updatedAt: "Just now" } : r));
      setSavedResumes(updated);
      showToast(`Resume "${resumeData.title}" updated successfully!`);
      try {
        await api.updateResume(resumeData.id, resumeData);
      } catch (e) {}
    } else {
      const newResume = {
        ...resumeData,
        id: `res-${Date.now()}`,
        updatedAt: "Just now"
      };
      updated = [newResume, ...savedResumes];
      setSavedResumes(updated);
      showToast(`New resume "${resumeData.title}" saved!`);
      try {
        await api.createResume(newResume);
      } catch (e) {}
    }
  };

  const duplicateResume = async (resumeId) => {
    const target = savedResumes.find((r) => r.id === resumeId);
    if (!target) return;
    const duplicated = {
      ...target,
      id: `res-${Date.now()}`,
      title: `${target.title} (Copy)`,
      updatedAt: "Just now"
    };
    setSavedResumes([duplicated, ...savedResumes]);
    showToast(`Duplicated "${target.title}"`);
    try {
      await api.duplicateResume(resumeId);
    } catch (e) {}
  };

  const deleteResume = async (resumeId) => {
    setSavedResumes(savedResumes.filter((r) => r.id !== resumeId));
    showToast("Resume deleted", "info");
    try {
      await api.deleteResume(resumeId);
    } catch (e) {}
  };

  const loadJobByUrl = async (url) => {
    try {
      const parsed = await api.parseJob({ url });
      if (parsed) {
        setCurrentJob(parsed);
        showToast(`Job "${parsed.title}" extracted successfully!`, "success");
        return parsed;
      }
      throw new Error("No job data returned from extraction.");
    } catch (err) {
      const errorMsg = err.message || "Failed to extract job details from URL.";
      showToast(errorMsg, "error");
      throw err;
    }
  };

  const setJobText = async (text) => {
    try {
      const parsed = await api.parseJob({ text });
      if (parsed) {
        setCurrentJob(parsed);
        showToast("Job description parsed successfully!", "success");
        return parsed;
      }
      throw new Error("No structured job data returned.");
    } catch (err) {
      const errorMsg = err.message || "Failed to parse job description text.";
      showToast(errorMsg, "error");
      throw err;
    }
  };

  const handleFileUpload = async (file) => {
    setUploadLoading(true);
    setUploadError(null);
    setAnalysisResult(null);
    try {
      localStorage.removeItem('resumemate_analysis');
    } catch (e) {}

    const initialFileData = {
      name: file.name,
      size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
      type: file.type || "application/pdf",
      uploadedAt: "Just now",
      status: "uploading"
    };
    setUploadedFile(initialFileData);
    showToast(`Uploading "${file.name}"...`, "info");

    // Call backend file parser
    try {
      const uploaded = await api.uploadResumeFile(file);
      if (uploaded) {
        const fileObj = {
          ...initialFileData,
          id: uploaded.id,
          status: uploaded.status || "ready",
          parsedData: uploaded.parsedData,
          extractedText: uploaded.extractedText,
          filePath: uploaded.filePath,
          pageCount: uploaded.pageCount || 1
        };
        setUploadedFile(fileObj);

        if (uploaded.parsedData) {
          const p = uploaded.parsedData;
          // Build a completely fresh resume object strictly from this uploaded resume
          // Never merge with previous candidate info (prev) to avoid data cross-contamination
          const freshResume = {
            id: `resume-${Date.now()}`,
            title: p.title || `${p.personalInfo?.fullName || "Candidate"}'s Resume`,
            template: "modern",
            updatedAt: "Just now",
            atsScore: p.atsScore || 85,
            personalInfo: {
              fullName: p.personalInfo?.fullName || "Candidate",
              headline: p.personalInfo?.headline || p.title || "Software Engineer",
              email: p.personalInfo?.email || "",
              phone: p.personalInfo?.phone || "",
              location: p.personalInfo?.location || "India",
              linkedin: p.personalInfo?.linkedin || "",
              github: p.personalInfo?.github || "",
              portfolio: p.personalInfo?.portfolio || ""
            },
            summary: p.summary || "",
            skills: p.skills || { languages: [], frameworks: [], tools: [], concepts: [] },
            education: Array.isArray(p.education) ? p.education : [],
            experience: Array.isArray(p.experience) ? p.experience : [],
            projects: (Array.isArray(p.projects) ? p.projects : []).filter(proj => {
              const name = (proj.name || "").trim().toLowerCase();
              const stopWords = ["including", "to", "and", "or", "in", "with", "etc", "etc.", "also", "live", "browse", "vm", "vcloud", "azure", "fixed", "for", "by", "from", "on", "at", "as", "recent", "present"];
              return !stopWords.includes(name) && name.length > 2 && (proj.bullets?.length > 0 || proj.tech?.trim() || name.split(/\s+/).length >= 2);
            }),
            certifications: Array.isArray(p.certifications) ? p.certifications : [],
            achievements: Array.isArray(p.achievements) ? p.achievements : [],
            extracted_skills: p.extracted_skills || [],
            atsBreakdown: p.atsBreakdown || null
          };

          setActiveResume(freshResume);
          try {
            localStorage.setItem('resumemate_active_builder_resume', JSON.stringify(freshResume));
          } catch (e) {}
        }

        const skillCount = uploaded.parsedData?.extracted_skills?.length || 0;
        showToast(`Parsed ${skillCount} skills from "${file.name}"!`, "success");
      }
    } catch (err) {
      console.warn("Backend parsing failed:", err.message);
      setUploadError(err.detail || err.message || "Failed to process resume file.");
      setUploadedFile((prev) => prev ? { ...prev, status: "error" } : null);
      showToast(err.detail || err.message || "Upload failed", "error");
    } finally {
      setUploadLoading(false);
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    setUploadError(null);
    setAnalysisResult(null);
    setActiveResume(defaultResumeData);

    try {
      localStorage.removeItem('resumemate_uploaded_file');
      localStorage.removeItem('resumemate_active_builder_resume');
      localStorage.removeItem('resumemate_analysis');
    } catch (e) {}

    showToast("Resume removed. All candidate session data cleared.", "info");
  };

  const triggerAnalysis = async () => {
    let result = null;
    try {
      const reqSkills = currentJob?.requiredSkills || (currentJob?.required_skills?.map(s => typeof s === 'object' ? s.name : s)) || [];
      const prefSkills = currentJob?.preferredSkills || (currentJob?.preferred_skills?.map(s => typeof s === 'object' ? s.name : s)) || [];

      // Call live FastAPI matching engine
      result = await api.analyze({
        uploadedFileId: uploadedFile?.id,
        resumeData: activeResume,
        resumeText: uploadedFile?.extractedText,
        jobId: currentJob?.id,
        jobTitle: currentJob?.title,
        company: currentJob?.company,
        jobText: currentJob?.raw_extracted_text || currentJob?.description,
        jobData: currentJob,
        requiredSkills: reqSkills,
        preferredSkills: prefSkills
      });
    } catch (e) {
      console.warn("Using offline analysis:", e.message);
    }

    if (result) {
      setAnalysisResult(result);
      const newRecord = {
        id: `hist-${Date.now()}`,
        jobTitle: result.jobTitle,
        company: result.company,
        matchScore: result.matchScore,
        atsScore: result.atsScore,
        date: "Today, " + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        dateFormatted: "Today",
        status: result.status,
        missingCount: result.missingSkills?.length || 0,
        matchedCount: result.matchedSkills?.length || 0,
        skills: result.matchedSkills || []
      };
      setHistory((prev) => [newRecord, ...prev]);
      showToast(`Analysis complete! Match score: ${result.matchScore}%`);
      return result;
    } else {
      // Local fallback
      const fallbackScore = analysisResult?.matchScore ?? 0;
      const newRecord = {
        id: `hist-${Date.now()}`,
        jobTitle: currentJob?.title || "Target Position",
        company: currentJob?.company || "Target Company",
        matchScore: fallbackScore,
        atsScore: 70,
        date: "Today, " + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        dateFormatted: "Today",
        status: fallbackScore >= 70 ? "Good Match" : "Evaluation Complete",
        missingCount: 0,
        matchedCount: 0,
        skills: []
      };
      setHistory((prev) => [newRecord, ...prev]);
      showToast(`Analysis complete! Match score: ${fallbackScore}%`);
      return null;
    }
  };

  return (
    <AppContext.Provider
      value={{
        backendOnline,
        user,
        setUser,
        currentJob,
        setCurrentJob,
        loadJobByUrl,
        setJobText,
        uploadedFile,
        handleFileUpload,
        removeFile,
        analysisResult,
        setAnalysisResult,
        triggerAnalysis,
        savedResumes,
        saveResumeFromBuilder,
        duplicateResume,
        deleteResume,
        history,
        activeResume,
        setActiveResume,
        updateActiveResume,
        uploadLoading,
        uploadError,
        toast,
        showToast
      }}
    >
      {children}
      {toast && (
        <div className="fixed bottom-5 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-4 py-2.5 rounded-lg shadow-warm-lg text-sm font-medium border transition-all duration-200 bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] border-[#E7E0D8] dark:border-[#413B34] animate-bounce-short">
          <span className={`w-2.5 h-2.5 rounded-full ${toast.type === 'error' ? 'bg-[#B96A63]' : toast.type === 'info' ? 'bg-[#C99545]' : 'bg-[#6B8E6B]'}`} />
          {toast.message}
        </div>
      )}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
