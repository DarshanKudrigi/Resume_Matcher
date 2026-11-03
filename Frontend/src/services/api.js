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
  signup: (payload) =>
    request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getMe: () => request('/auth/me'),
  logout: () => {
    localStorage.removeItem('resumemate_token');
  },

  // Users
  updateProfile: (payload) =>
    request('/users/me', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  // Resumes
  getResumes: () => request('/resumes'),
  getResume: (id) => request(`/resumes/${id}`),
  createResume: (payload) =>
    request('/resumes', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateResume: (id, payload) =>
    request(`/resumes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
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
  getUploadedFile: (id) => request(`/resumes/files/${id}`),
  getUploadedFiles: () => request('/resumes/files'),

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

  // Dashboard
  getDashboardStats: () => request('/dashboard/stats'),

  // Recommendations
  searchJobRecommendations: (payload) =>
    request('/recommendations/search', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  streamJobRecommendations: async (payload, onEvent, onError) => {
    try {
      const res = await fetch(`${API_BASE}/recommendations/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(),
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || 'Streaming failed');
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop(); // keep trailing partial line
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            try {
              const data = JSON.parse(trimmed.slice(6));
              if (onEvent) onEvent(data);
            } catch (parseErr) {
              console.warn('SSE parse error:', parseErr);
            }
          }
        }
      }
    } catch (e) {
      if (onError) onError(e);
      else throw e;
    }
  },

  // Chat
  sendChatMessage: (payload) =>
    request('/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getAISuggestions: (role = 'Frontend Developer') =>
    request(`/chat/suggestions?role=${encodeURIComponent(role)}`),
};
