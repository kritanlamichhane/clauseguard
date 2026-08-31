import React from 'react';
import { Search, X } from 'lucide-react';


interface ClauseFilterProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  clauseCounts: {
    all: number;
    high: number;
    medium: number;
    low: number;
    safe: number;
  };
}

export const ClauseFilter: React.FC<ClauseFilterProps> = ({
  activeTab,
  onTabChange,
  searchQuery,
  onSearchChange,
  clauseCounts,
}) => {
  const tabs = [
    { id: 'all', label: 'All Clauses', count: clauseCounts.all },
    { id: 'high', label: 'High Risk', count: clauseCounts.high, badge: 'bg-red-500/20 text-red-400' },
    { id: 'medium', label: 'Medium Risk', count: clauseCounts.medium, badge: 'bg-amber-500/20 text-amber-400' },
    { id: 'low', label: 'Low Risk', count: clauseCounts.low, badge: 'bg-blue-500/20 text-blue-400' },
    { id: 'safe', label: 'Safe', count: clauseCounts.safe, badge: 'bg-emerald-500/20 text-emerald-400' },
  ];

  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 glass-panel p-4 rounded-2xl border border-surface-border">
      {/* Category Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[44px] ${
                isActive
                  ? 'bg-primary-500 text-white shadow-glow-primary'
                  : 'bg-surface-subtle text-gray-400 hover:text-white hover:bg-surface-hover border border-surface-border'
              }`}
            >
              <span>{tab.label}</span>
              <span
                className={`px-2 py-0.5 rounded-full text-[10px] font-mono ${
                  isActive ? 'bg-white/20 text-white' : tab.badge || 'bg-surface-border text-gray-300'
                }`}
              >
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Search Input */}
      <div className="relative min-w-[240px]">
        <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Filter clauses by text..."
          className="w-full bg-surface-subtle border border-surface-border rounded-xl pl-9 pr-9 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-colors min-h-[44px]"
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
            title="Clear search"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
};
