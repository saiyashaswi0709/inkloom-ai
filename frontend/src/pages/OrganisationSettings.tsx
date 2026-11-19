import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Building2, Users, Plus, Shield, Cpu, CheckCircle2, AlertCircle } from 'lucide-react';

export const OrganisationSettings: React.FC = () => {
  const { organisation, user } = useAuth();
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // Add member form
  const [memberEmail, setMemberEmail] = useState('');
  const [memberRole, setMemberRole] = useState('creator');
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // AI Engine health
  const [aiStatus, setAiStatus] = useState<any | null>(null);

  const fetchSettings = async () => {
    try {
      const [membersRes, aiRes] = await Promise.all([
        api.get('/organisations/members'),
        api.get('/auth/validate-ai'),
      ]);
      setMembers(membersRes.data);
      setAiStatus(aiRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    setAdding(true);
    setError(null);
    try {
      await api.post('/organisations/members', {
        email: memberEmail,
        role: memberRole,
      });
      setShowAddModal(false);
      setMemberEmail('');
      fetchSettings();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add member');
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Organisation Settings</h1>
        <p className="text-sm text-slate-500 mt-1">
          Manage workspace members, role permissions, and active governance integrations.
        </p>
      </div>

      {/* Organisation Profile Card */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 text-base">{organisation?.name}</h3>
            <p className="text-xs text-slate-400">Slug: {organisation?.slug}</p>
          </div>
        </div>
        {organisation?.description && (
          <p className="text-xs text-slate-600">{organisation.description}</p>
        )}
      </div>

      {/* AI Intelligence Engine Status */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center text-purple-600">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-sm">AI Engine Architecture</h3>
              <p className="text-xs text-slate-400">NVIDIA Nemotron via OpenRouter & Deterministic Engine</p>
            </div>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              aiStatus?.configured
                ? 'bg-emerald-100 text-emerald-800'
                : 'bg-amber-100 text-amber-800'
            }`}
          >
            {aiStatus?.configured ? 'Nemotron Active' : 'Deterministic Fallback Active'}
          </span>
        </div>

        <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-700 space-y-1.5">
          <p>
            <strong>Configured Model:</strong> {aiStatus?.model || 'nvidia/llama-3.1-nemotron-70b-instruct'}
          </p>
          <p>
            <strong>Operational Status:</strong> {aiStatus?.status || 'Active'}
          </p>
          <p className="text-slate-500 italic">
            Note: All API credentials remain protected inside backend environment variables and are never transmitted to client browsers.
          </p>
        </div>
      </div>

      {/* Members Management */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4 text-slate-600" />
            <h3 className="font-semibold text-slate-900 text-sm">Team Members & Governance Roles</h3>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Member</span>
          </button>
        </div>

        <div className="divide-y divide-slate-100">
          {members.map((m) => (
            <div key={m.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
              <div>
                <p className="text-sm font-medium text-slate-900">{m.user?.full_name}</p>
                <p className="text-xs text-slate-500">{m.user?.email}</p>
              </div>
              <span
                className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold uppercase ${
                  m.role === 'reviewer' || m.role === 'admin'
                    ? 'bg-purple-100 text-purple-700'
                    : 'bg-emerald-100 text-emerald-700'
                }`}
              >
                {m.role}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Add Member Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Add Workspace Member</h3>
            <p className="text-xs text-slate-500">
              Assign Reviewer authority to allow final publication sign-offs.
            </p>

            {error && (
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700">
                {error}
              </div>
            )}

            <form onSubmit={handleAddMember} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700">Member Email</label>
                <input
                  type="email"
                  required
                  value={memberEmail}
                  onChange={(e) => setMemberEmail(e.target.value)}
                  placeholder="colleague@organisation.com"
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">Role Authority</label>
                <select
                  value={memberRole}
                  onChange={(e) => setMemberRole(e.target.value)}
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                >
                  <option value="creator">Creator (Drafts & submits content)</option>
                  <option value="reviewer">Reviewer (Signs off & approves publication)</option>
                  <option value="admin">Admin (Full administrative authority)</option>
                </select>
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
                  disabled={adding}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold"
                >
                  {adding ? 'Adding...' : 'Add Member'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
