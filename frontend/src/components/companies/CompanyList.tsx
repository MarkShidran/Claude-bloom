import { useMemo } from 'react';
import type { ColDef } from 'ag-grid-community';
import { DataGrid } from '@/components/common/DataGrid';
import type { Company } from '@/types/company';

interface CompanyListProps {
  companies: Company[] | undefined;
  loading: boolean;
  onRowClick: (company: Company) => void;
}

export function CompanyList({
  companies,
  loading,
  onRowClick,
}: CompanyListProps) {
  const columnDefs = useMemo<ColDef<Company>[]>(
    () => [
      {
        field: 'name',
        headerName: 'Название',
        flex: 2,
        minWidth: 200,
      },
      {
        field: 'ticker',
        headerName: 'Тикер',
        flex: 1,
        minWidth: 100,
      },
      {
        field: 'sector',
        headerName: 'Сектор',
        flex: 1,
        minWidth: 150,
      },
      {
        field: 'industry',
        headerName: 'Отрасль',
        flex: 1,
        minWidth: 150,
      },
      {
        field: 'country',
        headerName: 'Страна',
        flex: 1,
        minWidth: 100,
      },
    ],
    [],
  );

  return (
    <DataGrid<Company>
      columnDefs={columnDefs}
      rowData={companies}
      loading={loading}
      onRowClicked={onRowClick}
      height={600}
    />
  );
}
