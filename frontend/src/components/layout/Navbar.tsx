import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Shield, Sparkles, Building2, UserCircle, LogOut } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, organisation, role, logout } = useAuth();

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-sm">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-slate-900 text-lg tracking-tight">Inkloom AI</span>
            <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100">
              Enterprise
            </span>
          </div>
          <p className="text-xs text-slate-500 hidden sm:block">Intelligent Brand Governance Platform</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Active Organisation */}
        {organisation && (
          <div className="flex items-center space-x-2 px-3 py-1.5 bg-slate-100 rounded-md text-xs font-medium text-slate-700">
            <Building2 className="w-3.5 h-3.5 text-slate-500" />
            <span className="max-w-[150px] truncate">{organisation.name}</span>
          </div>
        )}

        {/* User & Role Badge */}
        <div className="flex items-center space-x-3 pl-2 border-l border-slate-200">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-slate-900 leading-tight">{user?.full_name}</p>
            <span
              className={`inline-block text-[11px] font-semibold px-2 py-0.2 rounded-full ${
                role === 'reviewer' || role === 'admin'
                  ? 'bg-purple-100 text-purple-700'
                  : 'bg-emerald-100 text-emerald-700'
              }`}
            >
              {role?.toUpperCase()}
            </span>
          </div>

          <button
            onClick={logout}
            className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
            title="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
