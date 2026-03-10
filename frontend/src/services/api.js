import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ─── Auth Services ─────────────────────────────────────
export const authService = {
  register: (data) => api.post('/register', data),
  login: (data) => api.post('/login', data),
};

// ─── Detection Services ────────────────────────────────
export const detectionService = {
  detectImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/detect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  liveDetect: (frameBase64) => {
    return api.post('/live-detect', { frame: frameBase64 });
  },

  detectMultiple: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/detect-multiple', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// ─── History Services ──────────────────────────────────
export const historyService = {
  getHistory: (page = 1, limit = 20, type = null) => {
    const params = { page, limit };
    if (type) params.detection_type = type;
    return api.get('/history', { params });
  },

  deleteItem: (id) => api.delete(`/history/${id}`),
  clearHistory: () => api.delete('/history'),
  getStats: () => api.get('/stats'),
};

export default api;
