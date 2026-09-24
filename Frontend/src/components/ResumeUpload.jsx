import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, Trash2 } from 'lucide-react';
import { useApp } from '../context/AppContext';

export default function ResumeUpload({ className = "" }) {
  const { uploadedFile, handleFileUpload, removeFile, showToast } = useApp();
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      processFile(file);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      processFile(file);
    }
  };

  const processFile = (file) => {
    // Validate format
    const validExtensions = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'];
    const ext = file.name.split('.').pop().toLowerCase();
    
    if (!validExtensions.includes(ext)) {
      showToast("Unsupported format. Please upload PDF, DOC, DOCX, JPG, or PNG.", "error");
      return;
    }

    // 10 MB limit
    if (file.size > 10 * 1024 * 1024) {
      showToast("File exceeds 10 MB limit.", "error");
      return;
    }

    handleFileUpload(file);
  };

  const triggerInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className={`rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] p-5 sm:p-6 shadow-warm-sm transition-colors duration-200 ${className}`}>
      
      {/* Card Header */}
      <div className="flex items-center justify-between pb-4 border-b border-[#E7E0D8] dark:border-[#413B34] mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#F7F5F0] dark:bg-[#1F1D1A] border border-[#E7E0D8] dark:border-[#413B34] flex items-center justify-center text-[#7C5C3B] dark:text-[#C49A6C]">
            <UploadCloud className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-[#2F2A26] dark:text-[#F4EFE8]">
              Upload Resume
            </h2>
            <p className="text-xs sm:text-sm text-[#77716B] dark:text-[#B9B0A5]">
              Drop your resume here or browse from your device.
            </p>
          </div>
        </div>

        {uploadedFile && (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#6B8E6B]/15 text-[#6B8E6B]">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Ready for Analysis
          </span>
        )}
      </div>

      {/* Hidden native input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
        onChange={handleFileChange}
        className="hidden"
      />

      {/* Upload Zone or Selected File View */}
      {!uploadedFile ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={triggerInput}
          className={`border-2 border-dashed rounded-xl p-8 sm:p-10 text-center cursor-pointer transition-all duration-200 ${
            isDragging
              ? 'border-[#7C5C3B] dark:border-[#C49A6C] bg-[#F7F5F0] dark:bg-[#1F1D1A]'
              : 'border-[#E7E0D8] dark:border-[#413B34] hover:border-[#A67C52] dark:hover:border-[#C49A6C] bg-[#F7F5F0]/40 dark:bg-[#1F1D1A]/40'
          }`}
        >
          <div className="w-14 h-14 mx-auto mb-3 rounded-full bg-[#FFFFFF] dark:bg-[#292622] border border-[#E7E0D8] dark:border-[#413B34] flex items-center justify-center text-[#7C5C3B] dark:text-[#C49A6C] shadow-warm-sm">
            <UploadCloud className="w-7 h-7" />
          </div>
          
          <h3 className="text-sm font-semibold text-[#2F2A26] dark:text-[#F4EFE8] mb-1">
            Drop your resume here or <span className="text-[#7C5C3B] dark:text-[#C49A6C] underline underline-offset-2">browse</span>
          </h3>
          
          <p className="text-xs text-[#77716B] dark:text-[#B9B0A5] mb-4">
            Accepted formats: <span className="font-medium text-[#2F2A26] dark:text-[#F4EFE8]">PDF, DOC, DOCX, JPG and PNG</span>
          </p>

          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-[#FFFFFF] dark:bg-[#292622] border border-[#E7E0D8] dark:border-[#413B34] text-[11px] text-[#77716B] dark:text-[#B9B0A5]">
            <span>Maximum file size: 10 MB</span>
          </div>
        </div>
      ) : (
        /* Selected File Card State */
        <div className="space-y-4">
          <div className="p-4 rounded-xl border border-[#E7E0D8] dark:border-[#413B34] bg-[#F7F5F0]/70 dark:bg-[#1F1D1A]/70 flex items-center justify-between gap-4">
            
            <div className="flex items-center gap-3.5 min-w-0">
              <div className="w-11 h-11 rounded-lg bg-[#FFFFFF] dark:bg-[#292622] border border-[#E7E0D8] dark:border-[#413B34] flex items-center justify-center text-[#7C5C3B] dark:text-[#C49A6C] shrink-0 shadow-warm-sm">
                <FileText className="w-6 h-6" />
              </div>

              <div className="min-w-0">
                <h4 className="text-sm font-semibold text-[#2F2A26] dark:text-[#F4EFE8] truncate">
                  {uploadedFile.name}
                </h4>
                <div className="flex items-center gap-2.5 mt-0.5 text-xs text-[#77716B] dark:text-[#B9B0A5]">
                  <span className="uppercase font-medium text-[10px] px-1.5 py-0.2 rounded bg-[#FFFFFF] dark:bg-[#292622] border border-[#E7E0D8] dark:border-[#413B34]">
                    {uploadedFile.type.split('/').pop()}
                  </span>
                  <span>•</span>
                  <span>{uploadedFile.size}</span>
                  <span>•</span>
                  <span className="text-[#6B8E6B] font-medium flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Uploaded successfully
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={triggerInput}
                className="text-xs px-3 py-1.5 rounded-lg border border-[#E7E0D8] dark:border-[#413B34] bg-[#FFFFFF] dark:bg-[#292622] text-[#77716B] dark:text-[#B9B0A5] hover:text-[#2F2A26] dark:hover:text-[#F4EFE8] transition-colors"
                title="Replace file"
              >
                Change
              </button>
              <button
                type="button"
                onClick={removeFile}
                className="p-1.5 rounded-lg border border-[#B96A63]/30 bg-[#FFFFFF] dark:bg-[#292622] text-[#B96A63] hover:bg-[#B96A63]/10 transition-colors"
                title="Remove file"
                aria-label="Remove uploaded resume"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between text-xs text-[#77716B] dark:text-[#B9B0A5] pt-1 gap-2">
            <span>Accepted formats: PDF, DOC, DOCX, JPG and PNG (Max 10 MB)</span>
            <span className="text-[11px] text-[#A67C52] dark:text-[#D8B08A]">Ready to match against job description</span>
          </div>
        </div>
      )}

    </div>
  );
}
