import apiClient from './client';
import type { QuoteTimeSeries, QuoteStats } from '@/types/quote';

export interface QuoteParams {
  from_date?: string;
  to_date?: string;
  interval?: string;
}

export const quotesApi = {
  getQuotes(
    securityId: number,
    params?: QuoteParams,
  ): Promise<QuoteTimeSeries> {
    return apiClient.get(`/quotes/security/${securityId}`, {
      params,
    }) as Promise<QuoteTimeSeries>;
  },

  getStats(securityId: number): Promise<QuoteStats> {
    return apiClient.get(
      `/quotes/security/${securityId}/stats`,
    ) as Promise<QuoteStats>;
  },
};
