import React from 'react';
import { X, ExternalLink, FileText } from 'lucide-react';

export default function SourceModal({ isOpen, onClose, sources }) {
  if (!isOpen || !sources || sources.length === 0) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-fade-in">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] flex flex-col shadow-2xl border border-[#e6cfa3]/60 overflow-hidden">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-[#f5ecd8]/40">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#9c1c2b]/10 text-[#9c1c2b] flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Retrieved Context Sources</h3>
              <p className="text-xs text-slate-500">{sources.length} knowledge base excerpt{sources.length > 1 ? 's' : ''} referenced</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 overflow-y-auto space-y-4">
          {sources.map((src, index) => (
            <div
              key={index}
              className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/60 hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-[#9c1c2b]/10 text-[#9c1c2b]">
                  Source #{index + 1}
                </span>
                {src.source && (
                  <a
                    href={src.source}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-medium text-[#e4572e] hover:underline inline-flex items-center gap-1"
                  >
                    <span>{src.source.replace(/^https?:\/\/(www\.)?/, '')}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
              <p className="text-xs text-slate-700 leading-relaxed font-mono whitespace-pre-wrap bg-white p-3 rounded-lg border border-slate-200/60">
                {src.content}
              </p>
            </div>
          ))}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-100 bg-slate-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-full bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-semibold transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
