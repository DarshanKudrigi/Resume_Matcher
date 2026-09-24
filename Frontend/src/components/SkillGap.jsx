import React from 'react';
import { BarChart2 } from 'lucide-react';

export default function SkillGap({ 
  skillGaps = [
    { skill: "JavaScript", status: "Strong", score: 95 },
    { skill: "React", status: "Strong", score: 92 },
    { skill: "Node.js", status: "Good", score: 65 },
    { skill: "Docker", status: "Missing", score: 20 },
    { skill: "AWS", status: "Missing", score: 15 },
    { skill: "System Design", status: "Missing", score: 25 },
  ],
  className = "" 
}) {
  const getStatusBadge = (status) => {
    switch (status) {
      case 'Strong':
        return {
          color: 'text-[#6B8E6B]',
          bg: 'bg-[#6B8E6B]/15 text-[#6B8E6B] border-[#6B8E6B]/30',
          barColor: 'bg-[#6B8E6B]',
          label: 'Strong'
        };
      case 'Good':
        return {
          color: 'text-[#C99545]',
          bg: 'bg-[#C99545]/15 text-[#C99545] border-[#C99545]/30',
          barColor: 'bg-[#C99545]',
          label: 'Good'
        };
      case 'Missing':
      default:
        return {
          color: 'text-[#B96A63]',
          bg: 'bg-[#B96A63]/15 text-[#B96A63] border-[#B96A63]/30',
          barColor: 'bg-[#B96A63]',
          label: 'Missing'
        };
    }
  };

  return (
    <div className={`rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 sm:p-6 shadow-warm-sm transition-colors duration-200 ${className}`}>
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-5 border-b border-[#E7E0D8] dark:border-[#413B34] gap-2">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#7C5C3B]/10 dark:bg-[#C49A6C]/10 text-[#7C5C3B] dark:text-[#C49A6C] flex items-center justify-center">
            <BarChart2 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Skill Gap Analysis
            </h3>
            <p className="text-xs text-[#77716B] dark:text-[#B9B0A5]">
              Direct proficiency comparison against target role benchmarks
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-[11px] text-[#77716B] dark:text-[#B9B0A5] self-start sm:self-auto">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#6B8E6B]" /> Strong
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#C99545]" /> Good
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#B96A63]" /> Missing
          </span>
        </div>
      </div>

      {/* Comparison List with Progress Bars */}
      <div className="space-y-4">
        {skillGaps.map((item) => {
          const badge = getStatusBadge(item.status);
          return (
            <div key={item.skill} className="space-y-1.5">
              
              <div className="flex items-center justify-between text-xs sm:text-sm">
                <span className="font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                  {item.skill}
                </span>

                <div className="flex items-center gap-3">
                  <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-md border ${badge.bg}`}>
                    {badge.label}
                  </span>
                  <span className="text-xs font-mono font-medium text-[#77716B] dark:text-[#B9B0A5] w-9 text-right">
                    {item.score}%
                  </span>
                </div>
              </div>

              {/* Progress track */}
              <div className="w-full h-2 rounded-full bg-[#F7F5F0] dark:bg-[#1F1D1A] overflow-hidden border border-[#E7E0D8]/60 dark:border-[#413B34]/60">
                <div
                  className={`h-full rounded-full transition-all duration-700 ease-out ${badge.barColor}`}
                  style={{ width: `${item.score}%` }}
                />
              </div>

              {item.description && (
                <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
                  {item.description}
                </p>
              )}

            </div>
          );
        })}
      </div>

    </div>
  );
}
