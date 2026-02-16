import apiClient from './client';
import type { PaginatedResponse } from '@/types/common';
import type { Company, CompanyCreate, CompanyDetail } from '@/types/company';

export interface CompanyListParams {
  search?: string;
  sector?: string;
  country?: string;
  offset?: number;
  limit?: number;
}

export const companiesApi = {
  list(params?: CompanyListParams): Promise<PaginatedResponse<Company>> {
    return apiClient.get('/companies', { params }) as Promise<
      PaginatedResponse<Company>
    >;
  },

  get(id: number): Promise<CompanyDetail> {
    return apiClient.get(`/companies/${id}`) as Promise<CompanyDetail>;
  },

  search(q: string, limit = 10): Promise<Company[]> {
    return apiClient.get('/companies/search', {
      params: { q, limit },
    }) as Promise<Company[]>;
  },

  create(data: CompanyCreate): Promise<Company> {
    return apiClient.post('/companies', data) as Promise<Company>;
  },

  update(id: number, data: Partial<CompanyCreate>): Promise<Company> {
    return apiClient.patch(`/companies/${id}`, data) as Promise<Company>;
  },
};
