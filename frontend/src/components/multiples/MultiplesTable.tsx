import { useMemo } from 'react';
import dayjs from 'dayjs';
import type { ColDef } from 'ag-grid-community';
import { DataGrid, formatFinancialNumber } from '@/components/common/DataGrid';
import type { MultipleOut } from '@/types/multiple';

interface MultiplesTableProps {
  multiples: MultipleOut[] | undefined;
  loading?: boolean;
}

export function MultiplesTable({ multiples, loading }: MultiplesTableProps) {
  const columnDefs = useMemo<ColDef<MultipleOut>[]>(
    () => [
      {
        field: 'calc_date',
        headerName: 'Дата расчёта',
        width: 130,
        valueFormatter: (params) =>
          params.value ? dayjs(params.value).format('DD.MM.YYYY') : '—',
      },
      {
        field: 'pe',
        headerName: 'P/E',
        type: 'numericColumn',
        width: 100,
        valueFormatter: (params) => formatFinancialNumber(params.value),
      },
      {
        field: 'ev_ebitda',
        headerName: 'EV/EBITDA',
        type: 'numericColumn',
        width: 120,
        valueFormatter: (params) => formatFinancialNumber(params.value),
      },
      {
        field: 'ev_sales',
        headerName: 'EV/Sales',
        type: 'numericColumn',
        width: 110,
        valueFormatter: (params) => formatFinancialNumber(params.value),
      },
      {
        field: 'pb',
        headerName: 'P/B',
        type: 'numericColumn',
        width: 100,
        valueFormatter: (params) => formatFinancialNumber(params.value),
      },
      {
        field: 'ps',
        headerName: 'P/S',
        type: 'numericColumn',
        width: 100,
        valueFormatter: (params) => formatFinancialNumber(params.value),
      },
      {
        field: 'roe',
        headerName: 'ROE',
        type: 'numericColumn',
        width: 100,
        valueFormatter: (params) => formatFinancialNumber(params.value),
      },
      {
        field: 'roa',
        headerName: 'ROA',
        type: 'numericColumn',
        width: 100,
        valueFormatter: (params) => formatFinancialNumber(params.value),
      },
      {
        field: 'debt_ebitda',
        headerName: 'Долг/EBITDA',
        type: 'numericColumn',
        width: 130,
        valueFormatter: (params) => formatFinancialNumber(params.value),
      },
    ],
    [],
  );

  return (
    <DataGrid<MultipleOut>
      columnDefs={columnDefs}
      rowData={multiples}
      loading={loading}
      height={500}
    />
  );
}
