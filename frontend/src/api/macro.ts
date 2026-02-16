import apiClient from './client';
import type { MacroTimeSeries } from '@/types/macro';

export interface MacroFxParams {
  pairs?: string[];
  from_date?: string;
  to_date?: string;
}

export interface MacroRatesParams {
  from_date?: string;
  to_date?: string;
}

export const macroApi = {
  getFx(
    params?: MacroFxParams,
  ): Promise<Record<string, MacroTimeSeries>> {
    return apiClient.get('/macro/fx', { params }) as Promise<
      Record<string, MacroTimeSeries>
    >;
  },

  getRates(params?: MacroRatesParams): Promise<MacroTimeSeries> {
    return apiClient.get('/macro/rates', { params }) as Promise<MacroTimeSeries>;
  },

  getLatest(): Promise<Record<string, number>> {
    return apiClient.get('/macro/latest') as Promise<Record<string, number>>;
  },
};
