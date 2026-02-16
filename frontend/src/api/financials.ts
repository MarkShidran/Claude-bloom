import apiClient from './client';
import type {
  FinancialStatementBrief,
  FinancialStatement,
  PeriodComparison,
} from '@/types/financial';

export interface FinancialStatementsParams {
  standard?: string;
  statement_type?: string;
  period_type?: string;
}

export interface PeriodComparisonParams {
  company_id: number;
  standard: string;
  statement_type: string;
  period_ends: string[];
}

export const financialsApi = {
  getStatements(
    companyId: number,
    params?: FinancialStatementsParams,
  ): Promise<FinancialStatementBrief[]> {
    return apiClient.get(`/financials/company/${companyId}/statements`, {
      params,
    }) as Promise<FinancialStatementBrief[]>;
  },

  getStatementItems(statementId: number): Promise<FinancialStatement> {
    return apiClient.get(
      `/financials/statements/${statementId}`,
    ) as Promise<FinancialStatement>;
  },

  compare(params: PeriodComparisonParams): Promise<PeriodComparison> {
    return apiClient.post(
      '/financials/compare',
      params,
    ) as Promise<PeriodComparison>;
  },

  upload(companyId: number, file: File): Promise<{ message: string }> {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post(
      `/financials/company/${companyId}/upload`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      },
    ) as Promise<{ message: string }>;
  },
};
