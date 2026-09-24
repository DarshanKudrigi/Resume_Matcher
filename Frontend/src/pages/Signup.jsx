import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FileCheck, ArrowRight, Eye, EyeOff } from 'lucide-react';
import ThemeToggle from '../components/ThemeToggle';
import { useApp } from '../context/AppContext';

export default function Signup() {
  const [fullName, setFullName] = useState('Darshan Sharma');
  const [email, setEmail] = useState('darshan.sharma@college.edu');
  const [password, setPassword] = useState('password123');
  const [confirmPassword, setConfirmPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const { setUser, showToast } = useApp();

  const handleSignup = (e) => {
    e.preventDefault();
    if (!fullName.trim() || !email.trim() || !password.trim()) {
      showToast('Please fill out all required fields', 'error');
      return;
    }
    if (password !== confirmPassword) {
      showToast('Passwords do not match', 'error');
      return;
    }
    if (password.length < 6) {
      showToast('Password should be at least 6 characters', 'error');
      return;
    }

    setUser((prev) => ({
      ...prev,
      name: fullName,
      email: email,
    }));

    showToast('Account created successfully!');
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex flex-col justify-center bg-[#F7F5F0] dark:bg-[#1F1D1A] transition-colors p-4 sm:p-6 lg:p-8">
      
      {/* Top bar with theme toggle */}
      <div className="absolute top-5 right-5 z-20">
        <ThemeToggle />
      </div>

      <div className="max-w-md w-full mx-auto rounded-2xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-lg p-8 sm:p-10">
        
        {/* Brand Logo */}
        <div className="flex items-center gap-2.5 mb-6">
          <div className="w-10 h-10 rounded-xl bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] flex items-center justify-center shadow-warm-sm">
            <FileCheck className="w-5 h-5 stroke-[2.2]" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-[#2F2A26] dark:text-[#F4EFE8]">
              Resume<span className="text-[#7C5C3B] dark:text-[#C49A6C]">Mate</span>
            </span>
            <span className="text-[10px] block font-semibold text-[#77716B] dark:text-[#B9B0A5] tracking-wider uppercase">
              Student Registration
            </span>
          </div>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
            Create an Account
          </h2>
          <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] mt-1">
            Sign up to benchmark your resume and evaluate skill gaps
          </p>
        </div>

        <form onSubmit={handleSignup} className="space-y-4">
          
          {/* Full Name */}
          <div>
            <label className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] block mb-1">
              Full Name
            </label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Darshan Sharma"
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B] dark:focus:border-[#C49A6C]"
            />
          </div>

          {/* Email */}
          <div>
            <label className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] block mb-1">
              College / Work Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="darshan@college.edu"
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B] dark:focus:border-[#C49A6C]"
            />
          </div>

          {/* Password */}
          <div>
            <label className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] block mb-1">
              Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 6 characters"
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B] dark:focus:border-[#C49A6C] pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[#77716B]"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] block mb-1">
              Confirm Password
            </label>
            <input
              type={showPassword ? "text" : "password"}
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter password"
              className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B] dark:focus:border-[#C49A6C]"
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="w-full py-2.5 px-4 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] dark:hover:bg-[#B38757] font-semibold text-xs sm:text-sm shadow-warm-sm transition-all flex items-center justify-center gap-2 mt-2"
          >
            <span>Create Account</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="text-center mt-6 text-xs text-[#77716B] dark:text-[#B9B0A5]">
          <span>Already have an account? </span>
          <Link to="/login" className="font-semibold text-[#7C5C3B] dark:text-[#C49A6C] hover:underline">
            Sign In
          </Link>
        </div>

      </div>

    </div>
  );
}
