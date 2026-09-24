import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  ArrowRight, 
  Sparkles, 
  FileText, 
  Filter 
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ChatBox from '../components/ChatBox';
import { useApp } from '../context/AppContext';

export default function History() {
  const { history } = useApp();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterScore, setFilterScore] = useState('all'); // 'all' | '80plus' | 'under80'

  const filteredHistory = history.filter((item) => {
    const matchesSearch = item.jobTitle.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          item.company.toLowerCase().includes(searchTerm.toLowerCase());
    if (!matchesSearch) return false;
    if (filterScore === '80plus') return item.matchScore >= 80;
    if (filterScore === 'under80') return item.matchScore < 80;
    return true;
  });

  const handleInspect = () => {
    navigate('/results');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#2F2A26] dark:text-[#F4EFE8] transition-colors">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E7E0D8] dark:border-[#413B34] gap-4">
          <div>
            <span className="text-xs font-semibold text-[#7C5C3B] dark:text-[#C49A6C] uppercase tracking-wider block mb-1">
              Audit Log
            </span>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#2F2A26] dark:text-[#F4EFE8]">
              Analysis History
            </h1>
            <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5] mt-1">
              Previous resume comparisons, match benchmarks, and timeline progression.
            </p>
          </div>

          <button
            type="button"
            onClick={() => navigate('/analyzer')}
            className="px-4 py-2 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] hover:bg-[#66492C] text-xs font-bold shadow-warm-sm transition-colors flex items-center gap-1.5 self-start sm:self-auto"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>New Analysis</span>
          </button>
        </div>

        {/* Filter and Search Bar */}
        <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#77716B]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by job title or company..."
              className="w-full pl-9 pr-3.5 py-2 text-xs rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] placeholder-[#77716B] focus:outline-none focus:border-[#7C5C3B]"
            />
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto w-full sm:w-auto">
            <Filter className="w-3.5 h-3.5 text-[#77716B]" />
            <span className="text-xs text-[#77716B] dark:text-[#B9B0A5]">Filter:</span>
            <select
              value={filterScore}
              onChange={(e) => setFilterScore(e.target.value)}
              className="text-xs px-2.5 py-1.5 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] focus:outline-none focus:border-[#7C5C3B]"
            >
              <option value="all">All Matches</option>
              <option value="80plus">Strong Matches (≥ 80%)</option>
              <option value="under80">Below 80%</option>
            </select>
          </div>
        </div>

        {/* Clean Table / List */}
        <div className="rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 text-[#77716B] dark:text-[#B9B0A5] uppercase font-bold tracking-wider text-[10px]">
                  <th className="py-3 px-4 sm:px-6">Target Role</th>
                  <th className="py-3 px-4">Company</th>
                  <th className="py-3 px-4 text-center">Match Score</th>
                  <th className="py-3 px-4 text-center">ATS Score</th>
                  <th className="py-3 px-4">Analyzed</th>
                  <th className="py-3 px-4 sm:px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E7E0D8] dark:divide-[#413B34]">
                {filteredHistory.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-[#F7F5F0]/40 dark:hover:bg-[#1F1D1A]/40 transition-colors"
                  >
                    <td className="py-3.5 px-4 sm:px-6 font-semibold text-[#2F2A26] dark:text-[#F4EFE8]">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-[#7C5C3B] dark:text-[#C49A6C] shrink-0" />
                        <span>{item.jobTitle}</span>
                      </div>
                    </td>

                    <td className="py-3.5 px-4 text-[#77716B] dark:text-[#B9B0A5]">
                      {item.company}
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      <span className={`inline-flex items-center justify-center px-2.5 py-0.5 rounded-full font-bold text-xs ${
                        item.matchScore >= 80 
                          ? 'bg-[#6B8E6B]/15 text-[#6B8E6B]'
                          : 'bg-[#C99545]/15 text-[#C99545]'
                      }`}>
                        {item.matchScore}%
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-center font-mono text-[#2F2A26] dark:text-[#F4EFE8]">
                      {item.atsScore}%
                    </td>

                    <td className="py-3.5 px-4 text-[#77716B] dark:text-[#B9B0A5]">
                      {item.dateFormatted || item.date}
                    </td>

                    <td className="py-3.5 px-4 sm:px-6 text-right">
                      <button
                        type="button"
                        onClick={() => handleInspect(item)}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] hover:bg-[#7C5C3B] hover:text-[#F7F5F0] dark:hover:bg-[#C49A6C] dark:hover:text-[#1F1D1A] font-semibold text-xs transition-colors"
                      >
                        <span>View Results</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredHistory.length === 0 && (
            <div className="text-center py-10 text-xs text-[#77716B] dark:text-[#B9B0A5]">
              No past analyses match your search filter.
            </div>
          )}
        </div>

      </main>

      <Footer />
      <ChatBox />
    </div>
  );
}
