import { useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Title, Group, Select, Pagination } from '@mantine/core';
import dayjs from 'dayjs';
import type { ColDef } from 'ag-grid-community';
import { DataGrid, formatFinancialNumber } from '@/components/common/DataGrid';
import { useMultiplesScreen } from '@/hooks/useMultiples';
import { companyDetailPath } from '@/config/routes';
import type { MultipleScreenRow } from '@/types/multiple';

const PAGE_SIZE = 50;

const SECTOR_OPTIONS = [
  { value: '', label: 'Все секторы' },
  { value: 'Нефть и газ', label: 'Нефть и газ' },
  { value: 'Финансы', label: 'Финансы' },
  { value: 'Металлургия', label: 'Металлургия' },
  { value: 'Электроэнергетика', label: 'Электроэнергетика' },
  { value: 'Телекоммуникации', label: 'Телекоммуникации' },
  { value: 'Транспорт', label: 'Транспорт' },
  { value: 'Ритейл', label: 'Ритейл' },
  { value: 'IT', label: 'IT' },
  { value: 'Химия', label: 'Химия' },
];

export function MultiplesPage() {
  const navigate = useNavigate();
  const [sector, setSector] = useState('');
  const [page, setPage] = useState(1);

  const offset = (page - 1) * PAGE_SIZE;

  const { data, isLoading } = useMultiplesScreen({
    sector: sector || undefined,
    offset,
    limit: PAGE_SIZE,
  });

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;

  const columnDefs = useMemo<ColDef<MultipleScreenRow>[]>(
    () => [
      {
        field: 'company_name',
        headerName: 'Компания',
        flex: 2,
        minWidth: 200,
        pinned: 'left',
      },
      {
        field: 'ticker',
        headerName: 'Тикер',
        width: 100,
      },
      {
        field: 'sector',
        headerName: 'Сектор',
        width: 150,
      },
      {
        field: 'calc_date',
        headerName: 'Дата',
        width: 120,
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
      {
        field: 'market_cap',
        headerName: 'Капитализация',
        type: 'numericColumn',
        width: 150,
        valueFormatter: (params) => formatFinancialNumber(params.value),
      },
    ],
    [],
  );

  const handleRowClick = useCallback(
    (row: MultipleScreenRow) => {
      navigate(companyDetailPath(row.company_id));
    },
    [navigate],
  );

  const handleSectorChange = useCallback(
    (value: string | null) => {
      setSector(value ?? '');
      setPage(1);
    },
    [],
  );

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <Title order={2}>Мультипликаторы</Title>
        <Select
          placeholder="Сектор"
          data={SECTOR_OPTIONS}
          value={sector}
          onChange={handleSectorChange}
          clearable
          w={220}
        />
      </Group>

      <DataGrid<MultipleScreenRow>
        columnDefs={columnDefs}
        rowData={data?.items}
        loading={isLoading}
        onRowClicked={handleRowClick}
        height={650}
      />

      {totalPages > 1 && (
        <Group justify="center">
          <Pagination value={page} onChange={setPage} total={totalPages} />
        </Group>
      )}
    </Stack>
  );
}
