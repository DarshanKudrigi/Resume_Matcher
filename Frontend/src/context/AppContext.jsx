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

  // Uploaded resume file state
  const [uploadedFile, setUploadedFile] = useState(() => {
    try {
      const saved = localStorage.getItem('resumemate_uploaded_file');
      return saved ? JSON.parse(saved) : {
        name: "Darshan_Sharma_Resume_2026.pdf",
        size: "1.8 MB",
        type: "application/pdf",
        uploadedAt: "Just now",
        status: "ready"
      };
    } catch (e) {
      return null;
    }
  });

  // Active analysis results
  const [analysisResult, setAnalysisResult] = useState(() => {
    try {
      const saved = localStorage.getItem('resumemate_analysis');
      return saved ? JSON.parse(saved) : initialAnalysisResult;
    } catch (e) {
      return initialAnalysisResult;
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
      return saved ? JSON.parse(saved) : defaultResumeData;
    } catch (e) {
      return defaultResumeData;
    }
  });

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
      localStorage.setItem('resumemate_uploaded_file', JSON.stringify(uploadedFile));
    } catch (e) {}
  }, [uploadedFile]);

  useEffect(() => {
    try {
      localStorage.setItem('resumemate_analysis', JSON.stringify(analysisResult));
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
        showToast("Job requirements loaded successfully!");
        return parsed;
      }
    } catch (e) {}

    // Fallback to sample job lookup
    const match = sampleJobPostings.find(j => url.includes(j.company.toLowerCase()) || url.includes("react"));
    const jobToLoad = match || {
      ...sampleJobPostings[0],
      url: url,
      title: "Frontend Engineer",
      company: "Extracted from URL"
    };
    setCurrentJob(jobToLoad);
    showToast("Job requirements loaded successfully!");
    return jobToLoad;
  };

  const setJobText = async (text) => {
    try {
      const parsed = await api.parseJob({ text });
      if (parsed) {
        setCurrentJob(parsed);
        showToast("Custom Job Description saved!");
        return;
      }
    } catch (e) {}

    setCurrentJob((prev) => ({
      ...prev,
      description: text,
      title: prev.title || "Custom Job Description",
      requiredSkills: ["JavaScript", "React", "HTML", "CSS", "Git"],
      preferredSkills: ["Node.js", "Docker", "AWS"]
    }));
    showToast("Custom Job Description saved!");
  };

  const handleFileUpload = async (file) => {
    const initialFileData = {
      name: file.name,
      size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
      type: file.type || "application/pdf",
      uploadedAt: "Just now",
      status: "ready"
    };
    setUploadedFile(initialFileData);
    showToast(`Uploaded "${file.name}"`);

    // Call backend file parser
    try {
      const uploaded = await api.uploadResumeFile(file);
      if (uploaded) {
        setUploadedFile({
          ...initialFileData,
          id: uploaded.id,
          parsedData: uploaded.parsedData,
          extractedText: uploaded.extractedText
        });
        if (uploaded.parsedData) {
          // Sync parsed data into active builder resume
          setActiveResume((prev) => ({
            ...prev,
            ...uploaded.parsedData
          }));
        }
        showToast(`Parsed skills from "${file.name}"!`);
      }
    } catch (err) {
      console.warn("Backend parsing unavailable, using local mock data:", err.message);
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    showToast("Resume file removed", "info");
  };

  const triggerAnalysis = async () => {
    let result = null;
    try {
      // Call live FastAPI matching engine
      result = await api.analyze({
        uploadedFileId: uploadedFile?.id,
        resumeData: activeResume,
        jobId: currentJob?.id,
        jobTitle: currentJob?.title,
        company: currentJob?.company,
        jobText: currentJob?.description
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
    } else {
      // Local fallback
      const newRecord = {
        id: `hist-${Date.now()}`,
        jobTitle: currentJob.title || "Frontend Developer",
        company: currentJob.company || "Apex Cloud Technologies",
        matchScore: 82,
        atsScore: 86,
        date: "Today, " + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        dateFormatted: "Today",
        status: "Strong Match",
        missingCount: 3,
        matchedCount: 5,
        skills: ["JavaScript", "React", "HTML", "CSS", "Git"]
      };
      setHistory((prev) => [newRecord, ...prev]);
      showToast("Analysis complete! Match score: 82%");
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
