import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { FileText, ArrowRight, Filter, Sparkles, CheckCircle2 } from 'lucide-react';
import { formatDateIST } from '../utils/date';

export const SubmissionHistory: React.FC = () => {
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');

  const fetchSubmissions = async () => {
    try {
      const url = statusFilter === 'all' ? '/submissions' : `/submissions?status_filter=${statusFilter}`;
      const res = await api.get(url);
      setSubmissions(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubmissions();
  }, [statusFilter]);

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
      case 'changes_requested':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800">Changes Requested</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-800">Draft</span>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Submission History</h1>
          <p className="text-sm text-slate-500 mt-1">
            Complete audit trail of governed marketing and corporate communications.
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs font-medium rounded-lg border border-slate-200 px-3 py-2 bg-white text-slate-700 focus:outline-none focus:border-indigo-500"
          >
            <option value="all">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="needs_changes">Needs Changes</option>
            <option value="ready_for_review">Ready for Review</option>
            <option value="in_review">In Review</option>
            <option value="approved">Approved</option>
            <option value="changes_requested">Changes Requested</option>
          </select>
        </div>
      </div>

      {/* Submissions List */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">Loading submission records...</div>
        ) : submissions.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            No submissions found under the selected filter.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {submissions.map((sub) => {
              const latestReport = sub.reports?.[0];
              return (
                <div
                  key={sub.id}
                  className="p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4 hover:bg-slate-50/70 transition-colors"
                >
                  <div className="space-y-1.5 max-w-xl">
                    <div className="flex items-center space-x-3">
                      <h3 className="font-semibold text-slate-900 text-sm">{sub.title}</h3>
                      <span className="text-[11px] font-medium uppercase px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                        {sub.content_type.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                      {sub.current_text || sub.original_text}
                    </p>
                    <div className="flex items-center space-x-3 text-xs text-slate-400 pt-0.5">
                      <span>Revisions: <strong>{sub.revisions?.length || 1}</strong></span>
                      <span>•</span>
                      <span>Created: {formatDateIST(sub.created_at)}</span>
                      {latestReport && (
                        <>
                          <span>•</span>
                          <span className="font-semibold text-indigo-700">
                            Score: {latestReport.overall_score}%
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 self-end md:self-center">
                    {getStatusBadge(sub.status)}
                    <button
                      onClick={() => navigate(`/analysis/results/${sub.id}`)}
                      className="px-3 py-1.5 border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 rounded-lg text-xs font-semibold text-slate-700 transition-colors flex items-center space-x-1"
                    >
                      <span>Results</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
