import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  FileText,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { formatDateIST } from '../utils/date';

export const Dashboard: React.FC = () => {
  const { organisation, role } = useAuth();
  const navigate = useNavigate();

  const [metrics, setMetrics] = useState<any>(null);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsRes, subsRes] = await Promise.all([
          api.get('/analytics/summary'),
          api.get('/submissions')
        ]);
        setMetrics(analyticsRes.data);
        setSubmissions(subsRes.data.slice(0, 5));
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">Approved</span>;
      case 'in_review':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800">In Review</span>;
      case 'needs_changes':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800">Needs Changes</span>;
      case 'ready_for_review':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">Ready for Review</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-800">Draft</span>;
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Governance Dashboard</h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time brand compliance monitoring for <span className="font-semibold text-slate-800">{organisation?.name}</span>
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => navigate('/analysis')}
            className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            <span>New Content Check</span>
          </button>
          {role === 'reviewer' && (
            <button
              onClick={() => navigate('/reviews')}
              className="flex items-center space-x-2 px-4 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-lg text-sm font-medium shadow-xs transition-colors"
            >
              <ShieldCheck className="w-4 h-4 text-purple-600" />
              <span>Review Queue</span>
            </button>
          )}
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Brand Adherence</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline space-x-2">
            <span className="text-3xl font-bold text-slate-900">
              {metrics ? `${metrics.average_adherence_score}%` : '--'}
            </span>
            <span className="text-xs text-emerald-600 font-medium">Verified index</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Submissions</span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline space-x-2">
            <span className="text-3xl font-bold text-slate-900">
              {metrics ? metrics.total_submissions : '--'}
            </span>
            <span className="text-xs text-slate-500 font-medium">Governed items</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Pending Action</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline space-x-2">
            <span className="text-3xl font-bold text-slate-900">
              {metrics ? metrics.pending_submissions : '--'}
            </span>
            <span className="text-xs text-amber-600 font-medium">Awaiting review</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Approved Content</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline space-x-2">
            <span className="text-3xl font-bold text-slate-900">
              {metrics ? metrics.approved_submissions : '--'}
            </span>
            <span className="text-xs text-emerald-600 font-medium">Ready to publish</span>
          </div>
        </div>
      </div>

      {/* Actionable Recommendations Callout */}
      {metrics?.actionable_recommendations && metrics.actionable_recommendations.length > 0 && (
        <div className="bg-indigo-50/60 border border-indigo-100 rounded-xl p-5">
          <div className="flex items-center space-x-2 text-indigo-950 font-semibold text-sm mb-2">
            <AlertCircle className="w-4 h-4 text-indigo-600" />
            <span>Governance Intelligence Recommendation</span>
          </div>
          <p className="text-sm text-indigo-900">
            {metrics.actionable_recommendations[0]}
          </p>
        </div>
      )}

      {/* Recent Submissions */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="font-semibold text-slate-900 text-sm">Recent Governed Submissions</h2>
          <button
            onClick={() => navigate('/submissions')}
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center space-x-1"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading activity...</div>
        ) : submissions.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">
            No submissions yet. Start your first brand governance analysis!
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {submissions.map((sub) => (
              <div
                key={sub.id}
                onClick={() => navigate(`/analysis/results/${sub.id}`)}
                className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 cursor-pointer transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-slate-900 text-sm">{sub.title}</span>
                    <span className="text-xs text-slate-500 uppercase tracking-wide bg-slate-100 px-2 py-0.5 rounded">
                      {sub.content_type.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 line-clamp-1 max-w-xl">
                    {sub.current_text || sub.original_text}
                  </p>
                </div>

                <div className="flex items-center space-x-4">
                  {getStatusBadge(sub.status)}
                  <span className="text-xs text-slate-400">
                    {formatDateIST(sub.created_at)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
