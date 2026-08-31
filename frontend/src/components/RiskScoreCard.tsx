import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle, Shield, Copy, Check, Sparkles } from 'lucide-react';
import { RiskLevel } from '../types';

interface RiskScoreCardProps {
  score: number;
  label: string;
  summary: string;
  totalClauses: number;
  fileName: string;
}

export const RiskScoreCard: React.FC<RiskScoreCardProps> = ({
  score,
  label,
  summary,
  totalClauses,
  fileName,
}) => {
  const [copied, setCopied] = useState(false);

  const getRiskDetails = (scoreVal: number): { level: RiskLevel; color: string; bg: string; icon: any } => {
    if (scoreVal >= 70) {
      return { level: 'high', color: 'text-risk-high', bg: 'bg-risk-high-bg border-risk-high-border', icon: ShieldAlert };
    } else if (scoreVal >= 40) {
      return { level: 'medium', color: 'text-risk-medium', bg: 'bg-risk-medium-bg border-risk-medium-border', icon: AlertTriangle };

    } else if (scoreVal >= 20) {
      return { level: 'low', color: 'text-risk-low', bg: 'bg-risk-low-bg border-risk-low-border', icon: Shield };
    } else {
      return { level: 'safe', color: 'text-risk-safe', bg: 'bg-risk-safe-bg border-risk-safe-border', icon: ShieldCheck };
    }
  };

  const riskDetails = getRiskDetails(score);
  const StatusIcon = riskDetails.icon;

  const handleCopySummary = () => {
    navigator.clipboard.writeText(`ClauseGuard Executive Summary for ${fileName}:\nRisk Score: ${score}/100 (${label})\n\n${summary}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // SVG Gauge params
  const strokeWidth = 10;
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-surface-border space-y-6 shadow-2xl">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        {/* Risk Score Circle Gauge */}
        <div className="flex flex-col items-center justify-center p-6 rounded-2xl bg-surface-subtle border border-surface-border">
          <div className="relative w-36 h-36 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="72"
                cy="72"
                r={radius}
                className="stroke-surface-border"
                strokeWidth={strokeWidth}
                fill="transparent"
              />
              <circle
                cx="72"
                cy="72"
                r={radius}
                className={`transition-all duration-1000 ease-out ${
                  score >= 70
                    ? 'stroke-red-500'
                    : score >= 40
                    ? 'stroke-amber-500'
                    : score >= 20
                    ? 'stroke-blue-500'
                    : 'stroke-emerald-500'
                }`}
                strokeWidth={strokeWidth}
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-4xl font-extrabold text-white tracking-tight">{score}</span>
              <span className="text-[10px] font-semibold uppercase text-gray-400">Risk Score</span>
            </div>
          </div>

          <div className={`mt-4 flex items-center gap-2 px-3.5 py-1.5 rounded-full border text-xs font-bold uppercase tracking-wider ${riskDetails.bg} ${riskDetails.color}`}>
            <StatusIcon className="w-4 h-4" />
            <span>{label}</span>
          </div>
        </div>

        {/* AI Executive Summary */}
        <div className="md:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary-500" />
              <h3 className="text-lg font-bold text-white tracking-tight">AI Executive Audit</h3>
            </div>
            <button
              onClick={handleCopySummary}
              className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white px-3 py-1.5 rounded-lg bg-surface-subtle hover:bg-surface-hover border border-surface-border transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[36px]"
              title="Copy Summary"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy Summary</span>
                </>
              )}
            </button>
          </div>

          <p className="text-sm text-gray-300 leading-relaxed bg-surface-subtle p-4 rounded-xl border border-surface-border/60">
            {summary}
          </p>

          <div className="flex items-center gap-4 text-xs text-gray-400 pt-1">
            <span className="px-2.5 py-1 rounded-md bg-surface-subtle border border-surface-border">
              File: <strong className="text-gray-200 font-mono">{fileName}</strong>
            </span>
            <span className="px-2.5 py-1 rounded-md bg-surface-subtle border border-surface-border">
              Clauses Audited: <strong className="text-gray-200">{totalClauses}</strong>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
