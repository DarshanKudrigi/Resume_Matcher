import React, { useState } from 'react';
import { 
  User, 
  FileText, 
  GraduationCap, 
  Briefcase, 
  FolderGit2, 
  Wrench, 
  Award, 
  Trophy, 
  Sparkles, 
  Plus, 
  Trash2, 
  ChevronDown, 
  ChevronUp 
} from 'lucide-react';
import { aiSuggestions } from '../data/mockData';

export default function ResumeForm({ 
  resumeData, 
  onChange, 
  showToast 
}) {
  const [openSections, setOpenSections] = useState({
    personal: true,
    summary: true,
    experience: true,
    projects: false,
    education: false,
    skills: false,
    certifications: false,
    achievements: false
  });

  const toggleSection = (key) => {
    setOpenSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  // Helper updates
  const updatePersonalInfo = (field, value) => {
    onChange({
      personalInfo: {
        ...resumeData.personalInfo,
        [field]: value
      }
    });
  };

  // AI-Style Frontend Features
  const handleImproveSummary = () => {
    const randomSummary = aiSuggestions.summaries[Math.floor(Math.random() * aiSuggestions.summaries.length)];
    onChange({ summary: randomSummary });
    if (showToast) showToast("Summary enhanced with AI suggestion (mock)!");
  };

  const handleGenerateBulletPoint = (expId) => {
    const randomBullet = aiSuggestions.bulletPoints[Math.floor(Math.random() * aiSuggestions.bulletPoints.length)];
    const updated = (resumeData.experience || []).map((exp) => {
      if (exp.id === expId) {
        return {
          ...exp,
          bullets: [...(exp.bullets || []), randomBullet]
        };
      }
      return exp;
    });
    onChange({ experience: updated });
    if (showToast) showToast("Generated high-impact bullet point!");
  };

  const handleImproveProject = (projId) => {
    const randomBullet = aiSuggestions.projectDescriptions[Math.floor(Math.random() * aiSuggestions.projectDescriptions.length)];
    const updated = (resumeData.projects || []).map((p) => {
      if (p.id === projId) {
        return {
          ...p,
          bullets: [...(p.bullets || []), randomBullet]
        };
      }
      return p;
    });
    onChange({ projects: updated });
    if (showToast) showToast("Enhanced project description!");
  };

  // Add / Remove Experience
  const addExperience = () => {
    const newExp = {
      id: `exp-${Date.now()}`,
      role: "Software Developer",
      company: "Tech Startup",
      location: "Remote",
      startDate: "2024",
      endDate: "Present",
      bullets: ["Built modular React features and collaborated on team repositories."]
    };
    onChange({ experience: [...(resumeData.experience || []), newExp] });
  };

  const removeExperience = (id) => {
    onChange({ experience: (resumeData.experience || []).filter(e => e.id !== id) });
  };

  // Add / Remove Project
  const addProject = () => {
    const newProj = {
      id: `proj-${Date.now()}`,
      name: "New Web Application",
      tech: "React, Tailwind CSS, JavaScript",
      link: "https://github.com",
      bullets: ["Designed intuitive user interfaces with responsive layout support."]
    };
    onChange({ projects: [...(resumeData.projects || []), newProj] });
  };

  const removeProject = (id) => {
    onChange({ projects: (resumeData.projects || []).filter(p => p.id !== id) });
  };

  // Add / Remove Education
  const addEducation = () => {
    const newEdu = {
      id: `edu-${Date.now()}`,
      institution: "State University",
      degree: "B.S. in Computer Science",
      location: "India",
      startDate: "2022",
      endDate: "2026",
      score: "CGPA: 8.5"
    };
    onChange({ education: [...(resumeData.education || []), newEdu] });
  };

  const removeEducation = (id) => {
    onChange({ education: (resumeData.education || []).filter(e => e.id !== id) });
  };

  return (
    <div className="space-y-4">

      {/* 1. PERSONAL INFORMATION */}
      <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] overflow-hidden shadow-warm-sm">
        <button
          type="button"
          onClick={() => toggleSection('personal')}
          className="w-full px-5 py-3.5 flex items-center justify-between bg-[#FFFFFF] dark:bg-[#292622] hover:bg-[#F7F5F0]/60 dark:hover:bg-[#1F1D1A]/50 transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <User className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C]" />
            <span className="text-xs sm:text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Personal Information
            </span>
          </div>
          {openSections.personal ? <ChevronUp className="w-4 h-4 text-[#77716B]" /> : <ChevronDown className="w-4 h-4 text-[#77716B]" />}
        </button>

        {openSections.personal && (
          <div className="p-5 border-t border-[#E7E0D8] dark:border-[#413B34] space-y-3.5 bg-[#F7F5F0]/20 dark:bg-[#1F1D1A]/20">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5] block mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={resumeData.personalInfo?.fullName || ""}
                  onChange={(e) => updatePersonalInfo('fullName', e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5] block mb-1">
                  Headline / Target Role
                </label>
                <input
                  type="text"
                  value={resumeData.personalInfo?.headline || ""}
                  onChange={(e) => updatePersonalInfo('headline', e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5] block mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={resumeData.personalInfo?.email || ""}
                  onChange={(e) => updatePersonalInfo('email', e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5] block mb-1">
                  Phone Number
                </label>
                <input
                  type="text"
                  value={resumeData.personalInfo?.phone || ""}
                  onChange={(e) => updatePersonalInfo('phone', e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5] block mb-1">
                  Location (City, Country)
                </label>
                <input
                  type="text"
                  value={resumeData.personalInfo?.location || ""}
                  onChange={(e) => updatePersonalInfo('location', e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5] block mb-1">
                  LinkedIn URL
                </label>
                <input
                  type="text"
                  value={resumeData.personalInfo?.linkedin || ""}
                  onChange={(e) => updatePersonalInfo('linkedin', e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5] block mb-1">
                  GitHub Profile
                </label>
                <input
                  type="text"
                  value={resumeData.personalInfo?.github || ""}
                  onChange={(e) => updatePersonalInfo('github', e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5] block mb-1">
                  Portfolio Website
                </label>
                <input
                  type="text"
                  value={resumeData.personalInfo?.portfolio || ""}
                  onChange={(e) => updatePersonalInfo('portfolio', e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 2. SUMMARY */}
      <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] overflow-hidden shadow-warm-sm">
        <button
          type="button"
          onClick={() => toggleSection('summary')}
          className="w-full px-5 py-3.5 flex items-center justify-between bg-[#FFFFFF] dark:bg-[#292622] hover:bg-[#F7F5F0]/60 dark:hover:bg-[#1F1D1A]/50 transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <FileText className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C]" />
            <span className="text-xs sm:text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Summary
            </span>
          </div>
          {openSections.summary ? <ChevronUp className="w-4 h-4 text-[#77716B]" /> : <ChevronDown className="w-4 h-4 text-[#77716B]" />}
        </button>

        {openSections.summary && (
          <div className="p-5 border-t border-[#E7E0D8] dark:border-[#413B34] space-y-3 bg-[#F7F5F0]/20 dark:bg-[#1F1D1A]/20">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5]">
                Professional Summary Text
              </label>
              
              {/* AI Button: Improve Summary */}
              <button
                type="button"
                onClick={handleImproveSummary}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/20 text-[#7C5C3B] dark:text-[#C49A6C] hover:bg-[#7C5C3B]/20 transition-colors border border-[#7C5C3B]/20"
              >
                <Sparkles className="w-3 h-3" />
                <span>Improve Summary</span>
              </button>
            </div>

            <textarea
              rows={4}
              value={resumeData.summary || ""}
              onChange={(e) => onChange({ summary: e.target.value })}
              className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B] leading-relaxed resize-none"
            />
          </div>
        )}
      </div>

      {/* 3. EXPERIENCE */}
      <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] overflow-hidden shadow-warm-sm">
        <button
          type="button"
          onClick={() => toggleSection('experience')}
          className="w-full px-5 py-3.5 flex items-center justify-between bg-[#FFFFFF] dark:bg-[#292622] hover:bg-[#F7F5F0]/60 dark:hover:bg-[#1F1D1A]/50 transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <Briefcase className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C]" />
            <span className="text-xs sm:text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Experience ({resumeData.experience?.length || 0})
            </span>
          </div>
          {openSections.experience ? <ChevronUp className="w-4 h-4 text-[#77716B]" /> : <ChevronDown className="w-4 h-4 text-[#77716B]" />}
        </button>

        {openSections.experience && (
          <div className="p-5 border-t border-[#E7E0D8] dark:border-[#413B34] space-y-4 bg-[#F7F5F0]/20 dark:bg-[#1F1D1A]/20">
            {resumeData.experience?.map((exp, expIdx) => (
              <div key={exp.id || expIdx} className="p-4 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#7C5C3B] dark:text-[#C49A6C]">
                    Position #{expIdx + 1}
                  </span>
                  <button
                    type="button"
                    onClick={() => removeExperience(exp.id)}
                    className="p-1 rounded text-[#B96A63] hover:bg-[#B96A63]/10"
                    title="Remove experience"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="text-[11px] font-semibold text-[#77716B] block mb-1">Job Role</label>
                    <input
                      type="text"
                      value={exp.role || ""}
                      onChange={(e) => {
                        const updated = [...resumeData.experience];
                        updated[expIdx].role = e.target.value;
                        onChange({ experience: updated });
                      }}
                      className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-semibold text-[#77716B] block mb-1">Company</label>
                    <input
                      type="text"
                      value={exp.company || ""}
                      onChange={(e) => {
                        const updated = [...resumeData.experience];
                        updated[expIdx].company = e.target.value;
                        onChange({ experience: updated });
                      }}
                      className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-semibold text-[#77716B] block mb-1">Duration</label>
                    <input
                      type="text"
                      value={`${exp.startDate || ""} - ${exp.endDate || ""}`}
                      onChange={(e) => {
                        const updated = [...resumeData.experience];
                        const parts = e.target.value.split('-');
                        updated[expIdx].startDate = parts[0]?.trim() || "";
                        updated[expIdx].endDate = parts[1]?.trim() || "";
                        onChange({ experience: updated });
                      }}
                      placeholder="e.g. May 2025 - Jul 2025"
                      className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-semibold text-[#77716B] block mb-1">Location</label>
                    <input
                      type="text"
                      value={exp.location || ""}
                      onChange={(e) => {
                        const updated = [...resumeData.experience];
                        updated[expIdx].location = e.target.value;
                        onChange({ experience: updated });
                      }}
                      className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                    />
                  </div>
                </div>

                {/* Bullet Points */}
                <div className="space-y-2 pt-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-semibold text-[#77716B]">Bullet Points</span>
                    <button
                      type="button"
                      onClick={() => handleGenerateBulletPoint(exp.id)}
                      className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#7C5C3B] dark:text-[#C49A6C] hover:underline"
                    >
                      <Sparkles className="w-3 h-3" />
                      <span>Generate Bullet Point</span>
                    </button>
                  </div>

                  {exp.bullets?.map((bullet, bIdx) => (
                    <div key={bIdx} className="flex gap-2 items-center">
                      <input
                        type="text"
                        value={bullet}
                        onChange={(e) => {
                          const updated = [...resumeData.experience];
                          updated[expIdx].bullets[bIdx] = e.target.value;
                          onChange({ experience: updated });
                        }}
                        className="flex-1 px-2.5 py-1 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          const updated = [...resumeData.experience];
                          updated[expIdx].bullets = updated[expIdx].bullets.filter((_, idx) => idx !== bIdx);
                          onChange({ experience: updated });
                        }}
                        className="p-1 text-[#B96A63] hover:opacity-80"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>

              </div>
            ))}

            <button
              type="button"
              onClick={addExperience}
              className="w-full py-2 rounded-lg border-2 border-dashed border-[#E7E0D8] dark:border-[#413B34] text-xs font-semibold text-[#77716B] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] flex items-center justify-center gap-1.5 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Experience Position</span>
            </button>
          </div>
        )}
      </div>

      {/* 4. PROJECTS */}
      <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] overflow-hidden shadow-warm-sm">
        <button
          type="button"
          onClick={() => toggleSection('projects')}
          className="w-full px-5 py-3.5 flex items-center justify-between bg-[#FFFFFF] dark:bg-[#292622] hover:bg-[#F7F5F0]/60 dark:hover:bg-[#1F1D1A]/50 transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <FolderGit2 className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C]" />
            <span className="text-xs sm:text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Projects ({resumeData.projects?.length || 0})
            </span>
          </div>
          {openSections.projects ? <ChevronUp className="w-4 h-4 text-[#77716B]" /> : <ChevronDown className="w-4 h-4 text-[#77716B]" />}
        </button>

        {openSections.projects && (
          <div className="p-5 border-t border-[#E7E0D8] dark:border-[#413B34] space-y-4 bg-[#F7F5F0]/20 dark:bg-[#1F1D1A]/20">
            {resumeData.projects?.map((proj, pIdx) => (
              <div key={proj.id || pIdx} className="p-4 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#7C5C3B] dark:text-[#C49A6C]">
                    Project #{pIdx + 1}
                  </span>
                  <button
                    type="button"
                    onClick={() => removeProject(proj.id)}
                    className="p-1 rounded text-[#B96A63] hover:bg-[#B96A63]/10"
                    title="Remove project"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="text-[11px] font-semibold text-[#77716B] block mb-1">Project Name</label>
                    <input
                      type="text"
                      value={proj.name || ""}
                      onChange={(e) => {
                        const updated = [...resumeData.projects];
                        updated[pIdx].name = e.target.value;
                        onChange({ projects: updated });
                      }}
                      className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-semibold text-[#77716B] block mb-1">Tech Stack</label>
                    <input
                      type="text"
                      value={proj.tech || ""}
                      onChange={(e) => {
                        const updated = [...resumeData.projects];
                        updated[pIdx].tech = e.target.value;
                        onChange({ projects: updated });
                      }}
                      className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                    />
                  </div>
                </div>

                {/* Project Bullets */}
                <div className="space-y-2 pt-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-semibold text-[#77716B]">Description Bullets</span>
                    <button
                      type="button"
                      onClick={() => handleImproveProject(proj.id)}
                      className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#7C5C3B] dark:text-[#C49A6C] hover:underline"
                    >
                      <Sparkles className="w-3 h-3" />
                      <span>Improve Project Description</span>
                    </button>
                  </div>

                  {proj.bullets?.map((bullet, bIdx) => (
                    <div key={bIdx} className="flex gap-2 items-center">
                      <input
                        type="text"
                        value={bullet}
                        onChange={(e) => {
                          const updated = [...resumeData.projects];
                          updated[pIdx].bullets[bIdx] = e.target.value;
                          onChange({ projects: updated });
                        }}
                        className="flex-1 px-2.5 py-1 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          const updated = [...resumeData.projects];
                          updated[pIdx].bullets = updated[pIdx].bullets.filter((_, idx) => idx !== bIdx);
                          onChange({ projects: updated });
                        }}
                        className="p-1 text-[#B96A63] hover:opacity-80"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>

              </div>
            ))}

            <button
              type="button"
              onClick={addProject}
              className="w-full py-2 rounded-lg border-2 border-dashed border-[#E7E0D8] dark:border-[#413B34] text-xs font-semibold text-[#77716B] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] flex items-center justify-center gap-1.5 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Featured Project</span>
            </button>
          </div>
        )}
      </div>

      {/* 5. EDUCATION */}
      <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] overflow-hidden shadow-warm-sm">
        <button
          type="button"
          onClick={() => toggleSection('education')}
          className="w-full px-5 py-3.5 flex items-center justify-between bg-[#FFFFFF] dark:bg-[#292622] hover:bg-[#F7F5F0]/60 dark:hover:bg-[#1F1D1A]/50 transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <GraduationCap className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C]" />
            <span className="text-xs sm:text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Education ({resumeData.education?.length || 0})
            </span>
          </div>
          {openSections.education ? <ChevronUp className="w-4 h-4 text-[#77716B]" /> : <ChevronDown className="w-4 h-4 text-[#77716B]" />}
        </button>

        {openSections.education && (
          <div className="p-5 border-t border-[#E7E0D8] dark:border-[#413B34] space-y-4 bg-[#F7F5F0]/20 dark:bg-[#1F1D1A]/20">
            {resumeData.education?.map((edu, eIdx) => (
              <div key={edu.id || eIdx} className="p-4 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#7C5C3B] dark:text-[#C49A6C]">
                    Institution #{eIdx + 1}
                  </span>
                  <button
                    type="button"
                    onClick={() => removeEducation(edu.id)}
                    className="p-1 rounded text-[#B96A63] hover:bg-[#B96A63]/10"
                    title="Remove education"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="text-[11px] font-semibold text-[#77716B] block mb-1">University / College</label>
                    <input
                      type="text"
                      value={edu.institution || ""}
                      onChange={(e) => {
                        const updated = [...resumeData.education];
                        updated[eIdx].institution = e.target.value;
                        onChange({ education: updated });
                      }}
                      className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-semibold text-[#77716B] block mb-1">Degree & Major</label>
                    <input
                      type="text"
                      value={edu.degree || ""}
                      onChange={(e) => {
                        const updated = [...resumeData.education];
                        updated[eIdx].degree = e.target.value;
                        onChange({ education: updated });
                      }}
                      className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-semibold text-[#77716B] block mb-1">Years Attended</label>
                    <input
                      type="text"
                      value={`${edu.startDate || ""} - ${edu.endDate || ""}`}
                      onChange={(e) => {
                        const updated = [...resumeData.education];
                        const parts = e.target.value.split('-');
                        updated[eIdx].startDate = parts[0]?.trim() || "";
                        updated[eIdx].endDate = parts[1]?.trim() || "";
                        onChange({ education: updated });
                      }}
                      placeholder="e.g. 2022 - 2026"
                      className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-semibold text-[#77716B] block mb-1">GPA / Score</label>
                    <input
                      type="text"
                      value={edu.score || ""}
                      onChange={(e) => {
                        const updated = [...resumeData.education];
                        updated[eIdx].score = e.target.value;
                        onChange({ education: updated });
                      }}
                      className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                    />
                  </div>
                </div>
              </div>
            ))}

            <button
              type="button"
              onClick={addEducation}
              className="w-full py-2 rounded-lg border-2 border-dashed border-[#E7E0D8] dark:border-[#413B34] text-xs font-semibold text-[#77716B] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] flex items-center justify-center gap-1.5 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Education Degree</span>
            </button>
          </div>
        )}
      </div>

      {/* 6. SKILLS */}
      <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] overflow-hidden shadow-warm-sm">
        <button
          type="button"
          onClick={() => toggleSection('skills')}
          className="w-full px-5 py-3.5 flex items-center justify-between bg-[#FFFFFF] dark:bg-[#292622] hover:bg-[#F7F5F0]/60 dark:hover:bg-[#1F1D1A]/50 transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <Wrench className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C]" />
            <span className="text-xs sm:text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Skills
            </span>
          </div>
          {openSections.skills ? <ChevronUp className="w-4 h-4 text-[#77716B]" /> : <ChevronDown className="w-4 h-4 text-[#77716B]" />}
        </button>

        {openSections.skills && (
          <div className="p-5 border-t border-[#E7E0D8] dark:border-[#413B34] space-y-3.5 bg-[#F7F5F0]/20 dark:bg-[#1F1D1A]/20">
            <div>
              <label className="text-[11px] font-semibold text-[#77716B] block mb-1">
                Languages (comma separated)
              </label>
              <input
                type="text"
                value={resumeData.skills?.languages?.join(", ") || ""}
                onChange={(e) => {
                  onChange({
                    skills: {
                      ...resumeData.skills,
                      languages: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                    }
                  });
                }}
                className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8]"
              />
            </div>

            <div>
              <label className="text-[11px] font-semibold text-[#77716B] block mb-1">
                Frameworks & Libraries (comma separated)
              </label>
              <input
                type="text"
                value={resumeData.skills?.frameworks?.join(", ") || ""}
                onChange={(e) => {
                  onChange({
                    skills: {
                      ...resumeData.skills,
                      frameworks: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                    }
                  });
                }}
                className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8]"
              />
            </div>

            <div>
              <label className="text-[11px] font-semibold text-[#77716B] block mb-1">
                Tools & Platforms (comma separated)
              </label>
              <input
                type="text"
                value={resumeData.skills?.tools?.join(", ") || ""}
                onChange={(e) => {
                  onChange({
                    skills: {
                      ...resumeData.skills,
                      tools: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                    }
                  });
                }}
                className="w-full px-2.5 py-1.5 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8]"
              />
            </div>
          </div>
        )}
      </div>

      {/* 7. CERTIFICATIONS */}
      <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] overflow-hidden shadow-warm-sm">
        <button
          type="button"
          onClick={() => toggleSection('certifications')}
          className="w-full px-5 py-3.5 flex items-center justify-between bg-[#FFFFFF] dark:bg-[#292622] hover:bg-[#F7F5F0]/60 dark:hover:bg-[#1F1D1A]/50 transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <Award className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C]" />
            <span className="text-xs sm:text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Certifications ({resumeData.certifications?.length || 0})
            </span>
          </div>
          {openSections.certifications ? <ChevronUp className="w-4 h-4 text-[#77716B]" /> : <ChevronDown className="w-4 h-4 text-[#77716B]" />}
        </button>

        {openSections.certifications && (
          <div className="p-5 border-t border-[#E7E0D8] dark:border-[#413B34] space-y-3 bg-[#F7F5F0]/20 dark:bg-[#1F1D1A]/20">
            {resumeData.certifications?.map((cert, cIdx) => (
              <div key={cert.id || cIdx} className="flex gap-2 items-center">
                <input
                  type="text"
                  value={cert.name || ""}
                  onChange={(e) => {
                    const updated = [...resumeData.certifications];
                    updated[cIdx].name = e.target.value;
                    onChange({ certifications: updated });
                  }}
                  placeholder="Certification Name"
                  className="flex-1 px-2.5 py-1 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                />
                <input
                  type="text"
                  value={cert.issuer || ""}
                  onChange={(e) => {
                    const updated = [...resumeData.certifications];
                    updated[cIdx].issuer = e.target.value;
                    onChange({ certifications: updated });
                  }}
                  placeholder="Issuer"
                  className="w-32 px-2.5 py-1 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                />
                <button
                  type="button"
                  onClick={() => {
                    onChange({
                      certifications: (resumeData.certifications || []).filter((_, idx) => idx !== cIdx)
                    });
                  }}
                  className="p-1 text-[#B96A63]"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={() => {
                onChange({
                  certifications: [
                    ...(resumeData.certifications || []),
                    { id: `cert-${Date.now()}`, name: "New Certification", issuer: "Credential Platform", year: "2025" }
                  ]
                });
              }}
              className="text-xs font-semibold text-[#7C5C3B] dark:text-[#C49A6C] hover:underline flex items-center gap-1"
            >
              <Plus className="w-3 h-3" /> Add Certification
            </button>
          </div>
        )}
      </div>

      {/* 8. ACHIEVEMENTS */}
      <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] overflow-hidden shadow-warm-sm">
        <button
          type="button"
          onClick={() => toggleSection('achievements')}
          className="w-full px-5 py-3.5 flex items-center justify-between bg-[#FFFFFF] dark:bg-[#292622] hover:bg-[#F7F5F0]/60 dark:hover:bg-[#1F1D1A]/50 transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <Trophy className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C]" />
            <span className="text-xs sm:text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Achievements ({resumeData.achievements?.length || 0})
            </span>
          </div>
          {openSections.achievements ? <ChevronUp className="w-4 h-4 text-[#77716B]" /> : <ChevronDown className="w-4 h-4 text-[#77716B]" />}
        </button>

        {openSections.achievements && (
          <div className="p-5 border-t border-[#E7E0D8] dark:border-[#413B34] space-y-3 bg-[#F7F5F0]/20 dark:bg-[#1F1D1A]/20">
            {resumeData.achievements?.map((ach, aIdx) => (
              <div key={ach.id || aIdx} className="space-y-1.5 p-2 rounded-lg bg-[#FFFFFF] dark:bg-[#292622] border border-[#E7E0D8] dark:border-[#413B34]">
                <div className="flex justify-between items-center">
                  <input
                    type="text"
                    value={ach.title || ""}
                    onChange={(e) => {
                      const updated = [...resumeData.achievements];
                      updated[aIdx].title = e.target.value;
                      onChange({ achievements: updated });
                    }}
                    placeholder="Award / Competition Title"
                    className="flex-1 px-2 py-1 text-xs font-semibold rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      onChange({
                        achievements: (resumeData.achievements || []).filter((_, idx) => idx !== aIdx)
                      });
                    }}
                    className="p-1 text-[#B96A63] ml-2"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
                <input
                  type="text"
                  value={ach.detail || ""}
                  onChange={(e) => {
                    const updated = [...resumeData.achievements];
                    updated[aIdx].detail = e.target.value;
                    onChange({ achievements: updated });
                  }}
                  placeholder="Detail / Context"
                  className="w-full px-2 py-1 text-xs rounded border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#77716B] dark:text-[#B9B0A5]"
                />
              </div>
            ))}
            <button
              type="button"
              onClick={() => {
                onChange({
                  achievements: [
                    ...(resumeData.achievements || []),
                    { id: `ach-${Date.now()}`, title: "New Honor or Award", detail: "Recognized for performance in campus competition." }
                  ]
                });
              }}
              className="text-xs font-semibold text-[#7C5C3B] dark:text-[#C49A6C] hover:underline flex items-center gap-1"
            >
              <Plus className="w-3 h-3" /> Add Achievement
            </button>
          </div>
        )}
      </div>

    </div>
  );
}
