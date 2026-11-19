import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface Organisation {
  id: string;
  name: string;
  slug: string;
  description?: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  organisation: Organisation | null;
  role: string | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  demoLogin: (role: 'reviewer' | 'creator') => Promise<void>;
  register: (email: string, password: string, fullName: string, orgName?: string) => Promise<void>;
  logout: () => void;
  setOrganisation: (org: Organisation) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [organisation, setOrganisationState] = useState<Organisation | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('inkloom_token');
    const savedUser = localStorage.getItem('inkloom_user');
    const savedOrg = localStorage.getItem('inkloom_org');
    const savedRole = localStorage.getItem('inkloom_role');

    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
        if (savedOrg) setOrganisationState(JSON.parse(savedOrg));
        if (savedRole) setRole(savedRole);
      } catch {
        localStorage.clear();
      }
    }
    setLoading(false);
  }, []);

  const handleAuthSuccess = (data: any) => {
    setToken(data.access_token);
    setUser(data.user);
    setOrganisationState(data.organisation || null);
    setRole(data.role || 'creator');

    localStorage.setItem('inkloom_token', data.access_token);
    localStorage.setItem('inkloom_user', JSON.stringify(data.user));
    if (data.organisation) {
      localStorage.setItem('inkloom_org', JSON.stringify(data.organisation));
    }
    if (data.role) {
      localStorage.setItem('inkloom_role', data.role);
    }
  };

  const login = async (email: string, password: string) => {
    const res = await api.post('/auth/login', { email, password });
    handleAuthSuccess(res.data);
  };

  const demoLogin = async (role: 'reviewer' | 'creator') => {
    const res = await api.post('/auth/demo-login', { role });
    handleAuthSuccess(res.data);
  };

  const register = async (email: string, password: string, fullName: string, orgName?: string) => {
    const res = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
      organisation_name: orgName,
    });
    handleAuthSuccess(res.data);
  };

  const logout = () => {
    setUser(null);
    setOrganisationState(null);
    setRole(null);
    setToken(null);
    localStorage.removeItem('inkloom_token');
    localStorage.removeItem('inkloom_user');
    localStorage.removeItem('inkloom_org');
    localStorage.removeItem('inkloom_role');
  };

  const setOrganisation = (org: Organisation) => {
    setOrganisationState(org);
    localStorage.setItem('inkloom_org', JSON.stringify(org));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        organisation,
        role,
        token,
        isAuthenticated: !!token && !!user,
        loading,
        login,
        demoLogin,
        register,
        logout,
        setOrganisation,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
