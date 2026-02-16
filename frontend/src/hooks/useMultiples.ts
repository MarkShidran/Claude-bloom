import { useQuery } from '@tanstack/react-query';
import {
  multiplesApi,
  type MultiplesParams,
  type MultiplesScreenParams,
} from '@/api/multiples';

export function useMultiples(
  companyId: number | undefined,
  params?: MultiplesParams,
) {
  return useQuery({
    queryKey: ['multiples', companyId, params],
    queryFn: () => multiplesApi.getMultiples(companyId!, params),
    enabled: companyId !== undefined,
    staleTime: 5 * 60 * 1000,
  });
}

export function useMultiplesScreen(params?: MultiplesScreenParams) {
  return useQuery({
    queryKey: ['multiplesScreen', params],
    queryFn: () => multiplesApi.screen(params),
    staleTime: 5 * 60 * 1000,
  });
}
