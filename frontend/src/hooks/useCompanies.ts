import { useQuery } from '@tanstack/react-query';
import { companiesApi, type CompanyListParams } from '@/api/companies';

export function useCompanies(params?: CompanyListParams) {
  return useQuery({
    queryKey: ['companies', params],
    queryFn: () => companiesApi.list(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCompany(id: number | undefined) {
  return useQuery({
    queryKey: ['company', id],
    queryFn: () => companiesApi.get(id!),
    enabled: id !== undefined,
    staleTime: 10 * 60 * 1000,
  });
}

export function useCompanySearch(query: string) {
  return useQuery({
    queryKey: ['companySearch', query],
    queryFn: () => companiesApi.search(query),
    enabled: query.length >= 2,
    staleTime: 5 * 60 * 1000,
  });
}
