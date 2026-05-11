import axios from 'axios';
import type { ApiResponse, AuthResponse, User } from '../types/API';
import type { Job, JobFilters, JobInput, Stats } from '../types/Job';

const API_BASE_URL = process.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';
const TOKEN_STORAGE_KEY = 'job_tracker_token';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function unwrap<T>(response: { data: ApiResponse<T> }): T {
  return response.data.data;
}

export const api = {
  setToken(token: string): void {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  },

  clearToken(): void {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  },

  getToken(): string | null {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  },

  async register(payload: { email: string; password: string; full_name?: string }): Promise<AuthResponse> {
    return unwrap(await client.post<ApiResponse<AuthResponse>>('/auth/register', payload));
  },

  async login(payload: { email: string; password: string }): Promise<AuthResponse> {
    return unwrap(await client.post<ApiResponse<AuthResponse>>('/auth/login', payload));
  },

  async getMe(): Promise<User> {
    return unwrap(await client.get<ApiResponse<User>>('/auth/me'));
  },

  async uploadJob(job: JobInput): Promise<Job> {
    return unwrap(await client.post<ApiResponse<Job>>('/jobs', job));
  },

  async getJobs(filters: JobFilters = {}): Promise<Job[]> {
    return unwrap(
      await client.get<ApiResponse<Job[]>>('/jobs', {
        params: {
          date_range: filters.date_range ?? 'all',
          status: filters.status || undefined,
        },
      }),
    );
  },

  async updateJob(id: string, job: Partial<JobInput>): Promise<Job> {
    return unwrap(await client.put<ApiResponse<Job>>(`/jobs/${id}`, job));
  },

  async deleteJob(id: string): Promise<void> {
    await client.delete(`/jobs/${id}`);
  },

  async getStats(dateRange = 'all'): Promise<Stats> {
    return unwrap(await client.get<ApiResponse<Stats>>('/stats', { params: { date_range: dateRange } }));
  },
};

export default api;
