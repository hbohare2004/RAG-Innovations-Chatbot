import React from 'react';

export default function TypingIndicator() {
  return (
    <div className="flex w-full py-3 px-2 sm:px-4 animate-fade-in justify-start">
      <div className="flex gap-3 max-w-3xl w-full">
        {/* Avatar */}
        <div className="w-9 h-9 rounded-2xl bg-white border border-[#e6cfa3]/60 p-1 flex items-center justify-center shadow-xs flex-shrink-0">
          <img src="/logo.png" alt="Rag Innovations" className="w-7 h-7 object-contain" />
        </div>

        <div className="flex flex-col items-start">
          <div className="flex items-center gap-2 mb-1 px-1">
            <span className="text-xs font-semibold text-slate-700">RagAI Assistant</span>
            <span className="text-[10px] text-slate-400">Thinking...</span>
          </div>

          <div className="px-5 py-3.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs rounded-tl-none flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#9c1c2b] animate-bounce [animation-delay:-0.3s]"></span>
            <span className="w-2 h-2 rounded-full bg-[#e4572e] animate-bounce [animation-delay:-0.15s]"></span>
            <span className="w-2 h-2 rounded-full bg-[#e6cfa3] animate-bounce"></span>
          </div>
        </div>
      </div>
    </div>
  );
}
