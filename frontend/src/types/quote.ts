export interface QuoteData {
  trade_date: string;
  open?: number;
  high?: number;
  low?: number;
  close: number;
  volume?: number;
  value?: number;
}

export interface QuoteTimeSeries {
  security_id: number;
  ticker: string;
  currency: string;
  quotes: QuoteData[];
  total: number;
}

export interface QuoteStats {
  security_id: number;
  ticker: string;
  last_price?: number;
  last_date?: string;
  high_52w?: number;
  low_52w?: number;
  avg_volume_30d?: number;
  return_1m?: number;
  return_3m?: number;
  return_ytd?: number;
  return_1y?: number;
  volatility_1y?: number;
}
