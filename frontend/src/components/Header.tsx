import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  Sparkles,
  Activity,
  Github,
  CheckCircle2,
  AlertCircle,
  LogIn,
  LogOut,
  Clock,
  FileText
} from 'lucide-react';
import { User } from '../types';
import { API_BASE_URL } from '../config';

interface HeaderProps {
  user: User | null;
  currentView: 'audit' | 'history' | 'report';
  onNavigate: (view: 'audit' | 'history') => void;
  onOpenAuth: () => void;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  user,
  currentView,
  onNavigate,
  onOpenAuth,
  onLogout,
}) => {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/health`);
        if (res.ok) {
          setApiOnline(true);
        } else {
          setApiOnline(false);
        }
      } catch (err) {
        setApiOnline(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-surface-border backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand */}
        <div
          onClick={() => onNavigate('audit')}
          className="flex items-center gap-3 cursor-pointer select-none"
        >
          <div className="relative p-2.5 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl shadow-glow-primary flex items-center justify-center">
            <ShieldAlert className="w-5 h-5 text-white" />
            <Sparkles className="w-3 h-3 text-cyan-300 absolute -top-1 -right-1 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-gray-100 to-gray-400 bg-clip-text text-transparent">
                ClauseGuard
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-500 border border-primary-500/20">
                AI Engine
              </span>
            </div>
            <p className="text-xs text-gray-400 font-normal hidden sm:block">
              Legal Contract Audit & Risk Intelligence
            </p>
          </div>
        </div>

        {/* Center Navigation Links */}
        <nav className="hidden md:flex items-center gap-1.5 bg-surface-subtle/80 p-1 rounded-xl border border-surface-border">
          <button
            type="button"
            onClick={() => onNavigate('audit')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
              currentView === 'audit' || currentView === 'report'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-gray-400 hover:text-gray-200 hover:bg-surface-hover'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Audit Contract</span>
          </button>

          <button
            type="button"
            onClick={() => onNavigate('history')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
              currentView === 'history'
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-gray-400 hover:text-gray-200 hover:bg-surface-hover'
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>Document History</span>
            {user && (
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            )}
          </button>
        </nav>

        {/* Status & Auth Actions */}
        <div className="flex items-center gap-3">
          {/* Mobile Navigation Dropdown/Buttons */}
          <div className="flex md:hidden items-center gap-1">
            <button
              onClick={() => onNavigate('audit')}
              className={`p-2 rounded-lg text-xs font-semibold ${
                currentView === 'audit' || currentView === 'report' ? 'text-primary-400' : 'text-gray-400'
              }`}
              title="Audit"
            >
              <FileText className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigate('history')}
              className={`p-2 rounded-lg text-xs font-semibold ${
                currentView === 'history' ? 'text-primary-400' : 'text-gray-400'
              }`}
              title="History"
            >
              <Clock className="w-4 h-4" />
            </button>
          </div>

          {/* API Health Pill */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-subtle border border-surface-border text-xs">
            <Activity className="w-3.5 h-3.5 text-gray-400" />
            <span className="text-gray-400 font-medium">API:</span>
            {apiOnline === null ? (
              <span className="inline-flex items-center gap-1 text-gray-400 animate-pulse">
                <span className="w-2 h-2 rounded-full bg-gray-500"></span> Checking...
              </span>
            ) : apiOnline ? (
              <span className="inline-flex items-center gap-1.5 text-emerald-400 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> Ready
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 text-amber-400 font-medium">
                <AlertCircle className="w-3.5 h-3.5" /> Offline
              </span>
            )}
          </div>

          {/* Auth Controls */}
          {user ? (
            <div className="flex items-center gap-2 pl-2 border-l border-surface-border">
              {/* User Profile Pill */}
              <div
                onClick={() => onNavigate('history')}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-surface-subtle hover:bg-surface-hover border border-surface-border cursor-pointer transition-colors"
                title={`Logged in as ${user.email}`}
              >
                <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-xs font-bold">
                  {user.username ? user.username.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-xs font-bold text-white leading-tight truncate max-w-[120px]">
                    {user.username}
                  </p>
                  <p className="text-[10px] text-gray-400 truncate max-w-[120px]">
                    {user.email}
                  </p>
                </div>
              </div>

              {/* Logout Button */}
              <button
                type="button"
                onClick={onLogout}
                className="p-2 text-gray-400 hover:text-red-400 rounded-xl hover:bg-red-500/10 border border-transparent hover:border-red-500/20 transition-colors"
                title="Sign Out"
                aria-label="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={onOpenAuth}
              className="px-4 py-2 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold shadow-glow-primary flex items-center gap-2 transition-all min-h-[38px]"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign In</span>
            </button>
          )}

          {/* GitHub Repo Link */}
          <a
            href="https://github.com/kritanlamichhane/clauseguard"
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-surface-hover transition-colors hidden sm:flex items-center justify-center"
            aria-label="GitHub Repository"
          >
            <Github className="w-4 h-4" />
          </a>
        </div>
      </div>
    </header>
  );
};
