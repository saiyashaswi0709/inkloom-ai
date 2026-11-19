import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Scroll, CheckCircle2, SpellCheck, ArrowRight, Shield, BookOpen } from 'lucide-react';

export const BrandKnowledgeBase: React.FC = () => {
  const navigate = useNavigate();

  const hubs = [
    {
      title: 'Brand Guidelines & Documents',
      description: 'Upload PDF and DOCX brand books, style standards, tone principles, and messaging frameworks.',
      icon: Scroll,
      to: '/guidelines',
      stats: 'Structured Chunks & Ground Truth',
      color: 'bg-indigo-50 text-indigo-600',
    },
    {
      title: 'Approved Corporate Facts',
      description: 'Verified metrics, security credentials, customer numbers, and performance benchmarks.',
      icon: CheckCircle2,
      to: '/facts',
      stats: 'Prevents Unsupported Claims',
      color: 'bg-emerald-50 text-emerald-600',
    },
    {
      title: 'Rules & Terminology Dictionary',
      description: 'Deterministic word replacements, prohibited marketing jargon, and regex pattern matching.',
      icon: SpellCheck,
      to: '/rules',
      stats: 'Real-time Deterministic Detection',
      color: 'bg-purple-50 text-purple-600',
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Brand Knowledge Base</h1>
        <p className="text-sm text-slate-500 mt-1">
          The single source of truth for your brand. All AI analysis and verification models reference these records.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {hubs.map((hub) => {
          const Icon = hub.icon;
          return (
            <div
              key={hub.title}
              onClick={() => navigate(hub.to)}
              className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs hover:border-indigo-300 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
            >
              <div className="space-y-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${hub.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 text-base">{hub.title}</h3>
                  <p className="text-xs text-slate-500 mt-1 leading-relaxed">{hub.description}</p>
                </div>
              </div>

              <div className="pt-6 mt-6 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">{hub.stats}</span>
                <div className="flex items-center text-xs font-semibold text-indigo-600 space-x-1">
                  <span>Manage</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Governance Philosophy Card */}
      <div className="p-6 rounded-xl bg-slate-100/70 border border-slate-200 space-y-3">
        <div className="flex items-center space-x-2 text-slate-900 font-semibold text-sm">
          <Shield className="w-4 h-4 text-indigo-600" />
          <span>Zero-Hallucination Evidence Grounding</span>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          Inkloom AI implements deterministic rule matching coupled with context-aware semantic retrieval. When drafts make claims that cannot be traced to an active Approved Fact or Guideline Chunk, the claim is highlighted as unverified rather than assumed true.
        </p>
      </div>
    </div>
  );
};
