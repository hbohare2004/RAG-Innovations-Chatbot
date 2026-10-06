import React from 'react';
import { Sparkles, Trash2, ExternalLink } from 'lucide-react';

export default function Header({ healthStatus, onClearChat, messageCount }) {
  const isHealthy = healthStatus?.status === 'healthy';
  const isDegraded = healthStatus?.status === 'degraded';

  return (
    <header className="sticky top-0 z-40 w-full glass-nav px-4 lg:px-8 py-2.5 transition-all">
      <div className="max-w-6xl mx-auto flex items-center justify-between">

        {/* Brand Logo & Identity */}
        <div className="flex items-center gap-3">
          <div className="h-10 px-2 py-1 bg-white rounded-xl shadow-xs border border-[#e6cfa3]/40 flex items-center justify-center">
            <img
              src="/logo.png"
              alt="Rag Innovations Logo"
              className="h-8 object-contain"
            />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-slate-900 tracking-tight">RagAI</span>
              <span className="hidden sm:inline-flex text-[10px] font-semibold uppercase tracking-wider bg-[#9c1c2b]/10 text-[#9c1c2b] px-2 py-0.5 rounded-full">
                AI Assistant
              </span>
            </div>
            <p className="hidden md:block text-xs text-slate-500 font-medium">Rag Innovations · Menstrual Hygiene & Wellness</p>
          </div>
        </div>

        {/* Status & Actions */}
        <div className="flex items-center gap-2 sm:gap-4">

          {/* Health status badge */}
          {/* <div 
            className={`hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${
              isHealthy 
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                : isDegraded 
                ? 'bg-amber-50 text-amber-700 border-amber-200' 
                : 'bg-rose-50 text-rose-700 border-rose-200'
            }`}
            title={healthStatus?.error || (isHealthy ? "RAG & Groq AI Online" : "Connecting to backend...")}
          >
            <span className={`w-2 h-2 rounded-full ${
              isHealthy ? 'bg-emerald-500 animate-pulse' : isDegraded ? 'bg-amber-500' : 'bg-rose-500'
            }`} />
            <span>{isHealthy ? 'AI Online' : isDegraded ? 'Degraded' : 'Offline'}</span>
          </div> */}

          {/* Official Website Link */}
          <a
            href="https://www.raginnovations.com"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden md:inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-[#9c1c2b] px-3 py-1.5 rounded-full hover:bg-[#9c1c2b]/5 transition-colors border border-slate-200/60"
          >
            <span>raginnovations.com</span>
            <ExternalLink className="w-3.5 h-3.5 opacity-70" />
          </a>

          {/* Clear conversation */}
          {messageCount > 0 && (
            <button
              onClick={onClearChat}
              className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-rose-600 px-3 py-1.5 rounded-full hover:bg-rose-50 border border-slate-200/60 transition-colors cursor-pointer"
              title="Reset conversation"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Clear Chat</span>
            </button>
          )}

          {/* Talk to Team CTA */}
          <a
            href="https://www.raginnovations.com/contact"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 bg-[#9c1c2b] hover:bg-[#9c1c2b]/80 text-white text-xs font-semibold px-4 py-2 rounded-full shadow-sm hover:shadow transition-all transform hover:-translate-y-0.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Talk to Team</span>
          </a>

        </div>

      </div>
    </header>
  );
}
