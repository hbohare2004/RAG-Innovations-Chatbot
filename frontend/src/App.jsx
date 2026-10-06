import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import WelcomeHero from './components/WelcomeHero';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import TypingIndicator from './components/TypingIndicator';
import { sendChatMessage, checkBackendHealth } from './services/api';
import { ArrowDown, AlertTriangle, RefreshCw } from 'lucide-react';

const STORAGE_KEY = 'raginno_chat_messages_v1';

export default function App() {
  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [isLoading, setIsLoading] = useState(false);
  const [healthStatus, setHealthStatus] = useState(null);
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Save messages to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch (e) {
      console.error('Failed to save to localStorage:', e);
    }
  }, [messages]);

  // Initial & periodic health check
  const performHealthCheck = async () => {
    const health = await checkBackendHealth();
    setHealthStatus(health);
  };

  useEffect(() => {
    performHealthCheck();
    const interval = setInterval(performHealthCheck, 30000);
    return () => clearInterval(interval);
  }, []);

  // Scroll to bottom
  const scrollToBottom = (behavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Track scroll position to show/hide scroll-to-bottom button
  const handleScroll = () => {
    if (!chatContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current;
    const isFarFromBottom = scrollHeight - scrollTop - clientHeight > 160;
    setShowScrollBottom(isFarFromBottom);
  };

  // Clear chat history
  const handleClearChat = () => {
    if (window.confirm("Are you sure you want to clear your conversation history?")) {
      setMessages([]);
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  // Send message handler
  const handleSendMessage = async (text) => {
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(text);
      
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources || [],
        timestamp: new Date().toISOString(),
        isError: response.status === 'error',
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `⚠️ **Connection Notice:** Unable to reach the RagAI backend service.\n\n*Details: ${err.message || 'Server connection failed'}*\n\nPlease ensure the FastAPI backend is running on \`http://localhost:8000\`.`,
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Suggestion prompt click
  const handleSelectPrompt = (promptText) => {
    handleSendMessage(promptText);
  };

  return (
    <div className="flex flex-col h-screen bg-[#faf7f2] text-slate-900 overflow-hidden font-sans">
      
      {/* Top Header */}
      <Header
        healthStatus={healthStatus}
        onClearChat={handleClearChat}
        messageCount={messages.length}
      />

      {/* Backend Offline Warning Banner */}
      {healthStatus?.status === 'offline' && (
        <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2 text-center text-xs text-amber-900 flex items-center justify-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span>Backend service is offline or connecting. Start the FastAPI backend on port 8000.</span>
          <button 
            onClick={performHealthCheck}
            className="underline font-semibold hover:text-amber-950 inline-flex items-center gap-1 ml-1 cursor-pointer"
          >
            <RefreshCw className="w-3 h-3" /> Retry
          </button>
        </div>
      )}

      {/* Main Chat Area */}
      <main
        ref={chatContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-2 sm:px-4 py-4 max-w-5xl w-full mx-auto relative scroll-smooth"
      >
        {messages.length === 0 ? (
          <WelcomeHero onSelectPrompt={handleSelectPrompt} />
        ) : (
          <div className="space-y-3 pb-8">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Scroll to Bottom Floating Button */}
      {showScrollBottom && (
        <button
          onClick={() => scrollToBottom('smooth')}
          className="fixed bottom-24 right-6 sm:right-12 z-30 p-2.5 rounded-full bg-white text-slate-700 shadow-lg border border-slate-200 hover:bg-slate-50 transition-all transform hover:scale-105 active:scale-95 animate-fade-in cursor-pointer"
          title="Scroll to latest message"
        >
          <ArrowDown className="w-4 h-4 text-[#9c1c2b]" />
        </button>
      )}

      {/* Bottom Input Area */}
      <footer className="w-full bg-gradient-to-t from-[#faf7f2] via-[#faf7f2]/95 to-transparent pt-2">
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          inputRef={inputRef}
        />
      </footer>

    </div>
  );
}
