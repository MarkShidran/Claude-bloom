import { useMemo } from 'react';
import dayjs from 'dayjs';
import type { ColDef, CellClassParams } from 'ag-grid-community';
import { DataGrid, formatFinancialNumber } from '@/components/common/DataGrid';
import type {
  PeriodComparison as PeriodComparisonType,
  PeriodComparisonRow,
} from '@/types/financial';

interface PeriodComparisonProps {
  comparison: PeriodComparisonType | undefined;
  loading?: boolean;
}

function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  return `${(value * 100).toLocaleString('ru-RU', { maximumFractionDigits: 1 })}%`;
}

function changeColor(value: number | null | undefined): string | undefined {
  if (value === null || value === undefined) return undefined;
  if (value > 0) return '#2b8a3e';
  if (value < 0) return '#c92a2a';
  return undefined;
}

export function PeriodComparisonTable({
  comparison,
  loading,
}: PeriodComparisonProps) {
  const columnDefs = useMemo<ColDef<PeriodComparisonRow>[]>(() => {
    if (!comparison) return [];

    const baseCols: ColDef<PeriodComparisonRow>[] = [
      {
        field: 'name_ru',
        headerName: 'Показатель',
        pinned: 'left',
        flex: 2,
        minWidth: 250,
        cellStyle: (params: CellClassParams<PeriodComparisonRow>) => ({
          fontWeight: params.data?.parent_code ? 'normal' : 'bold',
        }),
      },
    ];

    const periodCols: ColDef<PeriodComparisonRow>[] = comparison.periods.map(
      (period) => ({
        headerName: dayjs(period).format('DD.MM.YYYY'),
        valueGetter: (params) =>
          params.data?.values[period] ?? null,
        valueFormatter: (params) => formatFinancialNumber(params.value),
        type: 'numericColumn',
        minWidth: 140,
      }),
    );

    const changeCols: ColDef<PeriodComparisonRow>[] =
      comparison.periods.length > 1
        ? comparison.periods.slice(1).map((period) => ({
            headerName: `Изм. ${dayjs(period).format('DD.MM.YYYY')}`,
            valueGetter: (params) =>
              params.data?.changes[period] ?? null,
            valueFormatter: (params) => formatPercent(params.value),
            type: 'numericColumn',
            minWidth: 130,
            cellStyle: (params: CellClassParams<PeriodComparisonRow>) => ({
              color: changeColor(params.value as number | null),
            }),
          }))
        : [];

    return [...baseCols, ...periodCols, ...changeCols];
  }, [comparison]);

  return (
    <DataGrid<PeriodComparisonRow>
      columnDefs={columnDefs}
      rowData={comparison?.rows}
      loading={loading}
      height={700}
    />
  );
}
