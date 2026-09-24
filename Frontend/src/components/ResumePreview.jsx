import React from 'react';
import { Mail, Phone, MapPin, Printer } from 'lucide-react';

const LinkedinIcon = ({ className = "w-3 h-3" }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
  </svg>
);

const GithubIcon = ({ className = "w-3 h-3" }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
  </svg>
);

export default function ResumePreview({ 
  resumeData, 
  template = 'modern', // 'classic' | 'modern' | 'minimal'
  className = "" 
}) {
  const {
    personalInfo = {},
    summary = "",
    education = [],
    experience = [],
    projects = [],
    skills = {},
    certifications = [],
    achievements = []
  } = resumeData || {};

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      
      {/* Top Toolbar */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-[#E7E0D8] dark:border-[#413B34] no-print">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5]">
            Live Preview
          </span>
          <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/20 text-[#7C5C3B] dark:text-[#C49A6C]">
            {template} Template
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] hover:border-[#7C5C3B] text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] transition-colors shadow-warm-sm"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print / PDF</span>
          </button>
        </div>
      </div>

      {/* Resume Document Sheet */}
      <div className="flex-1 overflow-y-auto pr-1">
        <div 
          id="resume-document-sheet"
          className="resume-sheet bg-[#FFFFFF] text-[#2F2A26] rounded-xl border border-[#E7E0D8] dark:border-[#413B34] p-6 sm:p-8 shadow-warm-md text-xs leading-relaxed max-w-2xl mx-auto"
        >
          
          {/* ======================================================== */}
          {/* TEMPLATE 1: CLASSIC                                      */}
          {/* ======================================================== */}
          {template === 'classic' && (
            <div className="space-y-5 font-serif">
              {/* Header */}
              <div className="text-center border-b border-[#2F2A26]/20 pb-4">
                <h1 className="text-2xl font-bold tracking-normal uppercase text-[#2F2A26]">
                  {personalInfo.fullName || "Your Full Name"}
                </h1>
                {personalInfo.headline && (
                  <p className="text-xs italic text-[#77716B] mt-0.5 font-sans">
                    {personalInfo.headline}
                  </p>
                )}
                <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 mt-2 text-[11px] font-sans text-[#77716B]">
                  {personalInfo.email && <span>{personalInfo.email}</span>}
                  {personalInfo.phone && <span>• {personalInfo.phone}</span>}
                  {personalInfo.location && <span>• {personalInfo.location}</span>}
                  {personalInfo.linkedin && <span>• {personalInfo.linkedin}</span>}
                  {personalInfo.github && <span>• {personalInfo.github}</span>}
                </div>
              </div>

              {/* Summary */}
              {summary && (
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider border-b border-[#2F2A26]/20 pb-0.5 mb-2 font-sans">
                    Professional Summary
                  </h2>
                  <p className="text-[11px] text-[#2F2A26] leading-relaxed font-sans">{summary}</p>
                </div>
              )}

              {/* Experience */}
              {experience?.length > 0 && (
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider border-b border-[#2F2A26]/20 pb-0.5 mb-2 font-sans">
                    Work Experience
                  </h2>
                  <div className="space-y-3 font-sans">
                    {experience.map((exp, i) => (
                      <div key={exp.id || i}>
                        <div className="flex items-center justify-between font-semibold text-xs">
                          <span>{exp.role} <span className="font-normal text-[#77716B]">at {exp.company}</span></span>
                          <span className="text-[11px] text-[#77716B]">{exp.startDate} – {exp.endDate}</span>
                        </div>
                        {exp.location && <p className="text-[10px] text-[#77716B]">{exp.location}</p>}
                        <ul className="list-disc list-inside mt-1 space-y-0.5 text-[11px]">
                          {exp.bullets?.map((b, idx) => (
                            <li key={idx}>{b}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Projects */}
              {projects?.length > 0 && (
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider border-b border-[#2F2A26]/20 pb-0.5 mb-2 font-sans">
                    Key Projects
                  </h2>
                  <div className="space-y-2.5 font-sans">
                    {projects.map((proj, i) => (
                      <div key={proj.id || i}>
                        <div className="flex items-center justify-between font-semibold text-xs">
                          <span>{proj.name}</span>
                          <span className="text-[10px] text-[#77716B] font-mono">{proj.tech}</span>
                        </div>
                        <ul className="list-disc list-inside mt-1 space-y-0.5 text-[11px]">
                          {proj.bullets?.map((b, idx) => (
                            <li key={idx}>{b}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Education */}
              {education?.length > 0 && (
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider border-b border-[#2F2A26]/20 pb-0.5 mb-2 font-sans">
                    Education
                  </h2>
                  <div className="space-y-2 font-sans">
                    {education.map((edu, i) => (
                      <div key={edu.id || i} className="flex justify-between items-baseline">
                        <div>
                          <p className="font-semibold text-xs">{edu.institution}</p>
                          <p className="text-[11px] text-[#77716B]">{edu.degree}</p>
                        </div>
                        <div className="text-right text-[11px] text-[#77716B]">
                          <p>{edu.startDate} – {edu.endDate}</p>
                          {edu.score && <p className="font-medium text-[#2F2A26]">{edu.score}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Skills */}
              {skills && (
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider border-b border-[#2F2A26]/20 pb-0.5 mb-2 font-sans">
                    Skills
                  </h2>
                  <div className="text-[11px] space-y-1 font-sans">
                    {skills.languages && <p><span className="font-semibold">Languages:</span> {skills.languages.join(", ")}</p>}
                    {skills.frameworks && <p><span className="font-semibold">Frameworks:</span> {skills.frameworks.join(", ")}</p>}
                    {skills.tools && <p><span className="font-semibold">Developer Tools:</span> {skills.tools.join(", ")}</p>}
                  </div>
                </div>
              )}

              {/* Certifications & Achievements */}
              {(certifications?.length > 0 || achievements?.length > 0) && (
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider border-b border-[#2F2A26]/20 pb-0.5 mb-2 font-sans">
                    Certifications & Honors
                  </h2>
                  <div className="text-[11px] space-y-1 font-sans">
                    {certifications?.map((c, i) => (
                      <p key={i}>• <span className="font-semibold">{c.name}</span> – {c.issuer} ({c.year})</p>
                    ))}
                    {achievements?.map((a, i) => (
                      <p key={i}>• <span className="font-semibold">{a.title}</span>: {a.detail}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ======================================================== */}
          {/* TEMPLATE 2: MODERN                                       */}
          {/* ======================================================== */}
          {template === 'modern' && (
            <div className="space-y-4 font-sans">
              
              {/* Header Banner */}
              <div className="border-b-2 border-[#7C5C3B] pb-3">
                <h1 className="text-2xl font-bold tracking-tight text-[#2F2A26]">
                  {personalInfo.fullName || "Your Full Name"}
                </h1>
                {personalInfo.headline && (
                  <p className="text-xs font-medium text-[#7C5C3B] mt-0.5">
                    {personalInfo.headline}
                  </p>
                )}

                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-[11px] text-[#77716B]">
                  {personalInfo.email && <span className="flex items-center gap-1"><Mail className="w-3 h-3 text-[#7C5C3B]" />{personalInfo.email}</span>}
                  {personalInfo.phone && <span className="flex items-center gap-1"><Phone className="w-3 h-3 text-[#7C5C3B]" />{personalInfo.phone}</span>}
                  {personalInfo.location && <span className="flex items-center gap-1"><MapPin className="w-3 h-3 text-[#7C5C3B]" />{personalInfo.location}</span>}
                  {personalInfo.linkedin && <span className="flex items-center gap-1"><LinkedinIcon className="w-3 h-3 text-[#7C5C3B]" />{personalInfo.linkedin}</span>}
                  {personalInfo.github && <span className="flex items-center gap-1"><GithubIcon className="w-3 h-3 text-[#7C5C3B]" />{personalInfo.github}</span>}
                </div>
              </div>

              {/* Summary */}
              {summary && (
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-[#7C5C3B] mb-1.5 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#7C5C3B]" />
                    Professional Summary
                  </h2>
                  <p className="text-[11px] text-[#2F2A26] leading-relaxed bg-[#F7F5F0]/60 p-2.5 rounded-lg border border-[#E7E0D8]/60">
                    {summary}
                  </p>
                </div>
              )}

              {/* Experience */}
              {experience?.length > 0 && (
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-[#7C5C3B] mb-2 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#7C5C3B]" />
                    Experience
                  </h2>
                  <div className="space-y-3">
                    {experience.map((exp, i) => (
                      <div key={exp.id || i} className="border-l-2 border-[#E7E0D8] pl-3 py-0.5">
                        <div className="flex items-center justify-between text-xs font-bold text-[#2F2A26]">
                          <span>{exp.role}</span>
                          <span className="text-[10px] font-medium text-[#77716B] bg-[#F7F5F0] px-2 py-0.5 rounded">
                            {exp.startDate} – {exp.endDate}
                          </span>
                        </div>
                        <p className="text-[11px] font-medium text-[#7C5C3B] mb-1">
                          {exp.company} {exp.location && `• ${exp.location}`}
                        </p>
                        <ul className="list-disc list-inside space-y-0.5 text-[11px] text-[#2F2A26]">
                          {exp.bullets?.map((b, idx) => (
                            <li key={idx}>{b}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Projects */}
              {projects?.length > 0 && (
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-[#7C5C3B] mb-2 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#7C5C3B]" />
                    Featured Projects
                  </h2>
                  <div className="space-y-2.5">
                    {projects.map((proj, i) => (
                      <div key={proj.id || i} className="bg-[#F7F5F0]/40 p-2.5 rounded-lg border border-[#E7E0D8]/50">
                        <div className="flex items-center justify-between text-xs font-bold text-[#2F2A26]">
                          <span>{proj.name}</span>
                          <span className="text-[10px] font-mono font-normal text-[#7C5C3B]">{proj.tech}</span>
                        </div>
                        <ul className="list-disc list-inside mt-1 space-y-0.5 text-[11px] text-[#2F2A26]">
                          {proj.bullets?.map((b, idx) => (
                            <li key={idx}>{b}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Two column row for Education & Skills */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
                {/* Education */}
                {education?.length > 0 && (
                  <div>
                    <h2 className="text-xs font-bold uppercase tracking-wider text-[#7C5C3B] mb-2 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#7C5C3B]" />
                      Education
                    </h2>
                    <div className="space-y-2">
                      {education.map((edu, i) => (
                        <div key={edu.id || i} className="text-[11px]">
                          <p className="font-bold text-[#2F2A26]">{edu.institution}</p>
                          <p className="text-[#77716B]">{edu.degree}</p>
                          <div className="flex justify-between text-[10px] text-[#77716B] mt-0.5">
                            <span>{edu.startDate} – {edu.endDate}</span>
                            {edu.score && <span className="font-semibold text-[#7C5C3B]">{edu.score}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Skills */}
                {skills && (
                  <div>
                    <h2 className="text-xs font-bold uppercase tracking-wider text-[#7C5C3B] mb-2 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#7C5C3B]" />
                      Skills & Tooling
                    </h2>
                    <div className="flex flex-wrap gap-1 text-[10px]">
                      {skills.languages?.map((s, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-[#7C5C3B]/10 text-[#7C5C3B] font-semibold">{s}</span>
                      ))}
                      {skills.frameworks?.map((s, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-[#F7F5F0] border border-[#E7E0D8] text-[#2F2A26] font-medium">{s}</span>
                      ))}
                      {skills.tools?.map((s, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-[#F7F5F0] border border-[#E7E0D8] text-[#77716B]">{s}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Certifications & Achievements */}
              {(certifications?.length > 0 || achievements?.length > 0) && (
                <div className="pt-1">
                  <h2 className="text-xs font-bold uppercase tracking-wider text-[#7C5C3B] mb-1.5 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#7C5C3B]" />
                    Certifications & Achievements
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                    {certifications?.map((c, i) => (
                      <div key={i} className="text-[#2F2A26]">
                        <span className="font-semibold">{c.name}</span>
                        <span className="text-[10px] text-[#77716B] block">{c.issuer} ({c.year})</span>
                      </div>
                    ))}
                    {achievements?.map((a, i) => (
                      <div key={i} className="text-[#2F2A26]">
                        <span className="font-semibold">{a.title}</span>
                        <span className="text-[10px] text-[#77716B] block">{a.detail}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          )}

          {/* ======================================================== */}
          {/* TEMPLATE 3: MINIMAL                                      */}
          {/* ======================================================== */}
          {template === 'minimal' && (
            <div className="space-y-4 font-sans text-[#2F2A26]">
              {/* Header */}
              <div>
                <h1 className="text-2xl font-light tracking-tight text-[#2F2A26]">
                  {personalInfo.fullName || "Your Full Name"}
                </h1>
                {personalInfo.headline && (
                  <p className="text-xs text-[#77716B] tracking-wide mt-0.5 uppercase">
                    {personalInfo.headline}
                  </p>
                )}
                <div className="flex flex-wrap gap-3 mt-1.5 text-[11px] text-[#77716B]">
                  {personalInfo.email && <span>{personalInfo.email}</span>}
                  {personalInfo.phone && <span>{personalInfo.phone}</span>}
                  {personalInfo.location && <span>{personalInfo.location}</span>}
                  {personalInfo.github && <span>{personalInfo.github}</span>}
                </div>
              </div>

              <div className="h-px bg-[#E7E0D8]" />

              {/* Summary */}
              {summary && (
                <div>
                  <p className="text-[11px] leading-relaxed text-[#2F2A26]/90">
                    {summary}
                  </p>
                </div>
              )}

              {/* Experience */}
              {experience?.length > 0 && (
                <div>
                  <h2 className="text-[11px] font-bold uppercase tracking-widest text-[#77716B] mb-2">
                    Experience
                  </h2>
                  <div className="space-y-3">
                    {experience.map((exp, i) => (
                      <div key={exp.id || i}>
                        <div className="flex justify-between items-baseline text-xs">
                          <span className="font-medium text-[#2F2A26]">{exp.role}, <span className="text-[#77716B]">{exp.company}</span></span>
                          <span className="text-[10px] text-[#77716B]">{exp.startDate} – {exp.endDate}</span>
                        </div>
                        <ul className="mt-1 space-y-0.5 text-[11px] text-[#2F2A26]/80 list-disc list-inside">
                          {exp.bullets?.map((b, idx) => (
                            <li key={idx}>{b}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Projects */}
              {projects?.length > 0 && (
                <div>
                  <h2 className="text-[11px] font-bold uppercase tracking-widest text-[#77716B] mb-2">
                    Projects
                  </h2>
                  <div className="space-y-2">
                    {projects.map((proj, i) => (
                      <div key={proj.id || i}>
                        <div className="flex justify-between items-baseline text-xs">
                          <span className="font-medium">{proj.name}</span>
                          <span className="text-[10px] text-[#77716B]">{proj.tech}</span>
                        </div>
                        <ul className="mt-0.5 space-y-0.5 text-[11px] text-[#2F2A26]/80 list-disc list-inside">
                          {proj.bullets?.map((b, idx) => (
                            <li key={idx}>{b}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Education */}
              {education?.length > 0 && (
                <div>
                  <h2 className="text-[11px] font-bold uppercase tracking-widest text-[#77716B] mb-2">
                    Education
                  </h2>
                  <div className="space-y-1.5 text-xs">
                    {education.map((edu, i) => (
                      <div key={edu.id || i} className="flex justify-between items-baseline">
                        <span>{edu.degree} — {edu.institution}</span>
                        <span className="text-[10px] text-[#77716B]">{edu.startDate} – {edu.endDate} {edu.score ? `(${edu.score})` : ''}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Skills */}
              {skills && (
                <div>
                  <h2 className="text-[11px] font-bold uppercase tracking-widest text-[#77716B] mb-1">
                    Technical Skills
                  </h2>
                  <p className="text-[11px] text-[#2F2A26]/85">
                    {[...(skills.languages || []), ...(skills.frameworks || []), ...(skills.tools || [])].join(" • ")}
                  </p>
                </div>
              )}

            </div>
          )}

        </div>
      </div>

    </div>
  );
}
