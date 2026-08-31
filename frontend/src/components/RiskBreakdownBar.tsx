import React from 'react';
import { RiskBreakdown, RiskLevel } from '../types';
import { AlertOctagon, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

interface RiskBreakdownBarProps {
  breakdown: RiskBreakdown;
  activeFilter: string;
  onSelectFilter: (filter: string) => void;
}

export const RiskBreakdownBar: React.FC<RiskBreakdownBarProps> = ({
  breakdown,
  activeFilter,
  onSelectFilter,
}) => {
  const total = (breakdown.high || 0) + (breakdown.medium || 0) + (breakdown.low || 0) + (breakdown.safe || 0);

  const getPercent = (count: number) => {
    if (!total) return 0;
    return Math.round((count / total) * 100);
  };

  const categories: Array<{
    key: RiskLevel;
    label: string;
    count: number;
    color: string;
    bg: string;
    border: string;
    icon: any;
  }> = [
    {
      key: 'high',
      label: 'High Risk',
      count: breakdown.high || 0,
      color: 'text-risk-high',
      bg: 'bg-risk-high-bg',
      border: 'border-risk-high-border',
      icon: AlertOctagon,
    },
    {
      key: 'medium',
      label: 'Medium Risk',
      count: breakdown.medium || 0,
      color: 'text-risk-medium',
      bg: 'bg-risk-medium-bg',
      border: 'border-risk-medium-border',
      icon: AlertTriangle,
    },
    {
      key: 'low',
      label: 'Low Risk',
      count: breakdown.low || 0,
      color: 'text-risk-low',
      bg: 'bg-risk-low-bg',
      border: 'border-risk-low-border',
      icon: Info,
    },
    {
      key: 'safe',
      label: 'Safe',
      count: breakdown.safe || 0,
      color: 'text-risk-safe',
      bg: 'bg-risk-safe-bg',
      border: 'border-risk-safe-border',
      icon: CheckCircle2,
    },
  ];

  return (
    <div className="glass-panel p-6 rounded-2xl border border-surface-border space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-bold text-white uppercase tracking-wider">Risk Level Breakdown</h4>
        <span className="text-xs text-gray-400 font-mono">{total} Total Clauses</span>
      </div>

      {/* Stacked Percentage Bar */}
      <div className="w-full h-3 bg-surface-subtle rounded-full overflow-hidden flex border border-surface-border">
        {categories.map((cat) => {
          const pct = getPercent(cat.count);
          if (pct === 0) return null;
          return (
            <div
              key={cat.key}
              style={{ width: `${pct}%` }}
              className={`h-full transition-all duration-500 ${
                cat.key === 'high'
                  ? 'bg-red-500'
                  : cat.key === 'medium'
                  ? 'bg-amber-500'
                  : cat.key === 'low'
                  ? 'bg-blue-500'
                  : 'bg-emerald-500'
              }`}
              title={`${cat.label}: ${cat.count} (${pct}%)`}
            />
          );
        })}
      </div>

      {/* Interactive Category Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
        {categories.map((cat) => {
          const Icon = cat.icon;
          const isSelected = activeFilter === cat.key;

          return (
            <button
              key={cat.key}
              onClick={() => onSelectFilter(cat.key)}
              className={`p-3.5 rounded-xl border text-left transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[44px] ${
                isSelected
                  ? `${cat.bg} ${cat.border} ring-1 ring-white/20 scale-[1.02]`
                  : 'bg-surface-subtle border-surface-border hover:border-gray-700 hover:bg-surface-hover'
              }`}
            >
              <div className="flex items-center justify-between">
                <Icon className={`w-4 h-4 ${cat.color}`} />
                <span className={`text-lg font-bold ${cat.color}`}>{cat.count}</span>
              </div>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-xs font-semibold text-gray-300">{cat.label}</span>
                <span className="text-[10px] text-gray-400 font-mono">{getPercent(cat.count)}%</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
