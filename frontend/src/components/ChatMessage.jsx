import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check, BookOpen } from 'lucide-react';
import SourceModal from './SourceModal';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const [showSources, setShowSources] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy message:', err);
    }
  };

  const sources = message.sources || [];
  const hasSources = sources.length > 0;

  return (
    <div className={`flex w-full py-3 px-2 sm:px-4 animate-fade-in ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex gap-3 max-w-3xl w-full ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        
        {/* Avatar */}
        <div className="flex-shrink-0">
          {isUser ? (
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-[#9c1c2b] to-[#b42d3e] text-white flex items-center justify-center font-bold text-xs shadow-sm">
              You
            </div>
          ) : (
            <div className="w-9 h-9 rounded-2xl bg-white border border-[#e6cfa3]/60 p-1 flex items-center justify-center shadow-xs">
              <img src="/logo.png" alt="Rag Innovations" className="w-7 h-7 object-contain" />
            </div>
          )}
        </div>

        {/* Message Container */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[88%] sm:max-w-[85%]`}>
          
          {/* Header info (Name & Time) */}
          <div className="flex items-center gap-2 mb-1 px-1">
            <span className="text-xs font-semibold text-slate-700">
              {isUser ? 'You' : 'RagAI Assistant'}
            </span>
            {message.timestamp && (
              <span className="text-[10px] text-slate-400">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            )}
          </div>

          {/* Bubble */}
          <div
            className={`p-4 sm:p-5 rounded-2xl transition-all shadow-xs ${
              isUser
                ? 'bg-gradient-to-r from-[#9c1c2b] to-[#b42d3e] text-white rounded-tr-none shadow-sm'
                : message.isError
                ? 'bg-rose-50 border border-rose-200 text-rose-900 rounded-tl-none'
                : 'bg-white border border-slate-200/90 text-slate-800 rounded-tl-none shadow-xs'
            }`}
          >
            {isUser ? (
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
            ) : (
              <div className="markdown-content text-sm text-slate-800 leading-relaxed overflow-hidden">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
          </div>

          {/* Assistant Actions: Copy & Sources */}
          {!isUser && !message.isError && (
            <div className="flex items-center gap-2 mt-2 px-1">
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 hover:text-slate-800 px-2 py-1 rounded-md hover:bg-slate-100 transition-colors cursor-pointer"
                title="Copy answer to clipboard"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied!' : 'Copy'}</span>
              </button>

              {hasSources && (
                <button
                  onClick={() => setShowSources(true)}
                  className="inline-flex items-center gap-1 text-[11px] font-medium text-[#9c1c2b] hover:text-[#b42d3e] px-2 py-1 rounded-md bg-[#9c1c2b]/5 hover:bg-[#9c1c2b]/10 transition-colors border border-[#9c1c2b]/20 cursor-pointer"
                >
                  <BookOpen className="w-3.5 h-3.5" />
                  <span>{sources.length} Verified Source{sources.length > 1 ? 's' : ''}</span>
                </button>
              )}
            </div>
          )}

        </div>

      </div>

      {/* Sources modal */}
      {hasSources && (
        <SourceModal
          isOpen={showSources}
          onClose={() => setShowSources(false)}
          sources={sources}
        />
      )}
    </div>
  );
}
