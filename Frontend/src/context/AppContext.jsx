import React, { createContext, useContext, useState, useEffect } from 'react';
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

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 3500);
  };

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

  const saveResumeFromBuilder = (resumeData) => {
    const existingIndex = savedResumes.findIndex((r) => r.id === resumeData.id);
    let updated;
    if (existingIndex >= 0) {
      updated = savedResumes.map((r) => (r.id === resumeData.id ? { ...resumeData, updatedAt: "Just now" } : r));
      showToast(`Resume "${resumeData.title}" updated successfully!`);
    } else {
      const newResume = {
        ...resumeData,
        id: `res-${Date.now()}`,
        updatedAt: "Just now"
      };
      updated = [newResume, ...savedResumes];
      showToast(`New resume "${resumeData.title}" saved!`);
    }
    setSavedResumes(updated);
  };

  const duplicateResume = (resumeId) => {
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
  };

  const deleteResume = (resumeId) => {
    setSavedResumes(savedResumes.filter((r) => r.id !== resumeId));
    showToast("Resume deleted", "info");
  };

  const loadJobByUrl = (url) => {
    // Look up sample job or generate mock based on URL
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

  const setJobText = (text) => {
    setCurrentJob((prev) => ({
      ...prev,
      description: text,
      title: prev.title || "Custom Job Description",
      requiredSkills: ["JavaScript", "React", "HTML", "CSS", "Git"],
      preferredSkills: ["Node.js", "Docker", "AWS"]
    }));
    showToast("Custom Job Description saved!");
  };

  const handleFileUpload = (file) => {
    const fileData = {
      name: file.name,
      size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
      type: file.type || "application/pdf",
      uploadedAt: "Just now",
      status: "ready"
    };
    setUploadedFile(fileData);
    showToast(`Uploaded "${file.name}"`);
  };

  const removeFile = () => {
    setUploadedFile(null);
    showToast("Resume file removed", "info");
  };

  const triggerAnalysis = () => {
    // Generate an updated record for history and analysis
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
  };

  return (
    <AppContext.Provider
      value={{
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
