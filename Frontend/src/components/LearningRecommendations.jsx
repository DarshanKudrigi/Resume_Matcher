import React, { useState } from 'react';
import { BookOpen, Clock, Award, X, CheckCircle2, ChevronRight, ExternalLink } from 'lucide-react';

export default function LearningRecommendations({ recommendations = [], className = "" }) {
  const [selectedSkillModal, setSelectedSkillModal] = useState(null);

  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-4 ${className}`}>
      
      {/* Section Heading */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base sm:text-lg font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
            Recommended Official Documentation
          </h3>
          <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5]">
            Targeted official documentation and developer guides to close missing skill gaps
          </p>
        </div>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {recommendations.map((rec) => (
          <div
            key={rec.id || rec.skill}
            className="flex flex-col justify-between rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 shadow-warm-sm hover:border-[#A67C52] dark:hover:border-[#C49A6C] transition-all duration-200"
          >
            <div>
              {/* Skill and Badges */}
              <div className="flex items-start justify-between gap-2 mb-3">
                <span className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                  {rec.skill}
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/20 text-[#7C5C3B] dark:text-[#C49A6C] border border-[#7C5C3B]/20 dark:border-[#C49A6C]/30">
                  {rec.difficulty.split(' ')[0]}
                </span>
              </div>

              {/* Short explanation */}
              <p className="text-xs text-[#2F2A26] dark:text-[#F4EFE8] font-medium mb-3 leading-relaxed">
                "{rec.subtitle}"
              </p>

              <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5] line-clamp-2 mb-4 leading-normal">
                {rec.summary}
              </p>
            </div>

            <div className="pt-3 border-t border-[#E7E0D8] dark:border-[#413B34] space-y-3">
              {/* Metadata */}
              <div className="flex items-center justify-between text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-[#A67C52] dark:text-[#D8B08A]" />
                  {rec.estimatedTime}
                </span>
                <span className="flex items-center gap-1">
                  <Award className="w-3.5 h-3.5 text-[#A67C52] dark:text-[#D8B08A]" />
                  {rec.difficulty}
                </span>
              </div>

              {/* View Resources Button */}
              <button
                type="button"
                onClick={() => setSelectedSkillModal(rec)}
                className="w-full py-2 px-3 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#2F2A26] dark:text-[#F4EFE8] hover:bg-[#7C5C3B] hover:text-[#F7F5F0] dark:hover:bg-[#C49A6C] dark:hover:text-[#1F1D1A] text-xs font-semibold transition-all flex items-center justify-center gap-1.5"
              >
                <span>Read Official Docs</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

          </div>
        ))}
      </div>

      {/* Resources Modal */}
      {selectedSkillModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#2F2A26]/50 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-lg rounded-2xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-lg p-6 space-y-5 animate-scale-up">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-3 border-b border-[#E7E0D8] dark:border-[#413B34]">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-lg bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/20 text-[#7C5C3B] dark:text-[#C49A6C] flex items-center justify-center">
                  <BookOpen className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                    {selectedSkillModal.skill} Official Documentation
                  </h4>
                  <p className="text-xs text-[#77716B] dark:text-[#B9B0A5]">
                    Est. Time: {selectedSkillModal.estimatedTime} • {selectedSkillModal.difficulty}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setSelectedSkillModal(null)}
                className="p-1.5 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] text-[#77716B] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Topics Covered */}
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5] block mb-2">
                Official Concepts & Topics to Master:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {selectedSkillModal.keyTopics?.map((topic, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs text-[#2F2A26] dark:text-[#F4EFE8] p-2 rounded-md bg-[#F7F5F0] dark:bg-[#1F1D1A]">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#6B8E6B] shrink-0" />
                    <span className="truncate">{topic}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Curated Official Resources List */}
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-[#77716B] dark:text-[#B9B0A5] block mb-2">
                Recommended Official Documentation:
              </span>
              <div className="space-y-2.5">
                {selectedSkillModal.resources?.map((res, i) => (
                  <a
                    key={i}
                    href={res.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-3 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 hover:bg-[#F7F5F0] dark:hover:bg-[#1F1D1A] hover:border-[#7C5C3B] dark:hover:border-[#C49A6C] transition-all flex items-center justify-between gap-3 text-xs group cursor-pointer"
                    title={`Open official documentation in new tab: ${res.link}`}
                  >
                    <div>
                      <p className="font-semibold text-[#2F2A26] dark:text-[#F4EFE8] group-hover:text-[#7C5C3B] dark:group-hover:text-[#C49A6C] transition-colors flex items-center gap-1.5">
                        <span>{res.title}</span>
                        <ExternalLink className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100" />
                      </p>
                      <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5] mt-0.5">
                        {res.provider} • {res.type} {res.duration ? `(${res.duration})` : ''}
                      </p>
                    </div>
                    <span className="px-2.5 py-1 rounded bg-[#FFFFFF] dark:bg-[#292622] border border-[#E7E0D8] dark:border-[#413B34] group-hover:bg-[#7C5C3B] group-hover:text-white dark:group-hover:bg-[#C49A6C] dark:group-hover:text-[#1F1D1A] text-[10px] font-semibold text-[#7C5C3B] dark:text-[#C49A6C] transition-colors shrink-0 flex items-center gap-1">
                      Read Docs <ExternalLink className="w-2.5 h-2.5" />
                    </span>
                  </a>
                ))}
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="button"
                onClick={() => setSelectedSkillModal(null)}
                className="px-4 py-2 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] font-semibold text-xs transition-colors"
              >
                Close Guide
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
