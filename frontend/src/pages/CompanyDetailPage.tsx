import { useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import {
  Stack,
  Tabs,
  Alert,
  Select,
  Group,
  SegmentedControl,
  Chip,
} from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';
import { CompanyCard } from '@/components/companies/CompanyCard';
import { FinancialTable } from '@/components/financials/FinancialTable';
import { PeriodComparisonTable } from '@/components/financials/PeriodComparison';
import { QuoteChart } from '@/components/quotes/QuoteChart';
import { QuoteStatsDisplay } from '@/components/quotes/QuoteStats';
import { MultiplesTable } from '@/components/multiples/MultiplesTable';
import { MultiplesChart } from '@/components/multiples/MultiplesChart';
import { PeriodSelector } from '@/components/common/PeriodSelector';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { useCompany } from '@/hooks/useCompanies';
import { useQuotes, useQuoteStats } from '@/hooks/useQuotes';
import {
  useFinancialStatements,
  useFinancialItems,
  usePeriodComparison,
} from '@/hooks/useFinancials';
import { useMultiples } from '@/hooks/useMultiples';

const METRIC_OPTIONS = [
  { value: 'pe', label: 'P/E' },
  { value: 'ev_ebitda', label: 'EV/EBITDA' },
  { value: 'ev_sales', label: 'EV/Sales' },
  { value: 'pb', label: 'P/B' },
  { value: 'ps', label: 'P/S' },
  { value: 'roe', label: 'ROE' },
  { value: 'roa', label: 'ROA' },
  { value: 'debt_ebitda', label: 'Долг/EBITDA' },
];

export function CompanyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const companyId = id ? Number(id) : undefined;

  const { data: company, isLoading: companyLoading, error: companyError } =
    useCompany(companyId);

  // Financials state
  const [standard, setStandard] = useState('RSBU');
  const [periodType, setPeriodType] = useState('annual');
  const [selectedStatementId, setSelectedStatementId] = useState<
    number | undefined
  >();
  const [financialsView, setFinancialsView] = useState<'table' | 'comparison'>(
    'table',
  );

  // Quotes state
  const [selectedSecurityId, setSelectedSecurityId] = useState<
    number | undefined
  >();
  const [chartType, setChartType] = useState<'candlestick' | 'line'>(
    'candlestick',
  );

  // Multiples state
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([
    'pe',
    'ev_ebitda',
  ]);

  // Determine active security
  const activeSecurityId = selectedSecurityId ?? company?.securities[0]?.id;

  // Data hooks
  const { data: quotesData, isLoading: quotesLoading } =
    useQuotes(activeSecurityId);
  const { data: quoteStats } = useQuoteStats(activeSecurityId);

  const { data: statements } = useFinancialStatements(companyId, {
    standard,
    period_type: periodType,
  });
  const { data: statementDetail, isLoading: statementLoading } =
    useFinancialItems(selectedStatementId);

  const comparisonPeriods = useMemo(() => {
    if (!statements || statements.length < 2) return undefined;
    const sorted = [...statements].sort(
      (a, b) =>
        new Date(b.period_end).getTime() - new Date(a.period_end).getTime(),
    );
    return sorted.slice(0, 4).map((s) => s.period_end);
  }, [statements]);

  const { data: comparisonData, isLoading: comparisonLoading } =
    usePeriodComparison(
      comparisonPeriods && companyId
        ? {
            company_id: companyId,
            standard,
            statement_type:
              statements?.find((s) => s.standard === standard)
                ?.statement_type ?? 'balance_sheet',
            period_ends: comparisonPeriods,
          }
        : undefined,
    );

  const { data: multiples, isLoading: multiplesLoading } =
    useMultiples(companyId);

  // Statement selection
  const statementOptions = useMemo(
    () =>
      (statements ?? []).map((s) => ({
        value: String(s.id),
        label: `${s.statement_type} — ${s.period_end} (${s.standard})`,
      })),
    [statements],
  );

  // Security selection
  const securityOptions = useMemo(
    () =>
      (company?.securities ?? []).map((s) => ({
        value: String(s.id),
        label: `${s.ticker} (${s.security_type} / ${s.exchange})`,
      })),
    [company],
  );

  if (companyLoading) return <LoadingSpinner />;

  if (companyError || !company) {
    return (
      <Alert icon={<IconAlertCircle size={16} />} color="red" title="Ошибка">
        Не удалось загрузить данные компании.
      </Alert>
    );
  }

  const handleMetricToggle = (metric: string) => {
    setSelectedMetrics((prev) =>
      prev.includes(metric)
        ? prev.filter((m) => m !== metric)
        : [...prev, metric],
    );
  };

  return (
    <Stack gap="lg">
      <CompanyCard company={company} />

      <Tabs defaultValue="overview">
        <Tabs.List>
          <Tabs.Tab value="overview">Обзор</Tabs.Tab>
          <Tabs.Tab value="financials">Отчётность</Tabs.Tab>
          <Tabs.Tab value="quotes">Котировки</Tabs.Tab>
          <Tabs.Tab value="multiples">Мультипликаторы</Tabs.Tab>
        </Tabs.List>

        {/* Overview Tab */}
        <Tabs.Panel value="overview" pt="md">
          <Stack gap="md">
            {quoteStats && <QuoteStatsDisplay stats={quoteStats} />}
            {quotesData && (
              <QuoteChart data={quotesData} chartType="line" />
            )}
          </Stack>
        </Tabs.Panel>

        {/* Financials Tab */}
        <Tabs.Panel value="financials" pt="md">
          <Stack gap="md">
            <Group justify="space-between">
              <PeriodSelector
                standard={standard}
                periodType={periodType}
                onStandardChange={setStandard}
                onPeriodTypeChange={setPeriodType}
              />
              <SegmentedControl
                value={financialsView}
                onChange={(val) =>
                  setFinancialsView(val as 'table' | 'comparison')
                }
                data={[
                  { label: 'Отчёт', value: 'table' },
                  { label: 'Сравнение периодов', value: 'comparison' },
                ]}
              />
            </Group>

            {financialsView === 'table' ? (
              <>
                <Select
                  placeholder="Выберите отчёт..."
                  data={statementOptions}
                  value={
                    selectedStatementId
                      ? String(selectedStatementId)
                      : null
                  }
                  onChange={(val) =>
                    setSelectedStatementId(val ? Number(val) : undefined)
                  }
                  clearable
                  w={500}
                />
                <FinancialTable
                  statement={statementDetail}
                  loading={statementLoading}
                />
              </>
            ) : (
              <PeriodComparisonTable
                comparison={comparisonData}
                loading={comparisonLoading}
              />
            )}
          </Stack>
        </Tabs.Panel>

        {/* Quotes Tab */}
        <Tabs.Panel value="quotes" pt="md">
          <Stack gap="md">
            <Group>
              {securityOptions.length > 1 && (
                <Select
                  placeholder="Ценная бумага"
                  data={securityOptions}
                  value={
                    activeSecurityId ? String(activeSecurityId) : null
                  }
                  onChange={(val) =>
                    setSelectedSecurityId(val ? Number(val) : undefined)
                  }
                  w={300}
                />
              )}
              <SegmentedControl
                value={chartType}
                onChange={(val) =>
                  setChartType(val as 'candlestick' | 'line')
                }
                data={[
                  { label: 'Свечи', value: 'candlestick' },
                  { label: 'Линия', value: 'line' },
                ]}
              />
            </Group>

            {quoteStats && <QuoteStatsDisplay stats={quoteStats} />}

            <QuoteChart
              data={quotesLoading ? undefined : quotesData}
              chartType={chartType}
            />
          </Stack>
        </Tabs.Panel>

        {/* Multiples Tab */}
        <Tabs.Panel value="multiples" pt="md">
          <Stack gap="md">
            <Group gap="xs">
              {METRIC_OPTIONS.map((opt) => (
                <Chip
                  key={opt.value}
                  checked={selectedMetrics.includes(opt.value)}
                  onChange={() => handleMetricToggle(opt.value)}
                  variant="filled"
                >
                  {opt.label}
                </Chip>
              ))}
            </Group>

            <MultiplesChart
              multiples={multiples}
              selectedMetrics={selectedMetrics}
            />

            <MultiplesTable
              multiples={multiples}
              loading={multiplesLoading}
            />
          </Stack>
        </Tabs.Panel>
      </Tabs>
    </Stack>
  );
}
