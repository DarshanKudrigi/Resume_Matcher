import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  Settings as SettingsIcon, 
  ShieldCheck, 
  LogOut, 
  Save, 
  GraduationCap, 
  RotateCcw 
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ThemeToggle from '../components/ThemeToggle';
import ChatBox from '../components/ChatBox';
import { useApp } from '../context/AppContext';
import { useTheme } from '../context/ThemeContext';

export default function Settings() {
  const { user, setUser, showToast } = useApp();
  const { theme } = useTheme();
  const navigate = useNavigate();

  const [name, setName] = useState(user.name || "Darshan Sharma");
  const [email, setEmail] = useState(user.email || "darshan.sharma@college.edu");
  const [phone, setPhone] = useState(user.phone || "+91 98765 43210");
  const [location, setLocation] = useState(user.location || "Mumbai, India");
  const [notifyMatch, setNotifyMatch] = useState(true);
  const [notifyTips, setNotifyTips] = useState(true);

  const handleSaveProfile = (e) => {
    e.preventDefault();
    setUser((prev) => ({
      ...prev,
      name,
      email,
      phone,
      location
    }));
    showToast("Profile information updated successfully!");
  };

  const handleLogout = () => {
    showToast("Signed out successfully (Mock)", "info");
    navigate('/login');
  };

  const handleResetData = () => {
    localStorage.clear();
    showToast("Reset all cached student mock data", "info");
    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#2F2A26] dark:text-[#F4EFE8] transition-colors">
      <Navbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Page Header */}
        <div className="pb-4 border-b border-[#E7E0D8] dark:border-[#413B34]">
          <span className="text-xs font-semibold text-[#7C5C3B] dark:text-[#C49A6C] uppercase tracking-wider block mb-1">
            Account Preferences
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#2F2A26] dark:text-[#F4EFE8]">
            Profile & Settings
          </h1>
          <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5] mt-1">
            Manage your student profile details, appearance themes, and mock notification preferences.
          </p>
        </div>

        {/* 1. Profile Section */}
        <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 sm:p-6 shadow-warm-sm space-y-4">
          <div className="flex items-center gap-2.5 pb-3 border-b border-[#E7E0D8] dark:border-[#413B34]">
            <User className="w-5 h-5 text-[#7C5C3B] dark:text-[#C49A6C]" />
            <h2 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Personal Information
            </h2>
          </div>

          <form onSubmit={handleSaveProfile} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] block mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] block mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] block mb-1">
                  Phone Number
                </label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] block mb-1">
                  Location
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
                />
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                className="px-4 py-2 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] text-xs font-bold transition-colors flex items-center gap-1.5 shadow-warm-sm"
              >
                <Save className="w-3.5 h-3.5" />
                <span>Save Changes</span>
              </button>
            </div>
          </form>
        </div>

        {/* 2. Preferences: Theme & Notifications */}
        <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 sm:p-6 shadow-warm-sm space-y-4">
          <div className="flex items-center gap-2.5 pb-3 border-b border-[#E7E0D8] dark:border-[#413B34]">
            <SettingsIcon className="w-5 h-5 text-[#7C5C3B] dark:text-[#C49A6C]" />
            <h2 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Preferences
            </h2>
          </div>

          {/* Theme Toggle row */}
          <div className="flex items-center justify-between py-2 border-b border-[#E7E0D8]/60 dark:border-[#413B34]/60">
            <div>
              <p className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                Theme Mode
              </p>
              <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
                Switch between warm light beige and warm charcoal brown palette
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-[#77716B] capitalize">{theme} Mode</span>
              <ThemeToggle />
            </div>
          </div>

          {/* Notification toggles */}
          <div className="flex items-center justify-between py-2 border-b border-[#E7E0D8]/60 dark:border-[#413B34]/60">
            <div>
              <p className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                Analysis Notifications
              </p>
              <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
                Alert when a job description match finishes computing
              </p>
            </div>
            <input
              type="checkbox"
              checked={notifyMatch}
              onChange={(e) => setNotifyMatch(e.target.checked)}
              className="w-4 h-4 rounded text-[#7C5C3B] focus:ring-[#7C5C3B] accent-[#7C5C3B]"
            />
          </div>

          <div className="flex items-center justify-between py-2">
            <div>
              <p className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                Skill Gap & ATS Tips
              </p>
              <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
                Show personalized recommendations to boost resume match rates
              </p>
            </div>
            <input
              type="checkbox"
              checked={notifyTips}
              onChange={(e) => setNotifyTips(e.target.checked)}
              className="w-4 h-4 rounded text-[#7C5C3B] focus:ring-[#7C5C3B] accent-[#7C5C3B]"
            />
          </div>
        </div>

        {/* 3. Account Actions */}
        <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 sm:p-6 shadow-warm-sm space-y-4">
          <div className="flex items-center gap-2.5 pb-3 border-b border-[#E7E0D8] dark:border-[#413B34]">
            <ShieldCheck className="w-5 h-5 text-[#7C5C3B] dark:text-[#C49A6C]" />
            <h2 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Account & Demo Controls
            </h2>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-1">
            <div>
              <p className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                Reset Application State
              </p>
              <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
                Clear browser storage and restore default student sample data
              </p>
            </div>
            <button
              type="button"
              onClick={handleResetData}
              className="px-3.5 py-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] text-xs font-semibold text-[#77716B] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] transition-colors flex items-center gap-1.5 self-start sm:self-auto"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Mock Data</span>
            </button>
          </div>

          <div className="pt-3 border-t border-[#E7E0D8] dark:border-[#413B34] flex justify-end">
            <button
              type="button"
              onClick={handleLogout}
              className="px-4 py-2 rounded-lg border border-[#B96A63]/40 bg-[#B96A63]/10 text-[#B96A63] hover:bg-[#B96A63]/20 text-xs font-bold transition-colors flex items-center gap-2"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out (Mock)</span>
            </button>
          </div>
        </div>

        {/* College Project Accreditation Box */}
        <div className="p-4 rounded-xl bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] text-xs text-[#77716B] dark:text-[#B9B0A5] flex items-start gap-3">
          <GraduationCap className="w-5 h-5 text-[#7C5C3B] dark:text-[#C49A6C] shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <p className="font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              College Project: AI-Based Resume–Job Description Matching and Skill Gap Analysis System
            </p>
            <p className="text-[11px]">
              Built with React, JavaScript, and Tailwind CSS. Client-side matching architecture demonstrating intelligent parsing, ATS compatibility checking, and personalized learning roadmaps.
            </p>
          </div>
        </div>

      </main>

      <Footer />
      <ChatBox />
    </div>
  );
}
