import React, { useEffect, useState } from 'react';
import {
  Clock,
  Search,
  Trash2,
  FileText,
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
  Sparkles,
  ArrowRight,
  Loader2,
  RefreshCw,
  FolderOpen
} from 'lucide-react';
import { HistoryItem, AnalysisResponse } from '../types';

interface HistoryViewProps {
  token: string | null;
  onSelectHistoryItem: (analysis: AnalysisResponse) => void;
  onNewAudit: () => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({
  token,
  onSelectHistoryItem,
  onNewAudit,
}) => {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedRisk, setSelectedRisk] = useState<string>('all');
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [viewingId, setViewingId] = useState<number | null>(null);

  const fetchHistory = async () => {
    if (!token) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch('/history', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        throw new Error('Failed to load history records.');
      }
      const data: HistoryItem[] = await res.json();
      setItems(data);
    } catch (err: any) {
      setError(err.message || 'Error connecting to history server.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [token]);

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!token) return;
    if (!window.confirm('Are you sure you want to delete this contract audit from your history?')) {
      return;
    }

    setDeletingId(id);
    try {
      const res = await fetch(`/history/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        throw new Error('Failed to delete history record.');
      }
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err: any) {
      alert(err.message || 'Could not delete item.');
    } finally {
      setDeletingId(null);
    }
  };

  const handleOpenReport = async (id: number) => {
    if (!token) return;
    setViewingId(id);
    try {
      const res = await fetch(`/history/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        throw new Error('Failed to fetch full report details.');
      }
      const detail = await res.json();
      onSelectHistoryItem(detail);
    } catch (err: any) {
      alert(err.message || 'Could not load the full audit report.');
    } finally {
      setViewingId(null);
    }
  };

  // Filter & Search logic
  const filteredItems = items.filter((item) => {
    const matchesSearch =
      !searchQuery ||
      item.file_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.summary.toLowerCase().includes(searchQuery.toLowerCase());

    const riskNormalized = item.risk_label.toLowerCase();
    const matchesRisk =
      selectedRisk === 'all' ||
      (selectedRisk === 'high' && riskNormalized.includes('high')) ||
      (selectedRisk === 'medium' && riskNormalized.includes('medium')) ||
      (selectedRisk === 'low' && (riskNormalized.includes('low') || riskNormalized.includes('safe')));

    return matchesSearch && matchesRisk;
  });

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  const getRiskBadge = (score: number, label: string) => {
    if (score >= 70 || label.toLowerCase().includes('high')) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 text-xs font-semibold">
          <AlertTriangle className="w-3 h-3" />
          <span>{label || 'High Risk'} ({score}/100)</span>
        </span>
      );
    }
    if (score >= 40 || label.toLowerCase().includes('medium')) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-semibold">
          <ShieldAlert className="w-3 h-3" />
          <span>{label || 'Medium Risk'} ({score}/100)</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
        <CheckCircle2 className="w-3 h-3" />
        <span>{label || 'Low Risk'} ({score}/100)</span>
      </span>
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-border pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-primary-500/10 border border-primary-500/20 text-xs font-semibold text-primary-400 mb-2">
            <Clock className="w-3.5 h-3.5" />
            <span>Persistent Document Vault</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <FolderOpen className="w-6 h-6 text-primary-500" />
            Contract Audit History
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            All your past analyzed documents, risk summaries, and clause diagnostics are stored permanently.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchHistory}
            disabled={isLoading}
            className="p-2.5 rounded-xl bg-surface-subtle hover:bg-surface-hover border border-surface-border text-gray-300 text-xs font-semibold transition-colors flex items-center gap-2 min-h-[44px]"
            title="Refresh history"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>

          <button
            onClick={onNewAudit}
            className="px-4 py-2.5 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold shadow-glow-primary flex items-center gap-2 transition-colors min-h-[44px]"
          >
            <FileText className="w-4 h-4" />
            <span>Audit New File</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 glass-panel p-3 rounded-2xl border border-surface-border">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search past contracts by filename or keywords..."
            className="w-full bg-surface-subtle border border-surface-border/60 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-colors"
          />
        </div>

        {/* Risk Filter Buttons */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {[
            { id: 'all', label: 'All Risks' },
            { id: 'high', label: 'High Risk' },
            { id: 'medium', label: 'Medium' },
            { id: 'low', label: 'Low Risk' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedRisk(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${
                selectedRisk === tab.id
                  ? 'bg-primary-600 text-white shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-surface-subtle'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="py-20 text-center glass-panel rounded-2xl border border-surface-border space-y-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500 mx-auto" />
          <p className="text-sm text-gray-300 font-medium">Loading your document history...</p>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-300 space-y-2">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <h3 className="text-sm font-bold text-white">Failed to Load History</h3>
          </div>
          <p className="text-xs text-red-200">{error}</p>
          <button
            onClick={fetchHistory}
            className="px-3 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-xs font-semibold text-red-200 border border-red-500/40"
          >
            Retry
          </button>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && filteredItems.length === 0 && (
        <div className="py-20 text-center glass-panel rounded-2xl border border-surface-border space-y-4 max-w-lg mx-auto p-8">
          <div className="w-14 h-14 rounded-2xl bg-primary-500/10 border border-primary-500/20 text-primary-400 flex items-center justify-center mx-auto">
            <FolderOpen className="w-7 h-7" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-bold text-white">
              {searchQuery || selectedRisk !== 'all' ? 'No Matching Contracts Found' : 'No Documents Analyzed Yet'}
            </h3>
            <p className="text-xs text-gray-400 max-w-sm mx-auto">
              {searchQuery || selectedRisk !== 'all'
                ? 'Try adjusting your search terms or risk filters.'
                : 'Upload your first contract file to generate AI risk diagnostics and save it to your history.'}
            </p>
          </div>
          <button
            onClick={onNewAudit}
            className="px-4 py-2 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold shadow-glow-primary inline-flex items-center gap-2"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Audit a Contract Now</span>
          </button>
        </div>
      )}

      {/* History Items Grid / List */}
      {!isLoading && !error && filteredItems.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              onClick={() => handleOpenReport(item.id)}
              className="group glass-panel rounded-2xl p-5 border border-surface-border hover:border-primary-500/50 hover:shadow-glow-primary transition-all duration-200 cursor-pointer flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                {/* Header Row: Filename & Badge */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="p-2 rounded-xl bg-surface-subtle text-primary-400 group-hover:bg-primary-500/20 transition-colors flex-shrink-0">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-sm font-bold text-white truncate group-hover:text-primary-400 transition-colors">
                        {item.file_name}
                      </h4>
                      <p className="text-[11px] text-gray-400 font-mono">
                        {formatDate(item.created_at)} • {item.total_clauses} clauses
                      </p>
                    </div>
                  </div>

                  <div className="flex-shrink-0">
                    {getRiskBadge(item.risk_score, item.risk_label)}
                  </div>
                </div>

                {/* Summary Snippet */}
                <p className="text-xs text-gray-300 line-clamp-3 leading-relaxed bg-surface-subtle/50 p-3 rounded-xl border border-surface-border/30">
                  {item.summary || 'No AI summary available for this contract.'}
                </p>
              </div>

              {/* Action Buttons Footer */}
              <div className="flex items-center justify-between pt-2 border-t border-surface-border/50 text-xs">
                <button
                  type="button"
                  onClick={(e) => handleDelete(item.id, e)}
                  disabled={deletingId === item.id}
                  className="p-1.5 text-gray-400 hover:text-red-400 rounded-lg hover:bg-red-500/10 transition-colors flex items-center gap-1.5"
                  title="Delete from history"
                >
                  {deletingId === item.id ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-red-400" />
                  ) : (
                    <Trash2 className="w-3.5 h-3.5" />
                  )}
                  <span className="text-[11px]">Delete</span>
                </button>

                <div className="inline-flex items-center gap-1.5 text-primary-400 group-hover:text-primary-300 font-semibold text-xs">
                  {viewingId === item.id ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Loading Report...</span>
                    </>
                  ) : (
                    <>
                      <span>Open Full Report</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
