import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  FileCheck,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Edit3
} from 'lucide-react';

export const AnalysisResults: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [submission, setSubmission] = useState<any | null>(null);
  const [report, setReport] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeFinding, setActiveFinding] = useState<any | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const res = await api.get(`/submissions/${id}`);
        setSubmission(res.data);
        if (res.data.reports && res.data.reports.length > 0) {
          const latestReport = res.data.reports[0];
          setReport(latestReport);
          if (latestReport.findings && latestReport.findings.length > 0) {
            setActiveFinding(latestReport.findings[0]);
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [id]);

  if (loading) {
    return <div className="p-12 text-center text-slate-400 text-sm">Loading governance analysis...</div>;
  }

  if (!submission || !report) {
    return (
      <div className="p-12 text-center text-slate-500 bg-white rounded-xl border border-slate-200">
        Analysis report not found for this submission.
      </div>
    );
  }

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'critical':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-100 text-rose-800">Critical</span>;
      case 'high':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-100 text-amber-800">High</span>;
      case 'medium':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-100 text-blue-800">Medium</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-100 text-slate-800">Low</span>;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-emerald-600 border-emerald-500';
    if (score >= 70) return 'text-amber-600 border-amber-500';
    return 'text-rose-600 border-rose-500';
  };

  return (
    <div className="space-y-6">
      {/* Top Bar */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs uppercase font-semibold text-slate-400">Analysis Results</span>
            <span className="text-slate-300">•</span>
            <span className="text-xs text-slate-500">{submission.content_type.replace('_', ' ')}</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight mt-1">{submission.title}</h1>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => navigate(`/analysis/editor/${submission.id}`)}
            className="flex items-center space-x-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors"
          >
            <Edit3 className="w-4 h-4" />
            <span>Open Smart Correction Editor</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Summary Score Card */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
        <div className="flex items-center space-x-4 border-b md:border-b-0 md:border-r border-slate-100 pb-4 md:pb-0 pr-4">
          <div
            className={`w-16 h-16 rounded-full border-4 flex items-center justify-center font-bold text-xl ${getScoreColor(
              report.overall_score
            )}`}
          >
            {report.overall_score}%
          </div>
          <div>
            <h4 className="font-semibold text-slate-900 text-sm">Adherence Score</h4>
            <p className="text-xs text-slate-500 mt-0.5">
              {report.overall_score >= 85 ? 'Strong Brand Alignment' : 'Violations Detected'}
            </p>
          </div>
        </div>

        <div className="md:col-span-3 space-y-2">
          <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-900 uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-indigo-600" />
            <span>Executive Governance Findings</span>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed">{report.summary}</p>
          <div className="flex flex-wrap gap-4 pt-1 text-xs text-slate-500">
            <span>Rules Inspected: <strong>{report.rules_checked_count}</strong></span>
            <span>Violations Found: <strong className="text-rose-600">{report.violations_count}</strong></span>
            <span>Unverified Claims: <strong className="text-amber-600">{report.unverified_claims_count}</strong></span>
            <span>Engine: <strong>{report.model_used}</strong></span>
          </div>
        </div>
      </div>

      {/* Findings Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Findings List */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs divide-y divide-slate-100">
          <div className="p-4 bg-slate-50/50 rounded-t-xl font-semibold text-xs text-slate-500 uppercase tracking-wider flex items-center justify-between">
            <span>Violations & Findings ({report.findings?.length || 0})</span>
          </div>

          {report.findings?.length === 0 ? (
            <div className="p-6 text-center text-emerald-600 text-sm font-medium">
              No violations detected! Content meets all brand standards.
            </div>
          ) : (
            report.findings.map((f: any, idx: number) => (
              <div
                key={f.id}
                onClick={() => setActiveFinding(f)}
                className={`p-4 cursor-pointer transition-colors space-y-1.5 ${
                  activeFinding?.id === f.id ? 'bg-indigo-50/70 border-l-4 border-indigo-600' : 'hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  {getSeverityBadge(f.severity)}
                  <span className="text-[11px] text-slate-400 uppercase font-medium">
                    {f.finding_type.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-xs font-semibold text-slate-900 line-clamp-1">
                  "{f.problematic_text}"
                </p>
                <p className="text-xs text-slate-500 line-clamp-1">{f.explanation}</p>
              </div>
            ))
          )}
        </div>

        {/* Active Finding Evidence & Grounding Card */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-6">
          {activeFinding ? (
            <>
              <div className="border-b border-slate-100 pb-4 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getSeverityBadge(activeFinding.severity)}
                  <span className="text-xs font-semibold uppercase text-slate-500">
                    {activeFinding.finding_type.replace('_', ' ')}
                  </span>
                </div>
                <span className="text-xs text-slate-400">Finding ID: {activeFinding.id.slice(0, 8)}</span>
              </div>

              {/* Problematic Snippet Highlight */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Identified Problematic Text
                </h4>
                <div className="p-4 rounded-lg bg-rose-50/70 border border-rose-200/80 text-rose-900 font-medium text-sm">
                  "{activeFinding.problematic_text}"
                </div>
              </div>

              {/* Governance Explanation */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Why This Violates Brand Governance
                </h4>
                <p className="text-sm text-slate-700 leading-relaxed">{activeFinding.explanation}</p>
              </div>

              {/* Supporting Evidence Citation (Mandatory Innovation A) */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center space-x-2 text-indigo-900 font-semibold text-xs">
                  <FileCheck className="w-4 h-4 text-indigo-600" />
                  <span>Ground Truth Supporting Evidence</span>
                </div>
                <div className="text-xs text-slate-700 space-y-1">
                  <p>
                    <span className="font-semibold text-slate-900">Source: </span>
                    {activeFinding.citation_source || 'Unverified Source'}
                  </p>
                  <p>
                    <span className="font-semibold text-slate-900">Section / Reference: </span>
                    {activeFinding.citation_section || 'N/A'}
                  </p>
                </div>
              </div>

              {/* Suggested Correction Preview */}
              {activeFinding.suggestions && activeFinding.suggestions.length > 0 && (
                <div className="p-4 rounded-xl bg-indigo-50/60 border border-indigo-100 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-indigo-950 uppercase tracking-wide">
                      Intent-Preserving Smart Correction
                    </span>
                    <button
                      onClick={() => navigate(`/analysis/editor/${submission.id}`)}
                      className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center space-x-1"
                    >
                      <span>Review in Editor</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <p className="text-xs text-slate-600">
                    <span className="font-medium text-slate-900">Suggested: </span>
                    "{activeFinding.suggestions[0].suggested_replacement}"
                  </p>
                  <p className="text-[11px] text-slate-500 italic">
                    {activeFinding.suggestions[0].intent_explanation}
                  </p>
                </div>
              )}
            </>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
              Select a finding to inspect supporting evidence and brand citations.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
