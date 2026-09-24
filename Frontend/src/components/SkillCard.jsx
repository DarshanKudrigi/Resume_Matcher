import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Sparkles } from 'lucide-react';

export default function SkillCard({ 
  matchedSkills = ["JavaScript", "React", "HTML", "CSS", "Git"],
  missingSkills = ["Docker", "AWS", "System Design"],
  partialSkills = ["Node.js"],
  className = "" 
}) {
  return (
    <div className={`rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 sm:p-6 shadow-warm-sm transition-colors duration-200 ${className}`}>
      
      <div className="flex items-center justify-between pb-4 mb-5 border-b border-[#E7E0D8] dark:border-[#413B34]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/10 text-[#7C5C3B] dark:text-[#C49A6C] flex items-center justify-center">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Skills Breakdown
            </h3>
            <p className="text-xs text-[#77716B] dark:text-[#B9B0A5]">
              Categorized analysis from resume vs. job requirements
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-5">
        
        {/* MATCHED SKILLS */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-xs font-bold uppercase tracking-wider text-[#6B8E6B] flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              MATCHED SKILLS ({matchedSkills.length})
            </span>
            <span className="text-[11px] font-medium text-[#77716B] dark:text-[#B9B0A5]">
              Strong presence detected
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {matchedSkills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#6B8E6B]/10 dark:bg-[#6B8E6B]/20 text-[#2F2A26] dark:text-[#F4EFE8] border border-[#6B8E6B]/30 transition-all hover:bg-[#6B8E6B]/15"
              >
                <span className="w-2 h-2 rounded-full bg-[#6B8E6B]" />
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* MISSING SKILLS */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-xs font-bold uppercase tracking-wider text-[#B96A63] flex items-center gap-1.5">
              <XCircle className="w-4 h-4" />
              MISSING SKILLS ({missingSkills.length})
            </span>
            <span className="text-[11px] font-medium text-[#77716B] dark:text-[#B9B0A5]">
              Priority learning targets
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {missingSkills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#B96A63]/10 dark:bg-[#B96A63]/20 text-[#2F2A26] dark:text-[#F4EFE8] border border-[#B96A63]/30 transition-all hover:bg-[#B96A63]/15"
              >
                <span className="w-2 h-2 rounded-full bg-[#B96A63]" />
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* PARTIAL MATCH */}
        <div>
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-xs font-bold uppercase tracking-wider text-[#C99545] flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4" />
              PARTIAL MATCH ({partialSkills.length})
            </span>
            <span className="text-[11px] font-medium text-[#77716B] dark:text-[#B9B0A5]">
              Foundations present
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {partialSkills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#C99545]/10 dark:bg-[#C99545]/20 text-[#2F2A26] dark:text-[#F4EFE8] border border-[#C99545]/30 transition-all hover:bg-[#C99545]/15"
              >
                <span className="w-2 h-2 rounded-full bg-[#C99545]" />
                {skill}
              </span>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
