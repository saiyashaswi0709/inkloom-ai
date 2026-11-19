import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { Sparkles, FileText, Send, ArrowRight, Check, AlertCircle, BookOpen } from 'lucide-react';

export const ContentAnalysisWorkspace: React.FC = () => {
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [contentType, setContentType] = useState('press_release');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sampleDrafts = [
    {
      label: 'Financial Press Release (Contains violations)',
      title: 'Global Custody & Infrastructure Announcement',
      type: 'press_release',
      text: `Aura Global is thrilled to announce our new custody service. With unbreakable security and instantaneous settlement, our new crypto wallet ensures your institutional investments are 100% risk-free. Over 50,000 banks trust our system every second, and we are the cheapest in the market.`
    },
    {
      label: 'Security Advisory (Clean & compliant)',
      title: 'Annual Infrastructure Cryptographic Attestation',
      type: 'technical_doc',
      text: `Aura Global deployed AES-256 GCM hardware-level encryption across all 14 global data centers. Our average transaction settlement latency has been independently verified at 14 milliseconds, supported by a defense-in-depth cryptographic architecture.`
    }
  ];

  const handleLoadSample = (sample: typeof sampleDrafts[0]) => {
    setTitle(sample.title);
    setContentType(sample.type);
    setContent(sample.text);
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || !title.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // 1. Create submission
      const subRes = await api.post('/submissions', {
        title,
        content_type: contentType,
        content,
      });

      const submissionId = subRes.data.id;

      // 2. Trigger analysis
      const analysisRes = await api.post('/analysis/run', {
        submission_id: submissionId,
      });

      // 3. Navigate to results page
      navigate(`/analysis/results/${submissionId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis pipeline encountered an error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Content Analysis Workspace</h1>
        <p className="text-sm text-slate-500 mt-1">
          Submit draft communication to run deterministic rule matching and evidence-backed AI verification.
        </p>
      </div>

      {/* Quick Test Samples */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="text-xs text-slate-600">
          <span className="font-semibold text-slate-800">Quick Test: </span>
          Load a pre-configured enterprise draft with brand test cases:
        </div>
        <div className="flex flex-wrap gap-2">
          {sampleDrafts.map((s, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleLoadSample(s)}
              className="text-xs px-3 py-1.5 rounded-lg border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 text-slate-700 font-medium transition-colors"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Analysis Form */}
      <form onSubmit={handleAnalyze} className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Content Title
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Q4 High-Yield Digital Asset Announcement"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Content Type
            </label>
            <select
              value={contentType}
              onChange={(e) => setContentType(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="press_release">Press Release</option>
              <option value="blog_post">Blog Post / Article</option>
              <option value="marketing_copy">Marketing Landing Copy</option>
              <option value="technical_doc">Technical Documentation</option>
              <option value="social_post">Social Media Announcement</option>
            </select>
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Draft Content For Brand Inspection
            </label>
            <span className="text-xs text-slate-400">{content.length} characters</span>
          </div>
          <textarea
            required
            rows={10}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste your communication draft here. The governance engine will scan for prohibited phrases, terminology mismatches, unverified factual claims, and tone inconsistencies..."
            className="w-full rounded-lg border border-slate-300 p-4 text-sm font-sans focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 leading-relaxed"
          />
        </div>

        <div className="pt-2 flex items-center justify-between border-t border-slate-100">
          <div className="flex items-center space-x-2 text-xs text-slate-500">
            <Sparkles className="w-4 h-4 text-indigo-500" />
            <span>Multi-stage check: Deterministic rules → Retrieval → AI validation</span>
          </div>

          <button
            type="submit"
            disabled={loading || !content.trim() || !title.trim()}
            className="flex items-center space-x-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Analysing Brand Adherence...</span>
              </>
            ) : (
              <>
                <span>Inspect Brand Governance</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
