import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
  updateProfile: (userData) => api.put('/auth/me', userData),
};

// Website API calls
export const websiteAPI = {
  getWebsites: (params = {}) => api.get('/websites', { params }),
  getWebsite: (id) => api.get(`/websites/${id}`),
  createWebsite: (data) => api.post('/websites', data),
  updateWebsite: (id, data) => api.put(`/websites/${id}`, data),
  deleteWebsite: (id) => api.delete(`/websites/${id}`),
  generateWebsite: (data) => api.post('/generate/website', null, { params: data }),
  exportWebsite: (id) => api.get(`/websites/${id}/export`, { 
    responseType: 'blob',
    timeout: 30000 // 30 seconds for export
  }),
  
  // Hosting endpoints (Phase 1)
  deployWebsite: (id, customSubdomain = null) => api.post(`/websites/${id}/deploy`, null, { 
    params: customSubdomain ? { custom_subdomain: customSubdomain } : {} 
  }),
  undeployWebsite: (id) => api.delete(`/websites/${id}/undeploy`),
  redeployWebsite: (id) => api.put(`/websites/${id}/redeploy`),
  configureSSL: (id) => api.post(`/websites/${id}/ssl`),
};

// Hosting API calls
export const hostingAPI = {
  getHostedSites: () => api.get('/hosting/sites'),
};

// Template API calls
export const templateAPI = {
  getTemplates: (params = {}) => api.get('/templates', { params }),
  getTemplate: (id) => api.get(`/templates/${id}`),
};

// Health check
export const healthCheck = () => api.get('/health');

export default api;