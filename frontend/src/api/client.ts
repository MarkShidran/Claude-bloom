import axios, { AxiosError, AxiosResponse } from 'axios';
import { API_BASE_URL } from '@/config';

export interface ApiError {
  message: string;
  status: number;
  detail?: string;
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error: AxiosError<{ detail?: string }>) => {
    const apiError: ApiError = {
      message: error.message,
      status: error.response?.status ?? 0,
      detail: error.response?.data?.detail ?? error.message,
    };
    return Promise.reject(apiError);
  },
);

export default apiClient;
