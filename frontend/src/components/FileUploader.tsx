import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, FileCheck, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react';

interface FileUploaderProps {
  onFileSelected: (file: File) => void;
  isLoading: boolean;
}

export const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelected, isLoading }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndProcess = (file: File) => {
    setErrorMsg(null);
    const validExtensions = ['pdf', 'docx', 'txt'];
    const ext = file.name.split('.').pop()?.toLowerCase();

    if (!ext || !validExtensions.includes(ext)) {
      setErrorMsg('Invalid file type. Please upload a PDF, DOCX, or TXT document.');
      return;
    }

    if (file.size > 15 * 1024 * 1024) { // 15MB limit
      setErrorMsg('File size exceeds 15MB. Please upload a smaller document.');
      return;
    }

    setSelectedFile(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndProcess(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndProcess(e.target.files[0]);
    }
  };

  const handleAnalyzeClick = () => {
    if (selectedFile) {
      onFileSelected(selectedFile);
    }
  };

  const loadSampleContract = () => {
    const sampleText = `SERVICES AGREEMENT
1. Payment Terms. Payment shall be made within 90 days of receipt of invoice. Late payments will incur a 15% monthly penalty.
2. Termination. Vendor may terminate this agreement at any time without notice. Client may not terminate without 60 days written consent.
3. Limitation of Liability. Vendor's total liability under this agreement shall be limited to $50. Client agrees to indemnify Vendor for all third-party claims without limit.
4. Governing Law. This agreement shall be governed by the laws of the State of California.
5. Confidentiality. Both parties agree to maintain the confidentiality of proprietary trade secrets for a period of 3 years from January 1st, 2024.`;

    const blob = new Blob([sampleText], { type: 'text/plain' });
    const sampleFile = new File([blob], 'Sample_Vendor_Agreement.txt', { type: 'text/plain' });
    validateAndProcess(sampleFile);
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-4">
      {/* Upload Box */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        tabIndex={0}
        role="button"
        aria-label="Upload legal contract"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            fileInputRef.current?.click();
          }
        }}
        className={`relative glass-panel-interactive p-8 sm:p-12 rounded-2xl text-center cursor-pointer border-2 border-dashed transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary-500 ${
          isDragOver
            ? 'border-primary-500 bg-primary-500/10 scale-[1.01]'
            : selectedFile
            ? 'border-emerald-500/50 bg-emerald-500/5'
            : 'border-surface-border hover:border-primary-500/40'
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.docx,.txt"
          className="hidden"
          disabled={isLoading}
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          {selectedFile ? (
            <div className="p-4 rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-glow-safe">
              <FileCheck className="w-10 h-10 animate-bounce" />
            </div>
          ) : (
            <div className="p-4 rounded-2xl bg-primary-500/10 text-primary-500 border border-primary-500/20 shadow-glow-primary">
              <UploadCloud className="w-10 h-10" />
            </div>
          )}

          <div>
            <h3 className="text-lg font-semibold text-white tracking-tight">
              {selectedFile ? selectedFile.name : 'Upload your legal contract'}
            </h3>
            <p className="text-sm text-gray-400 mt-1">
              {selectedFile
                ? `${(selectedFile.size / 1024).toFixed(1)} KB — Ready for analysis`
                : 'Drag & drop your PDF, DOCX, or TXT file here, or click to browse'}
            </p>
          </div>

          {!selectedFile && (
            <div className="flex items-center gap-2 pt-2">
              <span className="px-2.5 py-1 rounded-md bg-surface-subtle border border-surface-border text-xs text-gray-400 font-mono">
                PDF
              </span>
              <span className="px-2.5 py-1 rounded-md bg-surface-subtle border border-surface-border text-xs text-gray-400 font-mono">
                DOCX
              </span>
              <span className="px-2.5 py-1 rounded-md bg-surface-subtle border border-surface-border text-xs text-gray-400 font-mono">
                TXT
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Validation Error */}
      {errorMsg && (
        <div className="flex items-center gap-2 p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm animate-fade-in">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
        {/* Sample Contract Loader */}
        <button
          type="button"
          onClick={loadSampleContract}
          disabled={isLoading}
          className="text-xs font-medium text-gray-400 hover:text-primary-500 flex items-center gap-1.5 px-3 py-2 rounded-lg hover:bg-surface-hover transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Load Sample Contract</span>
        </button>

        {/* Start Analysis Button */}
        {selectedFile && (
          <button
            type="button"
            onClick={handleAnalyzeClick}
            disabled={isLoading}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-primary-600 via-indigo-600 to-secondary-600 hover:from-primary-500 hover:to-secondary-500 text-white font-semibold text-sm shadow-glow-primary flex items-center justify-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[44px]"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Run Risk Audit</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
