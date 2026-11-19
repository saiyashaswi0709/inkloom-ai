import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
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
