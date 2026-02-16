import apiClient from './client';
import type { PaginatedResponse } from '@/types/common';
import type { MultipleOut, MultipleScreenRow } from '@/types/multiple';

export interface MultiplesParams {
  from_date?: string;
  to_date?: string;
}

export interface MultiplesScreenParams {
  sector?: string;
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
  offset?: number;
  limit?: number;
}

export const multiplesApi = {
  getMultiples(
    companyId: number,
    params?: MultiplesParams,
  ): Promise<MultipleOut[]> {
    return apiClient.get(`/multiples/company/${companyId}`, {
      params,
    }) as Promise<MultipleOut[]>;
  },

  screen(
    params?: MultiplesScreenParams,
  ): Promise<PaginatedResponse<MultipleScreenRow>> {
    return apiClient.get('/multiples/screen', { params }) as Promise<
      PaginatedResponse<MultipleScreenRow>
    >;
  },
};
