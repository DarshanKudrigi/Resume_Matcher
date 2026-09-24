import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, 
  Edit3, 
  Eye, 
  Copy, 
  Trash2, 
  Clock, 
  X
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ResumePreview from '../components/ResumePreview';
import ChatBox from '../components/ChatBox';
import { useApp } from '../context/AppContext';
import { defaultResumeData } from '../data/mockData';

export default function MyResumes() {
  const { 
    savedResumes, 
    duplicateResume, 
    deleteResume, 
    setActiveResume, 
    showToast 
  } = useApp();

  const navigate = useNavigate();
  const [previewResume, setPreviewResume] = useState(null);

  const handleEdit = (resume) => {
    setActiveResume(resume);
    navigate('/builder');
  };

  const handleCreateNew = () => {
    const newResume = {
      ...defaultResumeData,
      id: `res-${Date.now()}`,
      title: "New Tailored Resume",
      updatedAt: "Just now",
      atsScore: 78
    };
    setActiveResume(newResume);
    showToast("Created new resume workspace");
    navigate('/builder');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#2F2A26] dark:text-[#F4EFE8] transition-colors">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E7E0D8] dark:border-[#413B34] gap-4">
          <div>
            <span className="text-xs font-semibold text-[#7C5C3B] dark:text-[#C49A6C] uppercase tracking-wider block mb-1">
              Resume Repository
            </span>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#2F2A26] dark:text-[#F4EFE8]">
              My Resumes
            </h1>
            <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5] mt-1">
              Manage, preview, and customize your tailored resumes for different applications.
            </p>
          </div>

          <button
            type="button"
            onClick={handleCreateNew}
            className="px-4 py-2.5 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] text-xs font-bold shadow-warm-sm transition-colors flex items-center gap-2 self-start sm:self-auto"
          >
            <Plus className="w-4 h-4" />
            <span>Create New Resume</span>
          </button>
        </div>

        {/* Resumes Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {savedResumes.map((resume) => (
            <div
              key={resume.id}
              className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 shadow-warm-sm hover:border-[#A67C52] dark:hover:border-[#C49A6C] transition-all flex flex-col justify-between"
            >
              <div>
                {/* Top badges */}
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/20 text-[#7C5C3B] dark:text-[#C49A6C] uppercase tracking-wider">
                    {resume.template || 'Modern'} Template
                  </span>

                  <div className="flex items-center gap-1.5 text-xs font-bold">
                    <span className="text-[#77716B] dark:text-[#B9B0A5] text-[11px]">ATS:</span>
                    <span className="px-2 py-0.5 rounded bg-[#6B8E6B]/15 text-[#6B8E6B]">
                      {resume.atsScore || 86}%
                    </span>
                  </div>
                </div>

                {/* Title */}
                <h3 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8] mb-1">
                  {resume.title}
                </h3>
                
                <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] mb-3">
                  Target: {resume.targetRole || "Software Engineer"}
                </p>

                {/* Skill tags */}
                <div className="flex flex-wrap gap-1 mb-4">
                  {(resume.tags || ["React", "JavaScript", "CSS"]).map((tag, i) => (
                    <span
                      key={i}
                      className="text-[10px] px-2 py-0.5 rounded bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] text-[#77716B] dark:text-[#B9B0A5]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Footer metadata & buttons */}
              <div className="pt-3 border-t border-[#E7E0D8] dark:border-[#413B34] space-y-3">
                <div className="flex items-center justify-between text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    Updated: {resume.updatedAt}
                  </span>
                  <span>{resume.projects?.length || 2} Projects</span>
                </div>

                {/* Action buttons: Edit, Preview, Duplicate, Delete */}
                <div className="grid grid-cols-4 gap-1.5 pt-1">
                  <button
                    type="button"
                    onClick={() => handleEdit(resume)}
                    className="py-1.5 px-2 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] text-xs font-semibold hover:bg-[#66492C] transition-colors flex items-center justify-center gap-1"
                    title="Edit in Resume Builder"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Edit</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setPreviewResume(resume)}
                    className="py-1.5 px-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0] dark:bg-[#1F1D1A] text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] hover:border-[#7C5C3B] transition-colors flex items-center justify-center gap-1"
                    title="Full Preview"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>View</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => duplicateResume(resume.id)}
                    className="py-1.5 px-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] transition-colors flex items-center justify-center gap-1"
                    title="Duplicate resume"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => deleteResume(resume.id)}
                    className="py-1.5 px-2 rounded-lg border border-[#B96A63]/30 bg-[#FFFFFF] dark:bg-[#292622] text-xs font-semibold text-[#B96A63] hover:bg-[#B96A63]/10 transition-colors flex items-center justify-center"
                    title="Delete resume"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

            </div>
          ))}
        </div>

      </main>

      {/* Quick Preview Modal */}
      {previewResume && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#2F2A26]/50 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-2xl max-h-[90vh] flex flex-col rounded-2xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-lg p-5">
            <div className="flex items-center justify-between pb-3 border-b border-[#E7E0D8] dark:border-[#413B34] mb-3">
              <h3 className="text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                {previewResume.title} — Preview
              </h3>
              <button
                type="button"
                onClick={() => setPreviewResume(null)}
                className="p-1.5 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] text-[#77716B] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto">
              <ResumePreview
                resumeData={previewResume}
                template={previewResume.template || 'modern'}
              />
            </div>
          </div>
        </div>
      )}

      <Footer />
      <ChatBox />
    </div>
  );
}
