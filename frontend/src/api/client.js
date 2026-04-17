import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token from localStorage on init
const token = localStorage.getItem('token');
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired - redirect to login
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (data) => api.post('/api/auth/login', data),
  register: (data) => api.post('/api/auth/register', data),
  me: () => api.get('/api/auth/me'),
};

// Candidates API
export const candidatesAPI = {
  create: (data) => api.post('/api/candidates/', data),
  getAll: (params) => api.get('/api/candidates/', { params }),
  getById: (id) => api.get(`/api/candidates/${id}`),
  update: (id, data) => api.put(`/api/candidates/${id}`, data),
  delete: (id) => api.delete(`/api/candidates/${id}`),
};

// Employees API
export const employeesAPI = {
  create: (data) => api.post('/api/employees/', data),
  getAll: () => api.get('/api/employees/'),
};

// Departments API
export const departmentsAPI = {
  getAll: () => api.get('/api/departments/'),
  create: (data) => api.post('/api/departments/', data),
  update: (id, data) => api.put(`/api/departments/${id}`, data),
  delete: (id) => api.delete(`/api/departments/${id}`),
};

// Payroll API
export const payrollAPI = {
  getAll: (month) => api.get('/api/payroll/', { params: { month } }),
  generate: (data) => api.post('/api/payroll/generate', data),
  sendPayslips: (month) => api.post(`/api/payroll/send-payslips?month=${month}`),
};

// Interviews API
export const interviewsAPI = {
  create: (data) => api.post('/api/interviews/', data),
  getAll: (params) => api.get('/api/interviews/', { params }),
  update: (id, data) => api.put(`/api/interviews/${id}`, data),
  createFeedback: (data) => api.post('/api/interviews/feedback', data),
  getFeedback: (candidateId) => api.get(`/api/interviews/feedback/${candidateId}`),
};

// Job Postings API
export const jobPostingsAPI = {
  create: (data) => api.post('/api/job-postings/', data),
  getAll: (params) => api.get('/api/job-postings/', { params }),
  getById: (id) => api.get(`/api/job-postings/${id}`),
  update: (id, data) => api.put(`/api/job-postings/${id}`, data),
  delete: (id) => api.delete(`/api/job-postings/${id}`),
  generateDescription: (title, department) => api.post(`/api/job-postings/generate-description?title=${encodeURIComponent(title)}&department=${encodeURIComponent(department || '')}`),
};

// Analytics API
export const analyticsAPI = {
  getDashboard: () => api.get('/api/analytics/dashboard'),
  getPipeline: () => api.get('/api/analytics/pipeline'),
  getActivity: (limit) => api.get('/api/analytics/activity', { params: { limit } }),
  getHiringFunnel: () => api.get('/api/analytics/hiring-funnel'),
};

// Templates API
export const templatesAPI = {
  create: (data) => api.post('/api/templates/', data),
  getAll: (params) => api.get('/api/templates/', { params }),
  getById: (id) => api.get(`/api/templates/${id}`),
  update: (id, data) => api.put(`/api/templates/${id}`, data),
  delete: (id) => api.delete(`/api/templates/${id}`),
};

// Notes API
export const notesAPI = {
  create: (data) => api.post('/api/notes/', data),
  getByCandidate: (candidateId) => api.get(`/api/notes/${candidateId}`),
  delete: (id) => api.delete(`/api/notes/${id}`),
};

// Candidate Actions API
export const actionsAPI = {
  approve: (candidateId) => api.post('/api/actions/approve', { candidate_id: candidateId }),
  reject: (candidateId) => api.post('/api/actions/reject', { candidate_id: candidateId }),
  requestInterview: (data) => api.post('/api/actions/request-interview', data),
  sendOffer: (data) => api.post('/api/actions/send-offer', data),
  markHired: (candidateId) => api.post('/api/actions/mark-hired', { candidate_id: candidateId }),
};

// AI API
export const aiAPI = {
  screenCandidate: (data) => api.post('/api/ai/screen-candidate', data),
  generateEmail: (data) => api.post('/api/ai/generate-email', data),
  suggestQuestions: (jobRole, cvSummary) => api.post(`/api/ai/suggest-questions?job_role=${jobRole}&cv_summary=${cvSummary || ''}`),
  analyzeSentiment: (data) => api.post('/api/ai/analyze-sentiment', data),
};

// Public API (no auth)
export const publicAPI = {
  getCareers: (params) => api.get('/public/careers', { params }),
  getJob: (id) => api.get(`/public/careers/${id}`),
  applyToJob: (jobId, data) => api.post(`/public/careers/${jobId}/apply`, data),
};

// Email Inbox API
export const emailsAPI = {
  getInbox: () => api.get('/api/emails/inbox'),
  getThread: (candidateId) => api.get(`/api/emails/thread/${candidateId}`),
  reply: (data) => api.post('/api/emails/reply', data),
};
