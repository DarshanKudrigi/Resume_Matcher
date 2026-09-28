// Frontend API client for ResumeMate FastAPI backend

const API_BASE = '/api';

function getAuthHeader() {
  const token = localStorage.getItem('resumemate_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...options.headers,
  };

  // If body is FormData, don't set Content-Type
  if (options.body instanceof FormData) {
    delete headers['Content-Type'];
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'API request failed');
    }

    return await res.json();
  } catch (error) {
    console.warn(`[API] Error on ${endpoint}:`, error.message);
    throw error;
  }
}

export const api = {
  // Health
  checkHealth: () => request('/health'),

  // Auth
  login: async (email, password) => {
    const data = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (data?.access_token) {
      localStorage.setItem('resumemate_token', data.access_token);
    }
    return data;
  },

  register: async (userData) => {
    const data = await request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    if (data?.access_token) {
      localStorage.setItem('resumemate_token', data.access_token);
    }
    return data;
  },

  getMe: () => request('/auth/me'),

  updateProfile: (profileData) =>
    request('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    }),

  // Resumes
  getResumes: () => request('/resumes'),
  getResume: (id) => request(`/resumes/${id}`),
  createResume: (resumeData) =>
    request('/resumes', {
      method: 'POST',
      body: JSON.stringify(resumeData),
    }),
  updateResume: (id, resumeData) =>
    request(`/resumes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(resumeData),
    }),
  deleteResume: (id) =>
    request(`/resumes/${id}`, {
      method: 'DELETE',
    }),
  duplicateResume: (id) =>
    request(`/resumes/${id}/duplicate`, {
      method: 'POST',
    }),

  uploadResumeFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/resumes/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // Jobs
  getJobs: () => request('/jobs'),
  parseJob: (payload) =>
    request('/jobs/parse', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Analysis
  analyze: (payload) =>
    request('/analyze', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // History
  getHistory: () => request('/history'),
  getHistoryItem: (id) => request(`/history/${id}`),
  deleteHistoryItem: (id) =>
    request(`/history/${id}`, {
      method: 'DELETE',
    }),

  // Dashboard
  getDashboardStats: () => request('/dashboard/stats'),

  // Chat
  sendChatMessage: (payload) =>
    request('/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getAISuggestions: (role = 'Frontend Developer') =>
    request(`/chat/suggestions?role=${encodeURIComponent(role)}`),
};
