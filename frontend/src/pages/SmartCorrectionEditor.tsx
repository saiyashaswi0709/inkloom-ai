import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';
import {
  Check,
  X,
  Edit2,
  Send,
  ArrowLeft,
  Sparkles,
  History,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { formatTimeIST } from '../utils/date';

export const SmartCorrectionEditor: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [submission, setSubmission] = useState<any | null>(null);
  const [report, setReport] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchDetails = async () => {
    try {
      const res = await api.get(`/submissions/${id}`);
      setSubmission(res.data);
      if (res.data.reports && res.data.reports.length > 0) {
        setReport(res.data.reports[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const handleUpdateStatus = async (suggestionId: string, status: string, userText?: string) => {
    setActionLoading(suggestionId);
    setSuccessMessage(null);
    try {
      const res = await api.put(`/corrections/${suggestionId}`, {
        status,
        user_edited_text: userText,
      });

      // Update UI immediately after successful response (Requirement 4)
      if (report && report.findings) {
        setReport({
          ...report,
          findings: report.findings.map((f: any) => ({
            ...f,
            suggestions: (f.suggestions || []).map((s: any) =>
              s.id === suggestionId ? { ...s, status: res.data.status, user_edited_text: res.data.user_edited_text } : s
            ),
          })),
        });
      }

      setSuccessMessage(status === 'accepted' || status === 'edited' ? 'Correction applied and revision saved.' : 'Suggestion dismissed.');
      setEditingId(null);
      await fetchDetails();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleSubmitForReview = async () => {
    try {
      await api.post(`/submissions/${id}/submit-for-review`);
      navigate('/submissions');
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div className="p-12 text-center text-slate-400 text-sm">Loading Smart Correction Editor...</div>;
  }

  if (!submission || !report) {
    return <div className="p-12 text-center text-slate-500">Submission not found.</div>;
  }

  const allSuggestions = report.findings?.flatMap((f: any) =>
    (f.suggestions || []).map((s: any) => ({ ...s, finding: f }))
  ) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <button
            onClick={() => navigate(`/analysis/results/${submission.id}`)}
            className="flex items-center space-x-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Analysis Report</span>
          </button>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Smart Correction Editor</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Preserve your core message intent while seamlessly aligning with approved brand guidelines.
          </p>
        </div>

        <button
          onClick={handleSubmitForReview}
          className="flex items-center space-x-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors"
        >
          <Send className="w-4 h-4" />
          <span>Submit for Review</span>
        </button>
      </div>

      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Editor Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Interactive Suggestions List */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900 text-sm flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <span>Recommended Smart Corrections ({allSuggestions.length})</span>
            </h3>
            <span className="text-xs text-slate-400">Accept, Reject or Edit</span>
          </div>

          {allSuggestions.length === 0 ? (
            <div className="p-8 text-center bg-white rounded-xl border border-slate-200 text-slate-500 text-sm">
              No pending correction suggestions. Content is aligned with brand policies.
            </div>
          ) : (
            allSuggestions.map((s: any) => {
              const isAccepted = s.status === 'accepted';
              const isRejected = s.status === 'rejected';
              const isEdited = s.status === 'edited';
              const isDecided = isAccepted || isRejected || isEdited;

              return (
                <div
                  key={s.id}
                  className={`bg-white p-5 rounded-xl border shadow-xs transition-all space-y-4 ${
                    isAccepted || isEdited
                      ? 'border-emerald-300 bg-emerald-50/20'
                      : isRejected
                      ? 'border-slate-200 opacity-60'
                      : 'border-slate-200 hover:border-indigo-200'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-400 uppercase tracking-wide">
                      {s.finding.finding_type.replace('_', ' ')}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded-full font-semibold uppercase text-[10px] ${
                        isAccepted || isEdited
                          ? 'bg-emerald-100 text-emerald-800'
                          : isRejected
                          ? 'bg-slate-100 text-slate-600'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {s.status}
                    </span>
                  </div>

                  {/* Original Sentence */}
                  <div>
                    <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                      Original Draft Text
                    </label>
                    <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-100 mt-1 line-through decoration-rose-400">
                      {s.original_sentence}
                    </p>
                  </div>

                  {/* Suggested Replacement */}
                  <div>
                    <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                      Suggested Brand Replacement
                    </label>
                    {editingId === s.id ? (
                      <div className="mt-1 space-y-2">
                        <textarea
                          rows={3}
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          className="w-full rounded-md border border-indigo-400 p-2 text-xs focus:outline-none"
                        />
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={() => setEditingId(null)}
                            className="px-3 py-1 text-xs border border-slate-200 rounded text-slate-600 hover:bg-slate-50"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => handleUpdateStatus(s.id, 'edited', editText)}
                            className="px-3 py-1 text-xs bg-indigo-600 text-white rounded font-medium"
                          >
                            Save & Apply
                          </button>
                        </div>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-900 bg-indigo-50/50 p-3 rounded-lg border border-indigo-100 mt-1 font-medium">
                        {s.user_edited_text || s.suggested_replacement}
                      </p>
                    )}
                  </div>

                  {/* Intent Explanation */}
                  {s.intent_explanation && (
                    <p className="text-[11px] text-slate-500 italic bg-white p-2 rounded border border-slate-100">
                      💡 <strong>Intent Preservation:</strong> {s.intent_explanation}
                    </p>
                  )}

                  {/* Action Controls */}
                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                    {isDecided ? (
                      isAccepted || isEdited ? (
                        <div className="w-full flex items-center justify-between">
                          <span className="text-xs font-semibold text-emerald-700 flex items-center space-x-1.5">
                            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                            <span>Correction Applied</span>
                          </span>
                          <span className="text-[11px] text-slate-400 italic">No further actions required</span>
                        </div>
                      ) : (
                        <div className="w-full flex items-center justify-between">
                          <span className="text-xs font-semibold text-slate-500 flex items-center space-x-1.5">
                            <X className="w-4 h-4 text-slate-400" />
                            <span>Suggestion Dismissed</span>
                          </span>
                          <span className="text-[11px] text-slate-400 italic">No further actions required</span>
                        </div>
                      )
                    ) : (
                      <>
                        <button
                          type="button"
                          onClick={() => {
                            setEditingId(s.id);
                            setEditText(s.user_edited_text || s.suggested_replacement);
                          }}
                          className="text-xs font-semibold text-slate-500 hover:text-slate-800 flex items-center space-x-1"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                          <span>Customise</span>
                        </button>

                        <div className="flex items-center space-x-2">
                          <button
                            type="button"
                            onClick={() => handleUpdateStatus(s.id, 'rejected')}
                            disabled={actionLoading === s.id}
                            className="px-3 py-1.5 border border-slate-200 hover:bg-slate-100 text-slate-600 rounded-lg text-xs font-medium transition-colors"
                          >
                            <X className="w-3.5 h-3.5 inline mr-1" />
                            Reject
                          </button>
                          <button
                            type="button"
                            onClick={() => handleUpdateStatus(s.id, 'accepted')}
                            disabled={actionLoading === s.id}
                            className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-medium transition-colors shadow-xs"
                          >
                            <Check className="w-3.5 h-3.5 inline mr-1" />
                            Accept
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right: Live Current Text Preview with Revision History */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900 text-sm flex items-center space-x-2">
              <History className="w-4 h-4 text-slate-600" />
              <span>Current Draft (Revision #{submission.revisions?.length || 1})</span>
            </h3>
            <span className="text-xs text-slate-400">Live preview</span>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-4">
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 text-xs text-slate-800 whitespace-pre-wrap leading-relaxed font-sans min-h-[300px]">
              {submission.current_text}
            </div>

            {/* Persistent Revisions Trail */}
            <div className="space-y-2 pt-4 border-t border-slate-100">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Revision Audit History ({submission.revisions?.length || 0})
              </h4>
              <div className="space-y-2">
                {(submission.revisions || []).map((rev: any) => (
                  <div
                    key={rev.id}
                    className="flex items-center justify-between text-xs p-2 rounded bg-slate-50/70 border border-slate-100"
                  >
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-indigo-700">Rev #{rev.revision_number}</span>
                      <span className="text-slate-600 truncate max-w-xs">{rev.change_summary}</span>
                    </div>
                    <span className="text-slate-400">
                      {formatTimeIST(rev.created_at)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
