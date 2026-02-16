export interface MultipleOut {
  id: number;
  company_id: number;
  calc_date: string;
  period_end: string;
  pe?: number;
  ev_ebitda?: number;
  ev_sales?: number;
  pb?: number;
  ps?: number;
  roe?: number;
  roa?: number;
  debt_ebitda?: number;
  dividend_yield?: number;
  market_cap?: number;
  enterprise_value?: number;
  currency?: string;
}

export interface MultipleScreenRow {
  company_id: number;
  company_name: string;
  ticker?: string;
  sector?: string;
  calc_date: string;
  pe?: number;
  ev_ebitda?: number;
  ev_sales?: number;
  pb?: number;
  ps?: number;
  roe?: number;
  roa?: number;
  debt_ebitda?: number;
  market_cap?: number;
}
