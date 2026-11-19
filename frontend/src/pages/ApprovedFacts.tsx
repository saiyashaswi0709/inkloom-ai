import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { CheckCircle2, Plus, Shield, Trash2, Calendar, FileCheck } from 'lucide-react';

export const ApprovedFacts: React.FC = () => {
  const [facts, setFacts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form state
  const [statement, setStatement] = useState('');
  const [category, setCategory] = useState('Security');
  const [verificationSource, setVerificationSource] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFacts = async () => {
    try {
      const res = await api.get('/facts');
      setFacts(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFacts();
  }, []);

  const handleAddFact = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await api.post('/facts', {
        statement,
        category,
        verification_source: verificationSource,
      });
      setShowAddModal(false);
      setStatement('');
      setVerificationSource('');
      fetchFacts();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save fact');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to remove this fact?')) return;
    try {
      await api.delete(`/facts/${id}`);
      fetchFacts();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Approved Facts & Metrics</h1>
          <p className="text-sm text-slate-500 mt-1">
            Verified corporate claims, benchmarks, security certifications, and audited statistics.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Approved Fact</span>
        </button>
      </div>

      {/* Facts Grid */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 text-sm">Loading approved facts...</div>
      ) : facts.length === 0 ? (
        <div className="p-12 text-center text-slate-500 bg-white rounded-xl border border-slate-200">
          No approved facts recorded yet. Add corporate statistics to prevent unverified claims.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {facts.map((fact) => (
            <div
              key={fact.id}
              className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between space-y-4 hover:border-slate-300 transition-colors"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-100">
                    {fact.category}
                  </span>
                  <button
                    onClick={() => handleDelete(fact.id)}
                    className="text-slate-400 hover:text-rose-600 p-1 rounded transition-colors"
                    title="Remove fact"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
                <p className="text-sm font-medium text-slate-900 leading-relaxed">
                  "{fact.statement}"
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center space-x-2 text-xs text-slate-500">
                <FileCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                <span className="truncate">Source: {fact.verification_source}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Fact Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Add Approved Fact</h3>
            <p className="text-xs text-slate-500">
              Only verified claims will be recognized as factual truth by the AI detection model.
            </p>

            {error && (
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700">
                {error}
              </div>
            )}

            <form onSubmit={handleAddFact} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700">Statement</label>
                <textarea
                  required
                  rows={3}
                  value={statement}
                  onChange={(e) => setStatement(e.target.value)}
                  placeholder="e.g. Over 2,400 enterprise institutions actively deploy the Aura Cloud platform."
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                >
                  <option value="Security">Security</option>
                  <option value="Performance">Performance</option>
                  <option value="Market Reach">Market Reach</option>
                  <option value="Financials">Financials</option>
                  <option value="Compliance">Compliance</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">Verification Source</label>
                <input
                  type="text"
                  required
                  value={verificationSource}
                  onChange={(e) => setVerificationSource(e.target.value)}
                  placeholder="e.g. Audited SOC-2 Type II Report 2025"
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold"
                >
                  {saving ? 'Saving...' : 'Add Fact'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
