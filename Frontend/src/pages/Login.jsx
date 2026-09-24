import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  FileCheck, 
  Eye, 
  EyeOff, 
  Sparkles, 
  CheckCircle2, 
  ArrowRight, 
  ShieldCheck 
} from 'lucide-react';
import ThemeToggle from '../components/ThemeToggle';
import { useApp } from '../context/AppContext';

export default function Login() {
  const [email, setEmail] = useState('darshan.sharma@college.edu');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [forgotModalOpen, setForgotModalOpen] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetSent, setResetSent] = useState(false);
  const navigate = useNavigate();
  const { showToast } = useApp();

  const handleSignIn = (e) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      showToast('Please enter both email and password', 'error');
      return;
    }
    showToast('Signed in successfully as Darshan!');
    navigate('/dashboard');
  };

  const handleGoogleMock = () => {
    showToast('Signed in with Google (Mock)');
    navigate('/dashboard');
  };

  const handleForgotSubmit = (e) => {
    e.preventDefault();
    if (!resetEmail.trim()) {
      showToast('Please enter your email', 'error');
      return;
    }
    setResetSent(true);
    showToast('Reset instructions sent to your email (Mock)');
    setTimeout(() => {
      setForgotModalOpen(false);
      setResetSent(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen flex flex-col justify-center bg-[#F7F5F0] dark:bg-[#1F1D1A] transition-colors p-4 sm:p-6 lg:p-8">
      
      {/* Top bar with theme toggle */}
      <div className="absolute top-5 right-5 z-20">
        <ThemeToggle />
      </div>

      <div className="max-w-4xl w-full mx-auto rounded-2xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-lg overflow-hidden grid grid-cols-1 md:grid-cols-2">
        
        {/* Left Section: Short Project Introduction */}
        <div className="p-8 sm:p-10 bg-[#F7F5F0]/80 dark:bg-[#1F1D1A]/80 border-b md:border-b-0 md:border-r border-[#E7E0D8] dark:border-[#413B34] flex flex-col justify-between">
          <div>
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
                  College Project Edition
                </span>
              </div>
            </div>

            <div className="space-y-3 mb-8">
              <h2 className="text-2xl sm:text-3xl font-bold text-[#2F2A26] dark:text-[#F4EFE8] leading-tight">
                Build better resumes. <br />
                <span className="text-[#7C5C3B] dark:text-[#C49A6C]">Find your skill gaps.</span>
              </h2>
              <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5] leading-relaxed">
                AI-Based Resume–Job Description Matching and Skill Gap Analysis System designed for college graduates and aspiring software engineers.
              </p>
            </div>

            {/* Feature Highlights */}
            <div className="space-y-3 text-xs text-[#2F2A26] dark:text-[#F4EFE8]">
              <div className="flex items-center gap-2.5">
                <div className="w-5 h-5 rounded-full bg-[#6B8E6B]/15 text-[#6B8E6B] flex items-center justify-center shrink-0">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                </div>
                <span>Job Description keyword alignment & match score</span>
              </div>
              <div className="flex items-center gap-2.5">
                <div className="w-5 h-5 rounded-full bg-[#7C5C3B]/15 dark:bg-[#C49A6C]/20 text-[#7C5C3B] dark:text-[#C49A6C] flex items-center justify-center shrink-0">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>
                <span>Skill gap identification & curated study recommendations</span>
              </div>
              <div className="flex items-center gap-2.5">
                <div className="w-5 h-5 rounded-full bg-[#C99545]/15 text-[#C99545] flex items-center justify-center shrink-0">
                  <ShieldCheck className="w-3.5 h-3.5" />
                </div>
                <span>Interactive Resume Builder with ATS compatibility check</span>
              </div>
            </div>
          </div>

          <div className="pt-8 border-t border-[#E7E0D8] dark:border-[#413B34] text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
            <span>Developed by Darshan • Final Year Capstone Prototype</span>
          </div>
        </div>

        {/* Right Section: Login Form */}
        <div className="p-8 sm:p-10 flex flex-col justify-center">
          <div className="mb-6">
            <h3 className="text-xl font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Sign in to ResumeMate
            </h3>
            <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] mt-1">
              Enter your credentials or continue with mock profile
            </p>
          </div>

          <form onSubmit={handleSignIn} className="space-y-4">
            
            {/* Email Field */}
            <div>
              <label className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8] block mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@college.edu"
                className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B] dark:focus:border-[#C49A6C] transition-all"
              />
            </div>

            {/* Password Field with Show/Hide */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => setForgotModalOpen(true)}
                  className="text-xs text-[#7C5C3B] dark:text-[#C49A6C] hover:underline"
                >
                  Forgot password?
                </button>
              </div>

              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50 text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B] dark:focus:border-[#C49A6C] transition-all pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#77716B] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8]"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="w-full py-2.5 px-4 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] dark:hover:bg-[#B38757] font-semibold text-xs sm:text-sm shadow-warm-sm transition-all flex items-center justify-center gap-2"
            >
              <span>Sign In</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            {/* Divider */}
            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[#E7E0D8] dark:border-[#413B34]" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="px-2 bg-[#FFFFFF] dark:bg-[#292622] text-[#77716B] dark:text-[#B9B0A5]">
                  Or continue with
                </span>
              </div>
            </div>

            {/* Continue with Google (Mock) */}
            <button
              type="button"
              onClick={handleGoogleMock}
              className="w-full py-2.5 px-4 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] hover:bg-[#F7F5F0] dark:hover:bg-[#1F1D1A] text-xs sm:text-sm font-semibold text-[#2F2A26] dark:text-[#F4EFE8] transition-colors flex items-center justify-center gap-2.5 shadow-warm-sm"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
              </svg>
              <span>Continue with Google (Mock)</span>
            </button>

          </form>

          {/* Footer link to Signup */}
          <div className="text-center mt-6 text-xs text-[#77716B] dark:text-[#B9B0A5]">
            <span>Don't have an account? </span>
            <Link to="/signup" className="font-semibold text-[#7C5C3B] dark:text-[#C49A6C] hover:underline">
              Create account
            </Link>
          </div>

        </div>

      </div>

      {/* Forgot Password Modal */}
      {forgotModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#2F2A26]/50 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-sm rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-lg p-6 space-y-4">
            <h4 className="text-base font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Reset Password
            </h4>
            <p className="text-xs text-[#77716B] dark:text-[#B9B0A5]">
              Enter your student email and we will send you password reset instructions.
            </p>
            {resetSent ? (
              <div className="p-3 rounded-lg bg-[#6B8E6B]/15 text-[#6B8E6B] text-xs font-medium text-center">
                Password reset link sent to your email!
              </div>
            ) : (
              <form onSubmit={handleForgotSubmit} className="space-y-3">
                <input
                  type="email"
                  required
                  value={resetEmail}
                  onChange={(e) => setResetEmail(e.target.value)}
                  placeholder="darshan.sharma@college.edu"
                  className="w-full px-3 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-transparent text-[#2F2A26] dark:text-[#F4EFE8]"
                />
                <div className="flex gap-2 justify-end">
                  <button
                    type="button"
                    onClick={() => setForgotModalOpen(false)}
                    className="px-3 py-1.5 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] text-[#77716B]"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-3.5 py-1.5 text-xs rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] font-semibold"
                  >
                    Send Reset Link
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
