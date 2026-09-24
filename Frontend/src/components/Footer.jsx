import React from 'react';
import { FileCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] py-8 text-xs text-[#77716B] dark:text-[#B9B0A5] transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-md bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] flex items-center justify-center">
              <FileCheck className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className="font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">ResumeMate</span>
              <span className="mx-2 text-[#E7E0D8] dark:text-[#413B34]">|</span>
              <span>AI-Based Resume–Job Description Matching and Skill Gap Analysis System</span>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <Link to="/dashboard" className="hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] transition-colors">
              Dashboard
            </Link>
            <Link to="/analyzer" className="hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] transition-colors">
              Analyzer
            </Link>
            <Link to="/builder" className="hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] transition-colors">
              Resume Builder
            </Link>
            <Link to="/settings" className="hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] transition-colors">
              Settings
            </Link>
          </div>

          <div className="flex items-center gap-1.5 text-[11px]">
            <span>College Project Prototype</span>
            <span className="text-[#E7E0D8] dark:text-[#413B34]">•</span>
            <span>Frontend-only Architecture</span>
          </div>

        </div>
      </div>
    </footer>
  );
}
