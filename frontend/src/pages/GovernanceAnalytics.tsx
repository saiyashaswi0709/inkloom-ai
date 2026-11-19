import React, { useState, useEffect } from 'react';
import api from '../api/client';
import {
  BarChart3,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  Shield,
  Activity,
  CheckCircle2
} from 'lucide-react';
import { formatDateTimeIST } from '../utils/date';

export const GovernanceAnalytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await api.get('/analytics/summary');
        setAnalytics(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return <div className="p-12 text-center text-slate-400 text-sm">Loading governance intelligence...</div>;
  }

  if (!analytics) {
    return <div className="p-12 text-center text-slate-500">Analytics data unavailable.</div>;
  }

  const categoryEntries = Object.entries(analytics.violations_by_category || {});
  const totalCategoryViolations = categoryEntries.reduce((acc, [, v]: any) => acc + v, 0) || 1;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Governance Intelligence & Analytics</h1>
        <p className="text-sm text-slate-500 mt-1">
          Deep behavioral insights, recurring violation trends, and data-backed compliance recommendations.
        </p>
      </div>

      {/* Actionable Recommendations Based on Stored Data */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-xl border border-indigo-100 space-y-4">
        <div className="flex items-center space-x-2 text-indigo-950 font-semibold text-sm">
          <Lightbulb className="w-5 h-5 text-indigo-600" />
          <span>Actionable Governance Recommendations</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {analytics.actionable_recommendations?.map((rec: string, idx: number) => (
            <div key={idx} className="p-3.5 bg-white/90 rounded-lg border border-indigo-100 text-xs text-slate-700 flex items-start space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>{rec}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Grid: Violations by Category & Top Recurring Terms */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900 text-sm">Violations By Classification</h3>
            <span className="text-xs text-slate-400">Category Share</span>
          </div>

          <div className="space-y-4">
            {categoryEntries.map(([cat, count]: any) => {
              const pct = Math.round((count / totalCategoryViolations) * 100);
              return (
                <div key={cat} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-slate-700 uppercase tracking-wide">
                      {cat.replace('_', ' ')}
                    </span>
                    <span className="font-semibold text-slate-900">
                      {count} ({pct}%)
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                    <div
                      className="h-full bg-indigo-600 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Recurring Prohibited Terms */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900 text-sm">Top Recurring Prohibited Phrases</h3>
            <span className="text-xs text-slate-400">Frequency Count</span>
          </div>

          {analytics.top_recurring_prohibited_terms?.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-xs">No recurring terms recorded.</div>
          ) : (
            <div className="divide-y divide-slate-100">
              {analytics.top_recurring_prohibited_terms.map((item: any, idx: number) => (
                <div key={idx} className="py-3 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-[10px] font-bold">
                      {idx + 1}
                    </span>
                    <span className="text-xs font-semibold text-rose-800 bg-rose-50 px-2 py-0.5 rounded border border-rose-100">
                      "{item.term}"
                    </span>
                  </div>
                  <span className="text-xs font-semibold text-slate-700">
                    {item.occurrences} {item.occurrences === 1 ? 'occurrence' : 'occurrences'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Audit Log Activity Stream */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-slate-900 text-sm flex items-center space-x-2">
            <Activity className="w-4 h-4 text-slate-500" />
            <span>Governance Audit Trail</span>
          </h3>
          <span className="text-xs text-slate-400">Immutable Record</span>
        </div>

        <div className="divide-y divide-slate-100">
          {analytics.recent_activity?.map((log: any) => (
            <div key={log.id} className="py-2.5 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-3">
                <span className="font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">
                  {log.action}
                </span>
                <span className="text-slate-600">Resource: {log.resource_type}</span>
              </div>
              <span className="text-slate-400">{formatDateTimeIST(log.created_at)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
