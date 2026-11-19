import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Sparkles,
  FileText,
  ShieldCheck,
  BarChart3,
  BookOpen,
  Scroll,
  CheckCircle2,
  SpellCheck,
  Settings,
  HelpCircle
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { role } = useAuth();

  const navItems = [
    { section: 'Core Workspace' },
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/analysis', label: 'Content Analysis', icon: Sparkles },
    { to: '/submissions', label: 'Submissions History', icon: FileText },
    {
      to: '/reviews',
      label: 'Review Centre',
      icon: ShieldCheck,
      badge: role === 'reviewer' || role === 'admin' ? 'Reviewer' : undefined,
    },
    { to: '/analytics', label: 'Governance Analytics', icon: BarChart3 },

    { section: 'Brand Knowledge Base' },
    { to: '/knowledge', label: 'Knowledge Hub', icon: BookOpen },
    { to: '/guidelines', label: 'Brand Guidelines', icon: Scroll },
    { to: '/facts', label: 'Approved Facts', icon: CheckCircle2 },
    { to: '/rules', label: 'Rules & Terminology', icon: SpellCheck },

    { section: 'Administration' },
    { to: '/settings', label: 'Organisation Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between h-[calc(100vh-4rem)] sticky top-16 select-none">
      <div className="p-4 space-y-1 overflow-y-auto">
        {navItems.map((item, idx) => {
          if (item.section) {
            return (
              <p
                key={idx}
                className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-3 pt-4 pb-1"
              >
                {item.section}
              </p>
            );
          }

          const Icon = item.icon!;
          return (
            <NavLink
              key={item.to}
              to={item.to!}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-700 shadow-sm font-semibold'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`
              }
            >
              <div className="flex items-center space-x-3">
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-purple-100 text-purple-700">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </div>

      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center space-x-2 text-xs text-slate-500">
          <HelpCircle className="w-4 h-4 text-slate-400 shrink-0" />
          <span>Active AI: NVIDIA Nemotron</span>
        </div>
      </div>
    </aside>
  );
};
