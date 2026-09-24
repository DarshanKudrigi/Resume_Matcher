import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Sparkles, Bot, User, RotateCcw } from 'lucide-react';
import { chatResponses } from '../data/mockData';

export default function ChatBox() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'assistant',
      text: "Hello Darshan! I'm your ResumeMate assistant. Ask me anything about your 82% match score, missing skills, or how to tune your resume for Apex Cloud.",
      time: "Now"
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const suggestedQuestions = [
    "Why is my match score 82%?",
    "What skills am I missing?",
    "How can I improve my resume?",
    "What should I learn first?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen, isTyping]);

  const handleSendMessage = (textToSend) => {
    const query = textToSend || inputValue;
    if (!query.trim()) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    // Look for preset response or generate intelligent mock response
    setTimeout(() => {
      const lower = query.toLowerCase();
      const matched = chatResponses.find(r => 
        r.triggers.some(t => lower.includes(t)) || lower.includes(r.question.toLowerCase())
      );

      let replyText = "";
      if (matched) {
        replyText = matched.response;
      } else if (lower.includes("ats")) {
        replyText = "Your ATS compatibility is currently 86%. Ensure you integrate keywords like 'Docker' and 'AWS' within your project descriptions.";
      } else if (lower.includes("experience") || lower.includes("internship")) {
        replyText = "Emphasize quantifiable achievements in your engineering internship, such as component render times or API integrations.";
      } else {
        replyText = `Based on your resume and the Apex Cloud posting: focus on highlighting your React hooks, and consider building a small project with Docker and AWS S3 to close the top 2 skill gaps!`;
      }

      const botMessage = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: replyText,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);
    }, 550);
  };

  const handleResetChat = () => {
    setMessages([
      {
        id: 1,
        sender: 'assistant',
        text: "Chat reset. How can I help you analyze your resume or skill gaps today?",
        time: "Now"
      }
    ]);
  };

  return (
    <aside aria-label="ResumeMate Assistant Chat" className="fixed bottom-5 right-5 z-40">
      
      {/* Floating Launcher Button */}
      {!isOpen && (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-2.5 px-4 py-3 rounded-full bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] shadow-warm-lg hover:shadow-xl hover:scale-105 transition-all duration-200 font-semibold text-xs sm:text-sm border border-[#F7F5F0]/20"
        >
          <Sparkles className="w-4 h-4" />
          <span>Ask ResumeMate</span>
          <span className="w-2 h-2 rounded-full bg-[#6B8E6B] animate-pulse" />
        </button>
      )}

      {/* Expanded Chat Window */}
      {isOpen && (
        <div className="w-[calc(100vw-2.5rem)] sm:w-96 h-[510px] max-h-[85vh] rounded-2xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] shadow-warm-lg flex flex-col overflow-hidden transition-all duration-200 animate-scale-up">
          
          {/* Chat Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-[#F7F5F0] dark:bg-[#1F1D1A] border-b border-[#E7E0D8] dark:border-[#413B34]">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] flex items-center justify-center">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs sm:text-sm font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
                  Ask ResumeMate
                </h4>
                <p className="text-[10px] text-[#77716B] dark:text-[#B9B0A5]">
                  AI-Assisted Skill Gap Advisor (Mock)
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={handleResetChat}
                className="p-1.5 rounded-md text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] transition-colors"
                title="Reset conversation"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-md text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] transition-colors"
                title="Close chat"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 p-3.5 overflow-y-auto space-y-3 text-xs">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'assistant' && (
                  <div className="w-6 h-6 rounded-full bg-[#7C5C3B]/15 dark:bg-[#C49A6C]/20 text-[#7C5C3B] dark:text-[#C49A6C] flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                )}

                <div
                  className={`max-w-[82%] rounded-xl px-3.5 py-2.5 leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] rounded-tr-none'
                      : 'bg-[#F7F5F0] dark:bg-[#1F1D1A] text-[#2F2A26] dark:text-[#F4EFE8] border border-[#E7E0D8]/70 dark:border-[#413B34] rounded-tl-none'
                  }`}
                >
                  <p className="whitespace-pre-line">{msg.text}</p>
                  <span className={`text-[9px] block mt-1 ${msg.sender === 'user' ? 'text-[#F7F5F0]/70 dark:text-[#1F1D1A]/70 text-right' : 'text-[#77716B] dark:text-[#B9B0A5]'}`}>
                    {msg.time}
                  </span>
                </div>

                {msg.sender === 'user' && (
                  <div className="w-6 h-6 rounded-full bg-[#A67C52]/20 text-[#7C5C3B] dark:text-[#C49A6C] flex items-center justify-center shrink-0 mt-0.5">
                    <User className="w-3.5 h-3.5" />
                  </div>
                )}
              </div>
            ))}

            {isTyping && (
              <div className="flex items-center gap-2 text-xs text-[#77716B] dark:text-[#B9B0A5]">
                <div className="w-6 h-6 rounded-full bg-[#7C5C3B]/15 dark:bg-[#C49A6C]/20 text-[#7C5C3B] dark:text-[#C49A6C] flex items-center justify-center shrink-0">
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="p-2.5 rounded-xl bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#7C5C3B] dark:bg-[#C49A6C] animate-bounce" />
                  <span className="w-1.5 h-1.5 rounded-full bg-[#7C5C3B] dark:bg-[#C49A6C] animate-bounce [animation-delay:0.2s]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-[#7C5C3B] dark:bg-[#C49A6C] animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Preset Prompts */}
          <div className="px-3 py-2 border-t border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/50 dark:bg-[#1F1D1A]/50">
            <span className="text-[10px] font-semibold text-[#77716B] dark:text-[#B9B0A5] uppercase tracking-wider block mb-1.5">
              Suggested Questions:
            </span>
            <div className="flex flex-wrap gap-1.5 max-h-20 overflow-y-auto">
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSendMessage(q)}
                  className="text-[11px] px-2.5 py-1 rounded-md border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#2F2A26] dark:text-[#F4EFE8] hover:border-[#7C5C3B] dark:hover:border-[#C49A6C] transition-colors text-left"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Input Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage(inputValue);
            }}
            className="p-2.5 border-t border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] flex items-center gap-2"
          >
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about your resume..."
              className="flex-1 px-3 py-2 rounded-lg text-xs border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/60 dark:bg-[#1F1D1A]/60 text-[#2F2A26] dark:text-[#F4EFE8] placeholder-[#77716B] focus:outline-none focus:border-[#7C5C3B] dark:focus:border-[#C49A6C]"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isTyping}
              className="p-2 rounded-lg bg-[#7C5C3B] dark:bg-[#C49A6C] text-[#F7F5F0] dark:text-[#1F1D1A] disabled:opacity-50 transition-colors"
              aria-label="Send message"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>

        </div>
      )}

    </aside>
  );
}
