import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { SpellCheck, Plus, Trash2, ArrowRight, AlertTriangle, ShieldAlert } from 'lucide-react';

export const BrandRules: React.FC = () => {
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form
  const [ruleType, setRuleType] = useState('terminology');
  const [prohibitedTerm, setProhibitedTerm] = useState('');
  const [preferredTerm, setPreferredTerm] = useState('');
  const [severity, setSeverity] = useState('high');
  const [explanation, setExplanation] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRules = async () => {
    try {
      const res = await api.get('/rules');
      setRules(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleAddRule = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await api.post('/rules', {
        rule_type: ruleType,
        prohibited_term: prohibitedTerm,
        preferred_term: preferredTerm,
        severity,
        explanation,
      });
      setShowAddModal(false);
      setProhibitedTerm('');
      setPreferredTerm('');
      setExplanation('');
      fetchRules();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save rule');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to remove this rule?')) return;
    try {
      await api.delete(`/rules/${id}`);
      fetchRules();
    } catch (err) {
      console.error(err);
    }
  };

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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Rules & Terminology Dictionary</h1>
          <p className="text-sm text-slate-500 mt-1">
            Deterministic rules to block prohibited phrases, enforce official product names, and replace jargon.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Brand Rule</span>
        </button>
      </div>

      {/* Rules Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading rules...</div>
        ) : rules.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">No rules configured yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50/60 border-b border-slate-200 text-xs text-slate-500 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="px-6 py-3.5">Type & Severity</th>
                  <th className="px-6 py-3.5">Prohibited / Restricted</th>
                  <th className="px-6 py-3.5">Preferred Term</th>
                  <th className="px-6 py-3.5">Governance Explanation</th>
                  <th className="px-6 py-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rules.map((rule) => (
                  <tr key={rule.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        {getSeverityBadge(rule.severity)}
                        <span className="text-xs text-slate-400 uppercase font-medium">
                          {rule.rule_type.replace('_', ' ')}
                        </span>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <span className="font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded text-xs border border-rose-100">
                        {rule.prohibited_term || rule.pattern}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      {rule.preferred_term ? (
                        <span className="font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded text-xs border border-emerald-100">
                          {rule.preferred_term}
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400 italic">None (Restrict only)</span>
                      )}
                    </td>

                    <td className="px-6 py-4 text-xs text-slate-600 max-w-sm">
                      {rule.explanation}
                    </td>

                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleDelete(rule.id)}
                        className="text-slate-400 hover:text-rose-600 p-1 rounded transition-colors"
                        title="Delete rule"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Rule Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Add Brand Rule</h3>
            <p className="text-xs text-slate-500">
              Deterministic rules are verified instantly before AI inference.
            </p>

            {error && (
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700">
                {error}
              </div>
            )}

            <form onSubmit={handleAddRule} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700">Rule Type</label>
                  <select
                    value={ruleType}
                    onChange={(e) => setRuleType(e.target.value)}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="terminology">Terminology</option>
                    <option value="restricted_phrase">Restricted Phrase</option>
                    <option value="tone">Tone Rule</option>
                    <option value="regex">Regex Pattern</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-700">Severity</label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value)}
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">Prohibited Term or Phrase</label>
                <input
                  type="text"
                  required
                  value={prohibitedTerm}
                  onChange={(e) => setProhibitedTerm(e.target.value)}
                  placeholder="e.g. 100% risk-free"
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">Preferred Term (Replacement)</label>
                <input
                  type="text"
                  value={preferredTerm}
                  onChange={(e) => setPreferredTerm(e.target.value)}
                  placeholder="e.g. rigorously risk-managed"
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">Reason / Governance Explanation</label>
                <textarea
                  required
                  rows={2}
                  value={explanation}
                  onChange={(e) => setExplanation(e.target.value)}
                  placeholder="Explain why this term violates brand standards or regulatory policy."
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
                  {saving ? 'Saving...' : 'Add Rule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
