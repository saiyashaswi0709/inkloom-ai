import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  ShieldCheck,
  CheckCircle,
  AlertTriangle,
  Send,
  MessageSquare,
  FileText,
  Clock,
  History
} from 'lucide-react';
import { formatDateIST } from '../utils/date';

export const ReviewCentre: React.FC = () => {
  const { role, user } = useAuth();
  const [queue, setQueue] = useState<any[]>([]);
  const [selectedSub, setSelectedSub] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  // Review form state
  const [decision, setDecision] = useState<'approved' | 'changes_requested'>('approved');
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const isReviewer = role === 'reviewer' || role === 'admin';

  const fetchQueue = async () => {
    try {
      const res = await api.get('/reviews/queue');
      setQueue(res.data);
      if (res.data.length > 0 && !selectedSub) {
        setSelectedSub(res.data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSub) return;

    setSubmitting(true);
    setSuccessMsg(null);
    try {
      await api.post(`/reviews?submission_id=${selectedSub.id}`, {
        decision,
        comments,
        feedback_tags: [decision === 'approved' ? 'Verified Compliant' : 'Requires Revision'],
      });
      setSuccessMsg(`Submission successfully ${decision === 'approved' ? 'approved for publication' : 'sent back with change requests'}.`);
      setComments('');
      await fetchQueue();
    } catch (err: any) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Review Centre</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-700">
              Human Reviewer Authority
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Human reviewers retain final authority over content publication and brand compliance.
          </p>
        </div>
      </div>

      {!isReviewer && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800 flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
          <span>
            You are signed in as <strong>{role?.toUpperCase()}</strong>. Approval decisions require <strong>Reviewer</strong> permissions. Switch roles in the demo menu to test approvals.
          </span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Queue List */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs divide-y divide-slate-100">
          <div className="p-4 bg-slate-50/50 rounded-t-xl font-semibold text-xs text-slate-500 uppercase tracking-wider flex items-center justify-between">
            <span>Awaiting Review ({queue.length})</span>
          </div>

          {loading ? (
            <div className="p-8 text-center text-slate-400 text-sm">Loading review queue...</div>
          ) : queue.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-sm">
              All submissions reviewed! No pending items.
            </div>
          ) : (
            queue.map((sub) => (
              <div
                key={sub.id}
                onClick={() => setSelectedSub(sub)}
                className={`p-4 cursor-pointer transition-colors space-y-1.5 ${
                  selectedSub?.id === sub.id ? 'bg-purple-50/60 border-l-4 border-purple-600' : 'hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-900 text-sm">{sub.title}</span>
                  <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {sub.status.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-xs text-slate-500 line-clamp-1">{sub.current_text}</p>
                <div className="text-[11px] text-slate-400">
                  Rev #{sub.revisions?.length || 1} • {formatDateIST(sub.updated_at)}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Selected Submission Review Inspection & Decision */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-6">
          {selectedSub ? (
            <>
              <div className="flex items-start justify-between border-b border-slate-100 pb-4">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">{selectedSub.title}</h2>
                  <p className="text-xs text-slate-500 mt-1">
                    Submitted by: <strong>{selectedSub.author?.full_name || 'Staff Author'}</strong> • Type: {selectedSub.content_type}
                  </p>
                </div>
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800">
                  {selectedSub.status.toUpperCase()}
                </span>
              </div>

              {/* Text Inspection */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Draft Content Pending Approval
                </h4>
                <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-800 whitespace-pre-wrap leading-relaxed">
                  {selectedSub.current_text}
                </div>
              </div>

              {/* Review History */}
              {selectedSub.reviews && selectedSub.reviews.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Previous Review Attestations
                  </h4>
                  <div className="space-y-2">
                    {selectedSub.reviews.map((rev: any) => (
                      <div key={rev.id} className="p-3 bg-slate-50 rounded-lg border border-slate-100 text-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className={`font-semibold uppercase ${rev.decision === 'approved' ? 'text-emerald-700' : 'text-rose-700'}`}>
                            {rev.decision}
                          </span>
                          <span className="text-slate-400">{formatDateIST(rev.created_at)}</span>
                        </div>
                        {rev.comments && <p className="text-slate-600">{rev.comments}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Reviewer Action Form */}
              {isReviewer && (
                <form onSubmit={handleReviewSubmit} className="pt-4 border-t border-slate-100 space-y-4">
                  <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    Submit Governance Attestation
                  </h4>

                  <div className="flex items-center space-x-4">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="radio"
                        name="decision"
                        value="approved"
                        checked={decision === 'approved'}
                        onChange={() => setDecision('approved')}
                        className="text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="text-xs font-semibold text-emerald-800 bg-emerald-50 px-3 py-1 rounded-md border border-emerald-200">
                        Approve For Publication
                      </span>
                    </label>

                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="radio"
                        name="decision"
                        value="changes_requested"
                        checked={decision === 'changes_requested'}
                        onChange={() => setDecision('changes_requested')}
                        className="text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="text-xs font-semibold text-rose-800 bg-rose-50 px-3 py-1 rounded-md border border-rose-200">
                        Request Changes
                      </span>
                    </label>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">
                      Reviewer Feedback & Notes
                    </label>
                    <textarea
                      rows={3}
                      value={comments}
                      onChange={(e) => setComments(e.target.value)}
                      placeholder="Add compliance feedback, verification sources, or required modifications for the author..."
                      className="w-full rounded-md border border-slate-300 p-2.5 text-xs focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={submitting}
                      className={`px-6 py-2 rounded-lg text-xs font-semibold text-white transition-colors ${
                        decision === 'approved' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-rose-600 hover:bg-rose-700'
                      }`}
                    >
                      {submitting ? 'Submitting Review...' : decision === 'approved' ? 'Sign & Approve' : 'Submit Change Request'}
                    </button>
                  </div>
                </form>
              )}
            </>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
              Select a submission from the review queue.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
