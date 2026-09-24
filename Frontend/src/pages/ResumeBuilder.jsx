import React, { useState } from 'react';
import { 
  Save, 
  Eye, 
  Edit3, 
  RotateCcw 
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ResumeForm from '../components/ResumeForm';
import ResumePreview from '../components/ResumePreview';
import ATSChecker from '../components/ATSChecker';
import ChatBox from '../components/ChatBox';
import { useApp } from '../context/AppContext';
import { defaultResumeData } from '../data/mockData';

export default function ResumeBuilder() {
  const { 
    activeResume, 
    updateActiveResume, 
    saveResumeFromBuilder, 
    showToast 
  } = useApp();

  const [activeTemplate, setActiveTemplate] = useState(activeResume?.template || 'modern');
  const [mobileTab, setMobileTab] = useState('form'); // 'form' | 'preview'

  const handleTemplateChange = (tmpl) => {
    setActiveTemplate(tmpl);
    updateActiveResume({ template: tmpl });
    showToast(`Switched to ${tmpl.charAt(0).toUpperCase() + tmpl.slice(1)} template`);
  };

  const handleSave = () => {
    saveResumeFromBuilder({
      ...activeResume,
      template: activeTemplate
    });
  };

  const handleResetToDefault = () => {
    updateActiveResume(defaultResumeData);
    showToast("Reset resume to student sample");
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#2F2A26] dark:text-[#F4EFE8] transition-colors">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">
        
        {/* Top Controls Bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-3 border-b border-[#E7E0D8] dark:border-[#413B34] no-print">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-[#7C5C3B] dark:text-[#C49A6C] uppercase tracking-wider">
                Interactive Editor
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#6B8E6B]/15 text-[#6B8E6B] font-semibold">
                Live Sync
              </span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-[#2F2A26] dark:text-[#F4EFE8]">
              Resume Builder
            </h1>
          </div>

          {/* Template Switcher & Save Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Template selector pills */}
            <div className="flex items-center p-1 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622]">
              <span className="text-xs font-medium text-[#77716B] dark:text-[#B9B0A5] px-2 hidden sm:inline">
                Template:
              </span>
              {['classic', 'modern', 'minimal'].map((tmpl) => (
                <button
                  key={tmpl}
                  type="button"
                  onClick={() => handleTemplateChange(tmpl)}
                  className={`text-xs capitalize px-2.5 py-1 rounded-md font-semibold transition-colors ${
                    activeTemplate === tmpl
                      ? 'bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A]'
                      : 'text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]'
                  }`}
                >
                  {tmpl}
                </button>
              ))}
            </div>

            {/* Reset to student mock */}
            <button
              type="button"
              onClick={handleResetToDefault}
              className="p-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#77716B] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] transition-colors"
              title="Reset to default template data"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            {/* Save Button */}
            <button
              type="button"
              onClick={handleSave}
              className="px-4 py-2 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] dark:hover:bg-[#B38757] text-xs font-bold shadow-warm-sm transition-colors flex items-center gap-1.5"
            >
              <Save className="w-3.5 h-3.5" />
              <span>Save Resume</span>
            </button>
          </div>
        </div>

        {/* Mobile View Toggle (Tabs on small screens) */}
        <div className="lg:hidden flex items-center p-1 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] no-print">
          <button
            type="button"
            onClick={() => setMobileTab('form')}
            className={`flex-1 py-1.5 text-xs font-semibold rounded-md flex items-center justify-center gap-1.5 transition-colors ${
              mobileTab === 'form'
                ? 'bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A]'
                : 'text-[#77716B] dark:text-[#B9B0A5]'
            }`}
          >
            <Edit3 className="w-3.5 h-3.5" />
            <span>Edit Sections</span>
          </button>
          <button
            type="button"
            onClick={() => setMobileTab('preview')}
            className={`flex-1 py-1.5 text-xs font-semibold rounded-md flex items-center justify-center gap-1.5 transition-colors ${
              mobileTab === 'preview'
                ? 'bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A]'
                : 'text-[#77716B] dark:text-[#B9B0A5]'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Live Preview</span>
          </button>
        </div>

        {/* Two-Column Split Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Left Side: Resume Form (7 cols on lg) */}
          <div className={`lg:col-span-6 xl:col-span-6 space-y-5 ${mobileTab === 'preview' ? 'hidden lg:block' : 'block'}`}>
            <ResumeForm
              resumeData={activeResume}
              onChange={updateActiveResume}
              showToast={showToast}
            />

            {/* ATS Section directly visible in editor column */}
            <ATSChecker score={86} />
          </div>

          {/* Right Side: Live Resume Preview (6 cols on lg) */}
          <div className={`lg:col-span-6 xl:col-span-6 lg:sticky lg:top-20 ${mobileTab === 'form' ? 'hidden lg:block' : 'block'}`}>
            <ResumePreview
              resumeData={activeResume}
              template={activeTemplate}
            />
          </div>

        </div>

      </main>

      <Footer />
      <ChatBox />
    </div>
  );
}
