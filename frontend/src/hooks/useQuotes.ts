import { useQuery } from '@tanstack/react-query';
import { quotesApi, type QuoteParams } from '@/api/quotes';

export function useQuotes(
  securityId: number | undefined,
  params?: QuoteParams,
) {
  return useQuery({
    queryKey: ['quotes', securityId, params],
    queryFn: () => quotesApi.getQuotes(securityId!, params),
    enabled: securityId !== undefined,
    staleTime: 5 * 60 * 1000,
  });
}

export function useQuoteStats(securityId: number | undefined) {
  return useQuery({
    queryKey: ['quoteStats', securityId],
    queryFn: () => quotesApi.getStats(securityId!),
    enabled: securityId !== undefined,
    staleTime: 10 * 60 * 1000,
  });
}
