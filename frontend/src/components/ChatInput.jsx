import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

export default function ChatInput({ onSendMessage, isLoading, inputRef }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (inputRef) {
      inputRef.current = textareaRef.current;
    }
  }, [inputRef]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    onSendMessage(trimmed);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-4 pt-2">
      <div className="relative glass-panel rounded-3xl p-2 shadow-lg border border-[#e6cfa3]/60 focus-within:border-[#9c1c2b] focus-within:ring-2 focus-within:ring-[#9c1c2b]/15 transition-all">
        <form onSubmit={handleSubmit} className="flex items-end gap-2">

          {/* Text Area */}
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask RagAI..."
            disabled={isLoading}
            className="w-full resize-none bg-transparent px-4 py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none max-h-[180px] disabled:opacity-50"
          />

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`flex-shrink-0 w-11 h-11 rounded-2xl flex items-center justify-center transition-all cursor-pointer ${input.trim() && !isLoading
              ? 'bg-gradient-to-tr from-[#9c1c2b] to-[#e4572e] text-white shadow-md shadow-[#9c1c2b]/25 hover:scale-105 active:scale-95'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'
              }`}
            title="Send message (Enter)"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin text-[#9c1c2b]" />
            ) : (
              <Send className="w-4 h-4 translate-x-px" />
            )}
          </button>

        </form>
      </div>

      {/* Safety & Compliance disclaimer */}
      <p className="text-center text-[11px] text-slate-500 mt-2">
        <span className="font-semibold text-slate-600">RagAI</span> provides educational and company information. For personal medical concerns, please consult a qualified healthcare professional.
      </p>
    </div>
  );
}
