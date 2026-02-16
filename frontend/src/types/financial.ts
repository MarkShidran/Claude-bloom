export interface FinancialStatementBrief {
  id: number;
  standard: string;
  statement_type: string;
  period_type: string;
  period_end: string;
  currency: string;
}

export interface StatementItem {
  id: number;
  item_dict_id: number;
  code: string;
  name_ru: string;
  name_en?: string;
  value?: number;
  parent_code?: string;
  sort_order: number;
}

export interface FinancialStatement extends FinancialStatementBrief {
  items: StatementItem[];
}

export interface PeriodComparisonRow {
  code: string;
  name_ru: string;
  name_en?: string;
  parent_code?: string;
  sort_order: number;
  values: Record<string, number | null>;
  changes: Record<string, number | null>;
}

export interface PeriodComparison {
  company_id: number;
  standard: string;
  statement_type: string;
  periods: string[];
  rows: PeriodComparisonRow[];
}
