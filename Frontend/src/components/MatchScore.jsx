import React from 'react';
import { CheckCircle2 } from 'lucide-react';

export default function MatchScore({ 
  score = 82, 
  title = "Match Score", 
  subtitle = "Overall alignment with job requirements",
  size = 170,
  strokeWidth = 12,
  className = "" 
}) {
  // SVG circular calculations
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // Determine color based on score
  const getScoreColor = (val) => {
    if (val >= 80) return "text-[#6B8E6B] stroke-[#6B8E6B]";
    if (val >= 60) return "text-[#C99545] stroke-[#C99545]";
    return "text-[#B96A63] stroke-[#B96A63]";
  };

  const getScoreBadge = (val) => {
    if (val >= 80) return { label: "Strong Match", bg: "bg-[#6B8E6B]/15 text-[#6B8E6B]" };
    if (val >= 60) return { label: "Moderate Match", bg: "bg-[#C99545]/15 text-[#C99545]" };
    return { label: "Needs Improvement", bg: "bg-[#B96A63]/15 text-[#B96A63]" };
  };

  const badge = getScoreBadge(score);

  return (
    <div className={`flex flex-col items-center justify-center p-6 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-sm transition-colors duration-200 ${className}`}>
      
      {/* Title */}
      <div className="text-center mb-4">
        <h3 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
          {title}
        </h3>
        <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] mt-0.5">
          {subtitle}
        </p>
      </div>

      {/* SVG Circular Progress Gauge */}
      <div className="relative flex items-center justify-center my-2" style={{ width: size, height: size }}>
        <svg className="w-full h-full -rotate-90 transform" viewBox={`0 0 ${size} ${size}`}>
          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            className="stroke-[#E7E0D8] dark:stroke-[#413B34]"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress Indicator */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            className={`${getScoreColor(score)} transition-all duration-1000 ease-out`}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>

        {/* Center Percentage Display */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-4xl font-extrabold tracking-tight text-[#2F2A26] dark:text-[#F4EFE8]">
            {score}%
          </span>
          <span className="text-[11px] font-semibold text-[#77716B] dark:text-[#B9B0A5] uppercase tracking-wider mt-0.5">
            Compatibility
          </span>
        </div>
      </div>

      {/* Match Status Badge */}
      <div className="mt-4 flex flex-col items-center gap-1.5">
        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${badge.bg}`}>
          <CheckCircle2 className="w-3.5 h-3.5" />
          {badge.label}
        </span>
        <span className="text-xs text-[#77716B] dark:text-[#B9B0A5] text-center">
          5 of 6 essential technical competencies satisfied
        </span>
      </div>

    </div>
  );
}
