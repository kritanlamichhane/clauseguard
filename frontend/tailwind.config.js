/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0B0F19",
        surface: {
          DEFAULT: "#111827",
          hover: "#1F2937",
          border: "rgba(255, 255, 255, 0.08)",
          subtle: "rgba(255, 255, 255, 0.03)",
        },
        primary: {
          50: '#EEF2FF',
          100: '#E0E7FF',
          500: '#6366F1',
          600: '#4F46E5',
          700: '#4338CA',
          glow: 'rgba(99, 102, 241, 0.15)',
        },
        secondary: {
          500: '#06B6D4',
          600: '#0891B2',
          glow: 'rgba(6, 182, 212, 0.15)',
        },
        accent: {
          500: '#8B5CF6',
          600: '#7C3AED',
        },
        risk: {
          high: '#EF4444',
          'high-bg': 'rgba(239, 68, 68, 0.12)',
          'high-border': 'rgba(239, 68, 68, 0.3)',
          medium: '#F59E0B',
          'medium-bg': 'rgba(245, 158, 11, 0.12)',
          'medium-border': 'rgba(245, 158, 11, 0.3)',
          low: '#3B82F6',
          'low-bg': 'rgba(59, 130, 246, 0.12)',
          'low-border': 'rgba(59, 130, 246, 0.3)',
          safe: '#10B981',
          'safe-bg': 'rgba(16, 185, 129, 0.12)',
          'safe-border': 'rgba(16, 185, 129, 0.3)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'glow-primary': '0 0 25px -5px rgba(99, 102, 241, 0.25)',
        'glow-high': '0 0 25px -5px rgba(239, 68, 68, 0.25)',
        'glow-safe': '0 0 25px -5px rgba(16, 185, 129, 0.25)',
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 8s linear infinite',
      }
    },
  },
  plugins: [],
}
