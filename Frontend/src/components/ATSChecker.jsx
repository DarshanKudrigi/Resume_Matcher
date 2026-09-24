import React from 'react';
import { CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function ATSChecker({ 
  score = 86, 
  checks = [
    { id: "contact", name: "Contact information", passed: true },
    { id: "skills", name: "Skills section", passed: true },
    { id: "education", name: "Education", passed: true },
    { id: "projects", name: "Projects", passed: true },
    { id: "keywords", name: "Keywords", passed: false, warning: "Add more job-specific keywords." },
  ],
  className = "" 
}) {
  return (
    <div className={`rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 shadow-warm-sm transition-colors duration-200 ${className}`}>
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3.5 mb-4 border-b border-[#E7E0D8] dark:border-[#413B34]">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[#6B8E6B]/15 text-[#6B8E6B] flex items-center justify-center">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Resume Check
            </h4>
            <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
              Automated Applicant Tracking System screening
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5]">
            ATS Compatibility:
          </span>
          <span className="text-sm font-bold px-2 py-0.5 rounded-md bg-[#6B8E6B]/15 text-[#6B8E6B]">
            {score}%
          </span>
        </div>
      </div>

      {/* Checklist items */}
      <div className="space-y-2.5">
        {checks.map((check) => (
          <div key={check.id} className="flex items-start justify-between text-xs gap-2">
            <div className="flex items-center gap-2">
              {check.passed ? (
                <CheckCircle2 className="w-4 h-4 text-[#6B8E6B] shrink-0" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-[#C99545] shrink-0" />
              )}
              <span className={`font-medium ${check.passed ? 'text-[#2F2A26] dark:text-[#F4EFE8]' : 'text-[#C99545]'}`}>
                {check.name}
              </span>
            </div>

            {check.passed ? (
              <span className="text-[10px] text-[#6B8E6B] font-semibold uppercase">
                Verified
              </span>
            ) : (
              <span className="text-[10px] text-[#C99545] font-semibold uppercase">
                Needs Review
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Warning Notice Banner */}
      <div className="mt-4 p-3 rounded-lg bg-[#C99545]/10 border border-[#C99545]/30 flex items-start gap-2.5 text-xs text-[#2F2A26] dark:text-[#F4EFE8]">
        <AlertTriangle className="w-4 h-4 text-[#C99545] shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold block text-[#C99545]">Warning:</span>
          <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5] mt-0.5 leading-relaxed">
            Add more job-specific keywords. (Suggested: "Docker", "AWS", "Containerization").
          </p>
        </div>
      </div>

    </div>
  );
}
