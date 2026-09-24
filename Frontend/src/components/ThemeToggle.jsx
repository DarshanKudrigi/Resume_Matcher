import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function ThemeToggle({ className = "" }) {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={isDark ? "Switch to light theme" : "Switch to dark theme"}
      title={isDark ? "Switch to light theme" : "Switch to dark theme"}
      className={`p-2 rounded-lg border transition-colors duration-200 flex items-center justify-center
        bg-[#FFFFFF] dark:bg-[#292622] 
        text-[#2F2A26] dark:text-[#F4EFE8] 
        border-[#E7E0D8] dark:border-[#413B34] 
        hover:border-[#A67C52] dark:hover:border-[#C49A6C] 
        focus:outline-none focus:ring-2 focus:ring-[#7C5C3B]/20 dark:focus:ring-[#C49A6C]/20 ${className}`}
    >
      {isDark ? (
        <Sun className="w-4 h-4 text-[#D8B08A] hover:text-[#F4EFE8] transition-colors" />
      ) : (
        <Moon className="w-4 h-4 text-[#7C5C3B] hover:text-[#2F2A26] transition-colors" />
      )}
    </button>
  );
}
