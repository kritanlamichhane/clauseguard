import React from 'react';
import { ClauseResult, RiskLevel } from '../types';
import { AlertOctagon, AlertTriangle, Info, CheckCircle2, ChevronRight, Lightbulb, ShieldAlert } from 'lucide-react';

interface ClauseCardProps {
  clause: ClauseResult;
  index: number;
  onSelect: (clause: ClauseResult) => void;
}

export const ClauseCard: React.FC<ClauseCardProps> = ({ clause, index, onSelect }) => {
  const getBadgeStyle = (level: RiskLevel) => {
    switch (level) {
      case 'high':
        return {
          bg: 'bg-red-500/10 border-red-500/30 text-red-400',
          icon: AlertOctagon,
          label: 'High Risk',
        };
      case 'medium':
        return {
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
          icon: AlertTriangle,
          label: 'Medium Risk',
        };
      case 'low':
        return {
          bg: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
          icon: Info,
          label: 'Low Risk',
        };
      default:
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
          icon: CheckCircle2,
          label: 'Safe',
        };
    }
  };

  const badge = getBadgeStyle(clause.risk_level);
  const BadgeIcon = badge.icon;

  return (
    <div
      onClick={() => onSelect(clause)}
      className="glass-panel-interactive p-5 sm:p-6 rounded-2xl border border-surface-border space-y-4 cursor-pointer group"
      role="button"
      tabIndex={0}
      aria-label={`Inspect clause ${index + 1}`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          onSelect(clause);
        }
      }}
    >
      {/* Clause Card Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-surface-border/50 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold text-gray-400 px-2 py-0.5 rounded-md bg-surface-subtle border border-surface-border">
            #{index + 1}
          </span>
          <span className="text-xs font-semibold text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 rounded-md">
            {clause.clause_type_predicted || 'General Clause'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className={`flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full border ${badge.bg}`}>
            <BadgeIcon className="w-3.5 h-3.5" />
            <span>{clause.risk_type || badge.label}</span>
          </span>
          <ChevronRight className="w-4 h-4 text-gray-500 group-hover:text-primary-400 group-hover:translate-x-0.5 transition-all" />
        </div>
      </div>

      {/* Clause Text Snippet */}
      <div className="bg-surface-subtle p-3.5 rounded-xl border border-surface-border/60">
        <p className="text-xs sm:text-sm font-mono text-gray-300 leading-relaxed whitespace-pre-wrap">
          "{clause.clause_text}"
        </p>
      </div>

      {/* AI Explanation & Recommendation */}
      {clause.risk_level !== 'safe' && (clause.explanation || clause.recommendation) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          {/* Risk Explanation */}
          {clause.explanation && (
            <div className="p-3 rounded-xl bg-surface-subtle/50 border border-surface-border text-xs space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-amber-400">
                <ShieldAlert className="w-3.5 h-3.5 flex-shrink-0" />
                <span>Risk Explanation</span>
              </div>
              <p className="text-gray-300 leading-normal">{clause.explanation}</p>
            </div>
          )}

          {/* Action Recommendation */}
          {clause.recommendation && (
            <div className="p-3 rounded-xl bg-primary-500/5 border border-primary-500/20 text-xs space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-primary-400">
                <Lightbulb className="w-3.5 h-3.5 flex-shrink-0" />
                <span>Recommended Action</span>
              </div>
              <p className="text-gray-300 leading-normal">{clause.recommendation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
