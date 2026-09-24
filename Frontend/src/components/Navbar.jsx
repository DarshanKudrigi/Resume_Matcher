import React, { useState, useRef, useEffect } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { 
  FileCheck, 
  LayoutDashboard, 
  Sparkles, 
  FileText, 
  FolderKanban, 
  History as HistoryIcon, 
  Bell, 
  User, 
  Settings, 
  LogOut, 
  Menu, 
  X,
  CheckCircle2
} from 'lucide-react';
import ThemeToggle from './ThemeToggle';
import { useApp } from '../context/AppContext';

export default function Navbar() {
  const { user } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const notifRef = useRef(null);
  const profileRef = useRef(null);

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setNotificationsOpen(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setProfileMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Analyzer', path: '/analyzer', icon: Sparkles },
    { name: 'Resume Builder', path: '/builder', icon: FileText },
    { name: 'My Resumes', path: '/my-resumes', icon: FolderKanban },
    { name: 'History', path: '/history', icon: HistoryIcon },
  ];

  return (
    <header className="sticky top-0 z-40 bg-[#FFFFFF]/90 dark:bg-[#292622]/90 backdrop-blur-md border-b border-[#E7E0D8] dark:border-[#413B34] transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Left: Brand Logo */}
          <div className="flex items-center gap-8">
            <Link to="/dashboard" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] flex items-center justify-center shadow-warm-sm group-hover:opacity-95 transition-opacity">
                <FileCheck className="w-5 h-5 stroke-[2.2]" />
              </div>
              <div className="flex flex-col">
                <span className="text-lg font-bold tracking-tight text-[#2F2A26] dark:text-[#F4EFE8]">
                  Resume<span className="text-[#7C5C3B] dark:text-[#C49A6C]">Mate</span>
                </span>
                <span className="text-[10px] -mt-1 font-medium text-[#77716B] dark:text-[#B9B0A5] tracking-wider uppercase">
                  College Project
                </span>
              </div>
            </Link>

            {/* Desktop Navigation Links */}
            <nav className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => {
                const Icon = link.icon;
                return (
                  <NavLink
                    key={link.path}
                    to={link.path}
                    className={({ isActive }) =>
                      `flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                        isActive
                          ? 'bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#7C5C3B] dark:text-[#C49A6C] font-semibold border border-[#E7E0D8]/60 dark:border-[#413B34]'
                          : 'text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] hover:bg-[#F7F5F0]/60 dark:hover:bg-[#1F1D1A]/50'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 opacity-80" />
                    <span>{link.name}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>

          {/* Right: Theme Toggle, Notifications, User Menu */}
          <div className="flex items-center gap-2.5">
            
            {/* Theme Toggle */}
            <ThemeToggle />

            {/* Notifications Dropdown */}
            <div className="relative" ref={notifRef}>
              <button
                type="button"
                onClick={() => setNotificationsOpen(!notificationsOpen)}
                className="relative p-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] hover:border-[#A67C52] dark:hover:border-[#C49A6C] transition-colors"
                aria-label="Notifications"
                title="Notifications"
              >
                <Bell className="w-4 h-4" />
                {user.notifications && user.notifications.some(n => n.unread) && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[#C99545]" />
                )}
              </button>

              {notificationsOpen && (
                <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-lg p-3 z-50 animate-fade-in">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#E7E0D8] dark:border-[#413B34]">
                    <span className="text-sm font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                      Notifications
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#77716B] dark:text-[#B9B0A5]">
                      Mock Feed
                    </span>
                  </div>
                  <div className="space-y-2 max-h-72 overflow-y-auto">
                    {user.notifications?.map((item) => (
                      <div
                        key={item.id}
                        className={`p-2.5 rounded-lg text-xs transition-colors flex gap-2.5 items-start ${
                          item.unread
                            ? 'bg-[#F7F5F0] dark:bg-[#1F1D1A]/80 border-l-2 border-[#7C5C3B] dark:border-[#C49A6C]'
                            : 'bg-transparent opacity-80'
                        }`}
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 mt-0.5 text-[#6B8E6B] shrink-0" />
                        <div className="flex-1">
                          <p className="font-medium text-[#2F2A26] dark:text-[#F4EFE8]">{item.title}</p>
                          <p className="text-[#77716B] dark:text-[#B9B0A5] mt-0.5 leading-relaxed">{item.message}</p>
                          <span className="text-[10px] text-[#A67C52] dark:text-[#D8B08A] mt-1 inline-block">{item.time}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Profile Avatar & Name */}
            <div className="relative" ref={profileRef}>
              <button
                type="button"
                onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                className="flex items-center gap-2 pl-1.5 pr-2.5 py-1 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] hover:border-[#A67C52] dark:hover:border-[#C49A6C] transition-colors text-left"
              >
                <div className="w-7 h-7 rounded-full bg-[#D8A48F]/40 dark:bg-[#C49A6C]/30 text-[#7C5C3B] dark:text-[#D8B08A] font-bold text-xs flex items-center justify-center border border-[#7C5C3B]/20 dark:border-[#C49A6C]/30">
                  DS
                </div>
                <div className="hidden sm:flex flex-col text-left leading-tight">
                  <span className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                    {user.name.split(' ')[0]}
                  </span>
                  <span className="text-[10px] text-[#77716B] dark:text-[#B9B0A5]">
                    Student
                  </span>
                </div>
              </button>

              {profileMenuOpen && (
                <div className="absolute right-0 mt-2 w-52 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-lg py-1.5 z-50">
                  <div className="px-3.5 py-2 border-b border-[#E7E0D8] dark:border-[#413B34]">
                    <p className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] truncate">{user.name}</p>
                    <p className="text-[11px] text-[#77716B] dark:text-[#B9B0A5] truncate">{user.email}</p>
                  </div>
                  <Link
                    to="/settings"
                    onClick={() => setProfileMenuOpen(false)}
                    className="flex items-center gap-2 px-3.5 py-2 text-xs text-[#2F2A26] dark:text-[#F4EFE8] hover:bg-[#F7F5F0] dark:hover:bg-[#1F1D1A]"
                  >
                    <User className="w-3.5 h-3.5 text-[#7C5C3B] dark:text-[#C49A6C]" />
                    Profile & Settings
                  </Link>
                  <Link
                    to="/my-resumes"
                    onClick={() => setProfileMenuOpen(false)}
                    className="flex items-center gap-2 px-3.5 py-2 text-xs text-[#2F2A26] dark:text-[#F4EFE8] hover:bg-[#F7F5F0] dark:hover:bg-[#1F1D1A]"
                  >
                    <FolderKanban className="w-3.5 h-3.5 text-[#7C5C3B] dark:text-[#C49A6C]" />
                    My Saved Resumes
                  </Link>
                  <div className="border-t border-[#E7E0D8] dark:border-[#413B34] my-1" />
                  <button
                    type="button"
                    onClick={() => {
                      setProfileMenuOpen(false);
                      navigate('/login');
                    }}
                    className="w-full flex items-center gap-2 px-3.5 py-2 text-xs text-[#B96A63] hover:bg-[#B96A63]/10"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    Sign Out (Mock)
                  </button>
                </div>
              )}
            </div>

            {/* Mobile Hamburger Toggle */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8]"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] px-4 pt-3 pb-5 space-y-1.5">
          {navLinks.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium ${
                    isActive
                      ? 'bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#7C5C3B] dark:text-[#C49A6C] font-semibold'
                      : 'text-[#77716B] dark:text-[#B9B0A5]'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{link.name}</span>
              </NavLink>
            );
          })}
          <div className="pt-2 border-t border-[#E7E0D8] dark:border-[#413B34]">
            <Link
              to="/settings"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm text-[#77716B] dark:text-[#B9B0A5]"
            >
              <Settings className="w-4 h-4" />
              <span>Settings</span>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
