import axios from 'axios';
import type { ApiResponse } from '../types/API';
import type { Job, JobFilters, JobInput, Stats } from '../types/Job';

const API_BASE_URL = process.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

function unwrap<T>(response: { data: ApiResponse<T> }): T {
  return response.data.data;
}

export const api = {
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
