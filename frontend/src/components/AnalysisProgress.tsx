import React, { useEffect, useState } from 'react';
import { Loader2, FileText, Scissors, UserCheck, Cpu, Sparkles, CheckCircle2 } from 'lucide-react';

interface AnalysisProgressProps {
  fileName: string;
}

const STEPS = [
  { id: 1, label: 'Extracting Text & Cleaning Document', icon: FileText },
  { id: 2, label: 'Segmenting Contract into Clauses', icon: Scissors },
  { id: 3, label: 'Extracting Entities (Parties, Dates, Amounts)', icon: UserCheck },
  { id: 4, label: 'Running ML Classifier & ONNX Similarity Models', icon: Cpu },
  { id: 5, label: 'Generating AI Audit & Gemini Executive Summary', icon: Sparkles },
];

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ fileName }) => {
  const [currentStep, setCurrentStep] = useState(1);

  useEffect(() => {
    const timer1 = setTimeout(() => setCurrentStep(2), 800);
    const timer2 = setTimeout(() => setCurrentStep(3), 1800);
    const timer3 = setTimeout(() => setCurrentStep(4), 2800);
    const timer4 = setTimeout(() => setCurrentStep(5), 4000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
    };
  }, []);

  const progressPercent = Math.min((currentStep / STEPS.length) * 100, 95);

  return (
    <div className="w-full max-w-2xl mx-auto glass-panel p-6 sm:p-8 rounded-2xl border border-surface-border space-y-6 shadow-2xl animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-surface-border pb-4">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Loader2 className="w-5 h-5 text-primary-500 animate-spin" />
            Analyzing Contract...
          </h3>
          <p className="text-xs text-gray-400 mt-0.5 truncate max-w-md font-mono">
            {fileName}
          </p>
        </div>
        <span className="text-xs font-bold text-primary-400 bg-primary-500/10 px-3 py-1 rounded-full border border-primary-500/20">
          {Math.round(progressPercent)}% Complete
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-surface-subtle h-2 rounded-full overflow-hidden border border-surface-border">
        <div
          className="bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Steps List */}
      <div className="space-y-3 pt-2">
        {STEPS.map((step) => {
          const Icon = step.icon;
          const isDone = currentStep > step.id;
          const isCurrent = currentStep === step.id;

          return (
            <div
              key={step.id}
              className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-300 ${
                isCurrent
                  ? 'bg-primary-500/10 border border-primary-500/30 text-white shadow-glow-primary'
                  : isDone
                  ? 'bg-surface-subtle border border-emerald-500/20 text-emerald-400'
                  : 'text-gray-500 opacity-60 border border-transparent'
              }`}
            >
              <div
                className={`p-2 rounded-lg ${
                  isCurrent
                    ? 'bg-primary-500 text-white'
                    : isDone
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-surface-subtle text-gray-500'
                }`}
              >
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Icon className="w-4 h-4" />
                )}
              </div>
              <span className="text-sm font-medium">{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
