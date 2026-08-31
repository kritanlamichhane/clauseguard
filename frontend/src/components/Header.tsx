import React, { useEffect, useState } from 'react';
import { ShieldAlert, Sparkles, Activity, Github, CheckCircle2, AlertCircle } from 'lucide-react';

export const Header: React.FC = () => {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/health');
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
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

        {/* Status & Links */}
        <div className="flex items-center gap-4">
          {/* API Health Pill */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-subtle border border-surface-border text-xs">
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
                <AlertCircle className="w-3.5 h-3.5" /> Offline / Standby
              </span>
            )}
          </div>

          {/* GitHub Repo */}
          <a
            href="https://github.com/kritanlamichhane/clauseguard"
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-surface-hover transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label="GitHub Repository"
          >
            <Github className="w-5 h-5" />
          </a>
        </div>
      </div>
    </header>
  );
};
