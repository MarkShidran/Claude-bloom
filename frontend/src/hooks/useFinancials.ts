import { useQuery } from '@tanstack/react-query';
import {
  financialsApi,
  type FinancialStatementsParams,
  type PeriodComparisonParams,
} from '@/api/financials';

export function useFinancialStatements(
  companyId: number | undefined,
  params?: FinancialStatementsParams,
) {
  return useQuery({
    queryKey: ['financialStatements', companyId, params],
    queryFn: () => financialsApi.getStatements(companyId!, params),
    enabled: companyId !== undefined,
    staleTime: 5 * 60 * 1000,
  });
}

export function useFinancialItems(statementId: number | undefined) {
  return useQuery({
    queryKey: ['financialItems', statementId],
    queryFn: () => financialsApi.getStatementItems(statementId!),
    enabled: !!statementId,
    staleTime: 10 * 60 * 1000,
  });
}

export function usePeriodComparison(
  params: PeriodComparisonParams | undefined,
) {
  return useQuery({
    queryKey: ['periodComparison', params],
    queryFn: () => financialsApi.compare(params!),
    enabled:
      !!params &&
      !!params.company_id &&
      params.period_ends.length > 0,
    staleTime: 10 * 60 * 1000,
  });
}
