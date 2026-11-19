import axios from 'axios';

// In production on Vercel, default to the deployed Render backend if VITE_API_URL is unset
const DEFAULT_PROD_API_URL = 'https://inkloom-ai-haqr.onrender.com';
const envBaseUrl = (import.meta.env.VITE_API_URL || '').trim().replace(/\/+$/, '');
const rawBaseUrl = envBaseUrl || (import.meta.env.PROD ? DEFAULT_PROD_API_URL : '/api/v1');

// Ensure base URL always points to /api/v1 without trailing slashes or duplication
export const API_BASE_URL = (() => {
  if (!rawBaseUrl || rawBaseUrl === '/api/v1') {
    return '/api/v1';
  }
  if (rawBaseUrl.endsWith('/api/v1')) {
    return rawBaseUrl;
  }
  return `${rawBaseUrl}/api/v1`;
})();

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  // Ensure baseURL ends with /api/v1
  if (config.baseURL && !config.baseURL.endsWith('/api/v1')) {
    config.baseURL = `${config.baseURL.replace(/\/+$/, '')}/api/v1`;
  }

  // Ensure config.url does not duplicate /api/v1 prefix
  if (config.url && config.url.startsWith('/api/v1')) {
    config.url = config.url.replace(/^\/api\/v1/, '') || '/';
  }

  // Ensure config.url starts with /
  if (config.url && !config.url.startsWith('/')) {
    config.url = `/${config.url}`;
  }

  const token = localStorage.getItem('inkloom_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  const org = localStorage.getItem('inkloom_org');
  if (org) {
    try {
      const parsedOrg = JSON.parse(org);
      if (parsedOrg?.id) {
        config.headers['X-Organisation-Id'] = parsedOrg.id;
      }
    } catch {
      // Ignore JSON parse errors
    }
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('inkloom_token');
      localStorage.removeItem('inkloom_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
