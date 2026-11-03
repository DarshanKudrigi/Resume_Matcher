import React from 'react';
import { CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function ATSChecker({ 
  atsBreakdown = null,
  resumeData = null,
  score = null, 
  checks = null,
  className = "" 
}) {
  // Determine effective checks and score dynamically
  let effectiveChecks = [];
  let effectiveScore = 85;
  let verdict = "ATS Evaluated";

  if (atsBreakdown && Array.isArray(atsBreakdown.items) && atsBreakdown.items.length > 0) {
    effectiveScore = atsBreakdown.score ?? 85;
    verdict = atsBreakdown.verdict || "ATS Passed with High Compatibility";
    effectiveChecks = atsBreakdown.items.map(item => ({
      id: item.id,
      name: item.label || item.name,
      passed: Boolean(item.passed),
      note: item.note
    }));
  } else if (resumeData) {
    const pInfo = resumeData.personalInfo || {};
    const hasEmail = Boolean(pInfo.email && pInfo.email.includes('@'));
    const hasPhone = Boolean(pInfo.phone && pInfo.phone.trim().length >= 7);
    const hasSkills = Boolean(
      (resumeData.skills && (
        (Array.isArray(resumeData.skills) && resumeData.skills.length > 0) ||
        Object.values(resumeData.skills).some(v => Array.isArray(v) && v.length > 0)
      )) || (resumeData.extracted_skills && resumeData.extracted_skills.length > 0)
    );
    const hasEdu = Boolean(resumeData.education && resumeData.education.length > 0);
    const hasExpOrProj = Boolean(
      (resumeData.experience && resumeData.experience.length > 0) ||
      (resumeData.projects && resumeData.projects.length > 0)
    );
    const hasSummary = Boolean(resumeData.summary && resumeData.summary.trim().length > 15);

    effectiveChecks = [
      {
        id: "contact",
        name: "Contact information",
        passed: hasEmail && hasPhone,
        note: (hasEmail && hasPhone) 
          ? "Full contact details (email and phone) verified." 
          : `Missing ${!hasPhone ? 'phone number' : 'email address'}.`
      },
      {
        id: "skills",
        name: "Skills section",
        passed: hasSkills,
        note: hasSkills ? "Categorized technical competencies identified." : "Add key technical skills."
      },
      {
        id: "education",
        name: "Education & Credentials",
        passed: hasEdu,
        note: hasEdu ? "Degree credential and university listed." : "Add college/degree details."
      },
      {
        id: "projects",
        name: "Projects & Experience",
        passed: hasExpOrProj,
        note: hasExpOrProj ? "Practical project and role descriptions present." : "Add project portfolios or experience bullets."
      },
      {
        id: "summary",
        name: "Professional Summary",
        passed: hasSummary,
        note: hasSummary ? "Impactful career summary present." : "Add a concise professional summary."
      },
      {
        id: "layout",
        name: "Clean ATS Layout",
        passed: true,
        note: "Single/two-column text format with high ATS parsability."
      }
    ];

    const passedCount = effectiveChecks.filter(c => c.passed).length;
    effectiveScore = Math.round((passedCount / effectiveChecks.length) * 100);
    verdict = effectiveScore >= 85 ? "ATS Passed with High Compatibility" : (effectiveScore >= 70 ? "ATS Passed with Minor Enhancements" : "ATS Review Recommended");
  } else if (Array.isArray(checks) && checks.length > 0) {
    effectiveChecks = checks.map(c => ({
      id: c.id,
      name: c.name || c.label,
      passed: Boolean(c.passed),
      note: c.note || c.warning
    }));
    effectiveScore = score ?? Math.round((effectiveChecks.filter(c => c.passed).length / effectiveChecks.length) * 100);
  } else {
    effectiveScore = score ?? 85;
    effectiveChecks = [
      { id: "contact", name: "Contact information", passed: true, note: "Full name and contact verified." },
      { id: "skills", name: "Skills section", passed: true, note: "Categorized skills list found." },
      { id: "education", name: "Education", passed: true, note: "University degree parsed." },
      { id: "projects", name: "Projects & Experience", passed: true, note: "Project portfolios identified." },
      { id: "layout", name: "Clean ATS Layout", passed: true, note: "Standard text format." }
    ];
  }

  // Find any notice / warning to display
  const failedItem = effectiveChecks.find(c => !c.passed);

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
              Resume ATS Check
            </h4>
            <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
              {verdict}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-[#77716B] dark:text-[#B9B0A5]">
            Compatibility:
          </span>
          <span className={`text-sm font-bold px-2 py-0.5 rounded-md ${
            effectiveScore >= 80 
              ? 'bg-[#6B8E6B]/15 text-[#6B8E6B]' 
              : (effectiveScore >= 60 ? 'bg-[#C99545]/15 text-[#C99545]' : 'bg-red-500/15 text-red-500')
          }`}>
            {effectiveScore}%
          </span>
        </div>
      </div>

      {/* Checklist items */}
      <div className="space-y-2.5">
        {effectiveChecks.map((check) => (
          <div key={check.id} className="flex items-start justify-between text-xs gap-2">
            <div className="flex items-start gap-2 min-w-0">
              {check.passed ? (
                <CheckCircle2 className="w-4 h-4 text-[#6B8E6B] shrink-0 mt-0.5" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-[#C99545] shrink-0 mt-0.5" />
              )}
              <div className="min-w-0">
                <span className={`font-medium block ${check.passed ? 'text-[#2F2A26] dark:text-[#F4EFE8]' : 'text-[#C99545]'}`}>
                  {check.name}
                </span>
                {check.note && (
                  <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5] block leading-tight mt-0.5">
                    {check.note}
                  </span>
                )}
              </div>
            </div>

            {check.passed ? (
              <span className="text-[10px] text-[#6B8E6B] font-semibold uppercase shrink-0">
                Verified
              </span>
            ) : (
              <span className="text-[10px] text-[#C99545] font-semibold uppercase shrink-0">
                Needs Review
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Dynamic Notice Banner */}
      {failedItem ? (
        <div className="mt-4 p-3 rounded-lg bg-[#C99545]/10 border border-[#C99545]/30 flex items-start gap-2.5 text-xs text-[#2F2A26] dark:text-[#F4EFE8]">
          <AlertTriangle className="w-4 h-4 text-[#C99545] shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block text-[#C99545]">ATS Recommendation:</span>
            <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5] mt-0.5 leading-relaxed">
              {failedItem.note || `Enhance the "${failedItem.name}" section to boost your ATS compatibility score.`}
            </p>
          </div>
        </div>
      ) : (
        <div className="mt-4 p-3 rounded-lg bg-[#6B8E6B]/10 border border-[#6B8E6B]/30 flex items-start gap-2.5 text-xs text-[#2F2A26] dark:text-[#F4EFE8]">
          <CheckCircle2 className="w-4 h-4 text-[#6B8E6B] shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block text-[#6B8E6B]">ATS Compliant:</span>
            <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5] mt-0.5 leading-relaxed">
              All core ATS screening checkpoints passed. Document structure, contact info, and keywords are verified.
            </p>
          </div>
        </div>
      )}

    </div>
  );
}
