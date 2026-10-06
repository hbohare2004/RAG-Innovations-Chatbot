import React from 'react';
import { Sparkles, ShoppingBag, Flame, School, HeartPulse, HelpCircle } from 'lucide-react';

const SUGGESTED_TOPICS = [
  {
    icon: ShoppingBag,
    title: "Sanitary Pad Vending Machines",
    prompt: "Tell me about Rag Innovations' sanitary pad vending machines and their features.",
  },
  {
    icon: Flame,
    title: "Eco-friendly Incinerators",
    prompt: "How do Rag Innovations' sanitary napkin incinerators work for eco-friendly disposal?",
  },
  {
    icon: School,
    title: "School MHM Compliance",
    prompt: "What are the school Menstrual Hygiene Management (MHM) compliance solutions offered?",
  },
  {
    icon: HeartPulse,
    title: "Period & Wellness Support",
    prompt: "What are natural ways to manage severe period cramps and fatigue?",
  },
];

export default function WelcomeHero({ onSelectPrompt }) {
  return (
    <div className="max-w-3xl mx-auto text-center py-6 sm:py-8 px-4 animate-fade-in">

      {/* Centered Brand Logo */}
      {/* <div className="flex justify-center mb-5">
        <div className="p-3 bg-white rounded-2xl shadow-sm border border-[#e6cfa3]/50 inline-flex items-center justify-center">
          <img 
            src="/logo.png" 
            alt="Rag Innovations" 
            className="h-14 sm:h-16 object-contain"
          />
        </div>
      </div> */}

      {/* Brand kicker */}
      {/* <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#f5ecd8] border border-[#e6cfa3] text-[#9c1c2b] text-xs font-semibold uppercase tracking-wider mb-4 shadow-xs">
        <Sparkles className="w-3.5 h-3.5 text-[#e4572e]" />
        <span>Official AI Companion</span>
      </div> */}

      {/* Main Title */}
      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mb-2">
        How can I assist you today?
      </h1>

      <p className="text-xs sm:text-sm text-slate-600 max-w-xl mx-auto leading-relaxed mb-6">
        Ask any questions regarding automated sanitary napkin vending machines, eco-friendly incinerators, school hygiene compliance, or supportive menstrual health guidance.
      </p>

      {/* Suggestion Grid */}
      <div className="text-left mb-4">
        <div className="flex items-center gap-2 mb-3 px-1">
          <HelpCircle className="w-4 h-4 text-[#9c1c2b]" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Suggested Questions
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {SUGGESTED_TOPICS.map((item, index) => {
            const Icon = item.icon;
            return (
              <button
                key={index}
                onClick={() => onSelectPrompt(item.prompt)}
                className="group p-3.5 rounded-2xl border border-slate-200/80 bg-white hover:border-[#9c1c2b]/40 hover:shadow-md transition-all text-left flex flex-col justify-between hover:-translate-y-0.5 cursor-pointer"
              >
                <div className="flex items-center gap-2.5 mb-1.5">
                  <div className="w-7 h-7 rounded-xl bg-[#9c1c2b]/10 text-[#9c1c2b] flex items-center justify-center group-hover:bg-[#9c1c2b] group-hover:text-white transition-colors">
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-xs sm:text-sm font-bold text-slate-800 group-hover:text-[#9c1c2b] transition-colors">
                    {item.title}
                  </span>
                </div>
                <p className="text-[11px] sm:text-xs text-slate-500 line-clamp-2 leading-relaxed">
                  "{item.prompt}"
                </p>
              </button>
            );
          })}
        </div>
      </div>

    </div>
  );
}
