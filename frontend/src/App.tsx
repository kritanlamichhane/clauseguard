import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { FileUploader } from './components/FileUploader';
import { AnalysisProgress } from './components/AnalysisProgress';
import { RiskScoreCard } from './components/RiskScoreCard';
import { RiskBreakdownBar } from './components/RiskBreakdownBar';
import { EntityPills } from './components/EntityPills';
import { ClauseFilter } from './components/ClauseFilter';
import { ClauseCard } from './components/ClauseCard';
import { ClauseDetailDrawer } from './components/ClauseDetailDrawer';
import { AuthModal } from './components/AuthModal';
import { HistoryView } from './components/HistoryView';
import { AnalysisResponse, ClauseResult, User } from './types';
import { AlertTriangle, RefreshCw, FileText, Printer, Sparkles, Clock } from 'lucide-react';
import { API_BASE_URL } from './config';
import { wakeBackend } from './keepAlive';

const STORAGE_TOKEN_KEY = 'clauseguard_auth_token';
const STORAGE_USER_KEY = 'clauseguard_auth_user';

export const App: React.FC = () => {
  // Authentication State
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(STORAGE_TOKEN_KEY));
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem(STORAGE_USER_KEY);
    try {
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [isAuthModalOpen, setIsAuthModalOpen] = useState<boolean>(false);

  // View Mode: 'audit' (uploader), 'history' (past docs), 'report' (active analysis report)
  const [currentView, setCurrentView] = useState<'audit' | 'history' | 'report'>('audit');

  // Backend wake-up status for Render free-tier cold starts
  const [backendStatus, setBackendStatus] = useState<'unknown' | 'waking' | 'ready'>('unknown');

  // Audit State
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);

  // Filters & Drawer state
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedClause, setSelectedClause] = useState<ClauseResult | null>(null);

  // Wake the backend on page load (handles Render free-tier spin-down)
  useEffect(() => {
    const cancel = wakeBackend({
      onWaking: () => setBackendStatus('waking'),
      onReady:  () => setBackendStatus('ready'),
      onFailed: () => setBackendStatus('ready'), // stop showing banner on timeout
    });
    return cancel;
  }, []);

  // Verify auth token on initial load
  useEffect(() => {
    if (token) {
      fetch(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => {
          if (!res.ok) throw new Error('Session expired');
          return res.json();
        })
        .then((userData: User) => {
          setUser(userData);
          localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(userData));
        })
        .catch(() => {
          handleLogout();
        });
    }
  }, []);

  const handleAuthSuccess = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem(STORAGE_TOKEN_KEY, newToken);
    localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(newUser));
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(STORAGE_TOKEN_KEY);
    localStorage.removeItem(STORAGE_USER_KEY);
    if (currentView === 'history') {
      setCurrentView('audit');
    }
  };

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => null);
        throw new Error(errData?.detail || `Server error: ${response.statusText}`);
      }

      const data: AnalysisResponse = await response.json();
      setAnalysisData(data);
      setCurrentView('report');
    } catch (err: any) {
      console.error('[ClauseGuard Error]', err);
      setError(err.message || 'Failed to analyze contract. Please ensure the backend API is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setAnalysisData(null);
    setError(null);
    setActiveFilter('all');
    setSearchQuery('');
    setSelectedClause(null);
    setCurrentView('audit');
  };

  const handleSelectHistoryReport = (historyReport: AnalysisResponse) => {
    setAnalysisData(historyReport);
    setActiveFilter('all');
    setSearchQuery('');
    setSelectedClause(null);
    setCurrentView('report');
  };

  const handleNavigate = (view: 'audit' | 'history') => {
    if (view === 'history' && !user) {
      setIsAuthModalOpen(true);
      return;
    }
    setCurrentView(view);
  };

  const handlePrint = () => {
    window.print();
  };

  // Filter clauses based on active tab and search query
  const filteredClauses = (analysisData?.clauses || []).filter((c) => {
    const matchesFilter =
      activeFilter === 'all' || c.risk_level === activeFilter;
    const matchesSearch =
      !searchQuery ||
      c.clause_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.clause_type_predicted?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.risk_type?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const clauseCounts = {
    all: analysisData?.clauses.length || 0,
    high: analysisData?.risk_breakdown.high || 0,
    medium: analysisData?.risk_breakdown.medium || 0,
    low: analysisData?.risk_breakdown.low || 0,
    safe: analysisData?.risk_breakdown.safe || 0,
  };

  return (
    <div className="min-h-screen flex flex-col bg-background text-gray-100 font-sans selection:bg-primary-500 selection:text-white">
      {/* Header */}
      <Header
        user={user}
        currentView={currentView}
        onNavigate={handleNavigate}
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onLogout={handleLogout}
      />

      {/* Backend warm-up banner (Render free-tier cold-start notice) */}
      {backendStatus === 'waking' && (
        <div
          role="status"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '10px 16px',
            background: 'rgba(234, 179, 8, 0.12)',
            borderBottom: '1px solid rgba(234, 179, 8, 0.25)',
            color: '#fbbf24',
            fontSize: '13px',
            fontWeight: 500,
          }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ flexShrink: 0, animation: 'spin 1.2s linear infinite' }}
          >
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
          Backend is warming up — this takes ~30 seconds on the free tier. Please wait…
        </div>
      )}

      {/* Main Content Viewport */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
        {/* VIEW 1: Document History View */}
        {currentView === 'history' && (
          <HistoryView
            token={token}
            onSelectHistoryItem={handleSelectHistoryReport}
            onNewAudit={handleReset}
          />
        )}

        {/* VIEW 2: New Audit / Uploader View */}
        {currentView === 'audit' && !isLoading && (
          <section className="space-y-8 animate-fade-in">
            {/* Hero Banner */}
            <div className="text-center space-y-4 max-w-3xl mx-auto">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary-500/10 border border-primary-500/20 text-xs font-semibold text-primary-400">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Next-Gen Legal Risk Intelligence</span>
              </div>
              <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
                Instant AI Risk Audit for <br className="hidden sm:block" />
                <span className="bg-gradient-to-r from-primary-400 via-secondary-400 to-accent-400 bg-clip-text text-transparent">
                  Legal Contracts & Agreements
                </span>
              </h1>
              <p className="text-base text-gray-400 max-w-2xl mx-auto">
                Upload any PDF or DOCX contract. ClauseGuard segments clauses, runs ML classification, extracts entities, and delivers plain-English risk advice.
              </p>

              {!user && (
                <div className="pt-2">
                  <button
                    type="button"
                    onClick={() => setIsAuthModalOpen(true)}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-surface-subtle hover:bg-surface-hover border border-surface-border text-xs text-gray-300 font-medium transition-colors"
                  >
                    <Clock className="w-3.5 h-3.5 text-primary-400" />
                    <span>Sign in to save and review past document audits</span>
                  </button>
                </div>
              )}
            </div>

            {/* File Uploader */}
            <FileUploader onFileSelected={handleFileSelect} isLoading={isLoading} />
          </section>
        )}

        {/* Progress Tracker during API upload */}
        {isLoading && file && (
          <section className="py-12">
            <AnalysisProgress fileName={file.name} />
          </section>
        )}

        {/* Error Card */}
        {error && (
          <section className="max-w-2xl mx-auto p-6 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-300 space-y-4">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0" />
              <h3 className="text-lg font-bold text-white">Analysis Failed</h3>
            </div>
            <p className="text-sm text-red-200">{error}</p>
            <button
              onClick={handleReset}
              className="px-4 py-2 rounded-xl bg-red-500/20 hover:bg-red-500/30 text-red-200 text-xs font-semibold border border-red-500/40 transition-colors"
            >
              Try Again
            </button>
          </section>
        )}

        {/* VIEW 3: Analysis Results Dashboard */}
        {currentView === 'report' && analysisData && !isLoading && (
          <section className="space-y-8 animate-fade-in">
            {/* Top Dashboard Actions */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 border-b border-surface-border pb-6">
              <div>
                <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                  <FileText className="w-6 h-6 text-primary-500" />
                  Contract Audit Report
                </h2>
                <p className="text-xs text-gray-400 font-mono mt-1">
                  File: {analysisData.file_name} • {analysisData.total_clauses} Clauses Analyzed
                  {analysisData.history_id && (
                    <span className="ml-2 inline-flex items-center gap-1 text-emerald-400">
                      • Saved to History (# {analysisData.history_id})
                    </span>
                  )}
                </p>
              </div>

              <div className="flex items-center gap-3">
                {user && (
                  <button
                    onClick={() => setCurrentView('history')}
                    className="px-4 py-2.5 rounded-xl bg-surface-subtle hover:bg-surface-hover border border-surface-border text-xs font-semibold text-gray-300 flex items-center gap-2 transition-colors min-h-[44px]"
                  >
                    <Clock className="w-4 h-4" />
                    <span>View History</span>
                  </button>
                )}
                <button
                  onClick={handlePrint}
                  className="px-4 py-2.5 rounded-xl bg-surface-subtle hover:bg-surface-hover border border-surface-border text-xs font-semibold text-gray-300 flex items-center gap-2 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[44px]"
                >
                  <Printer className="w-4 h-4" />
                  <span>Print Report</span>
                </button>
                <button
                  onClick={handleReset}
                  className="px-4 py-2.5 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold shadow-glow-primary flex items-center gap-2 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[44px]"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Audit Another File</span>
                </button>
              </div>
            </div>

            {/* Risk Score & AI Executive Summary */}
            <RiskScoreCard
              score={analysisData.risk_score}
              label={analysisData.risk_label}
              summary={analysisData.summary}
              totalClauses={analysisData.total_clauses}
              fileName={analysisData.file_name}
            />

            {/* Risk Breakdown Bar & Category Selector */}
            <RiskBreakdownBar
              breakdown={analysisData.risk_breakdown}
              activeFilter={activeFilter}
              onSelectFilter={setActiveFilter}
            />

            {/* Metadata Entity Pills */}
            <EntityPills entities={analysisData.entities} />

            {/* Clause Filter Bar */}
            <ClauseFilter
              activeTab={activeFilter}
              onTabChange={setActiveFilter}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              clauseCounts={clauseCounts}
            />

            {/* Clause Cards List */}
            <div className="space-y-4">
              {filteredClauses.length > 0 ? (
                filteredClauses.map((clause, idx) => (
                  <ClauseCard
                    key={idx}
                    clause={clause}
                    index={idx}
                    onSelect={setSelectedClause}
                  />
                ))
              ) : (
                <div className="text-center py-12 glass-panel rounded-2xl border border-surface-border space-y-2">
                  <p className="text-sm font-semibold text-gray-400">No clauses match your search or filter.</p>
                  <button
                    onClick={() => {
                      setActiveFilter('all');
                      setSearchQuery('');
                    }}
                    className="text-xs text-primary-400 hover:underline"
                  >
                    Reset Filters
                  </button>
                </div>
              )}
            </div>

            {/* Slide-over Detail Inspector Drawer */}
            <ClauseDetailDrawer
              clause={selectedClause}
              onClose={() => setSelectedClause(null)}
            />
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-border py-6 glass-panel text-center text-xs text-gray-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© ClauseGuard AI • Modern Contract Intelligence System</p>
          <p className="font-mono text-[11px]">Powered by PyTorch, ONNX Runtime & Google Gemini</p>
        </div>
      </footer>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />
    </div>
  );
};
