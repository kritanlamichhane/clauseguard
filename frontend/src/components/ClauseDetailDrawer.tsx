import React, { useEffect } from 'react';
import { ClauseResult } from '../types';
import { X, ShieldAlert, Lightbulb, Cpu, FileText, CheckCircle2, Copy, Check } from 'lucide-react';

interface ClauseDetailDrawerProps {
  clause: ClauseResult | null;
  onClose: () => void;
}

export const ClauseDetailDrawer: React.FC<ClauseDetailDrawerProps> = ({ clause, onClose }) => {
  const [copied, setCopied] = React.useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!clause) return null;

  const handleCopyClause = () => {
    navigator.clipboard.writeText(clause.clause_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex justify-end">
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity animate-fade-in"
      />

      {/* Drawer Panel */}
      <div className="relative w-full max-w-xl glass-panel h-full border-l border-surface-border p-6 sm:p-8 overflow-y-auto z-10 shadow-2xl flex flex-col justify-between animate-slide-left">
        <div className="space-y-6">
          {/* Drawer Header */}
          <div className="flex items-center justify-between border-b border-surface-border pb-4">
            <div>
              <span className="text-xs font-mono text-primary-400 uppercase tracking-wider font-bold">
                {clause.clause_type_predicted || 'Clause Inspector'}
              </span>
              <h3 className="text-xl font-bold text-white tracking-tight mt-0.5">
                {clause.risk_type || 'Clause Audit Details'}
              </h3>
            </div>

            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-surface-hover transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[44px] min-w-[44px] flex items-center justify-center"
              aria-label="Close clause details drawer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Full Clause Text */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-primary-500" />
                <span>Full Clause Text</span>
              </label>
              <button
                onClick={handleCopyClause}
                className="text-xs text-gray-400 hover:text-white flex items-center gap-1 px-2.5 py-1 rounded bg-surface-subtle border border-surface-border"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
            <div className="p-4 rounded-xl bg-surface-subtle border border-surface-border font-mono text-sm text-gray-200 leading-relaxed">
              "{clause.clause_text}"
            </div>
          </div>

          {/* AI Explanation & Recommendation */}
          <div className="space-y-4">
            {clause.explanation && (
              <div className="p-4 rounded-xl bg-surface-subtle border border-amber-500/30 space-y-2">
                <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider">
                  <ShieldAlert className="w-4 h-4" />
                  <span>AI Risk Audit</span>
                </div>
                <p className="text-sm text-gray-300 leading-relaxed">{clause.explanation}</p>
              </div>
            )}

            {clause.recommendation && (
              <div className="p-4 rounded-xl bg-primary-500/10 border border-primary-500/30 space-y-2">
                <div className="flex items-center gap-2 text-primary-400 text-xs font-bold uppercase tracking-wider">
                  <Lightbulb className="w-4 h-4" />
                  <span>Actionable Recommendation</span>
                </div>
                <p className="text-sm text-gray-200 leading-relaxed">{clause.recommendation}</p>
              </div>
            )}
          </div>

          {/* ML & ONNX Signals */}
          <div className="space-y-3 pt-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-secondary-500" />
              <span>Pipeline Intelligence Signals</span>
            </h4>

            {clause.similarity_match ? (
              <div className="p-3.5 rounded-xl bg-surface-subtle border border-surface-border text-xs space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-cyan-400">Semantic Similarity Model (ONNX)</span>
                  <span className="font-mono text-cyan-300 font-bold">
                    {(clause.similarity_match.similarity_score * 100).toFixed(0)}% Match
                  </span>
                </div>
                <p className="text-gray-400 font-mono text-[11px]">
                  Matched reference: "{clause.similarity_match.matched_reference}"
                </p>
              </div>
            ) : (
              <div className="p-3 rounded-xl bg-surface-subtle border border-surface-border text-xs text-gray-400 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>No high-risk semantic reference matches detected.</span>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="pt-6 border-t border-surface-border mt-8 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 rounded-xl bg-surface-subtle hover:bg-surface-hover text-white text-xs font-semibold border border-surface-border transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[44px]"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
