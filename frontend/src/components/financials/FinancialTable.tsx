import { useMemo } from 'react';
import type { ColDef, CellClassParams } from 'ag-grid-community';
import { DataGrid, formatFinancialNumber } from '@/components/common/DataGrid';
import type { FinancialStatement, StatementItem } from '@/types/financial';

interface FinancialTableProps {
  statement: FinancialStatement | undefined;
  loading?: boolean;
}

interface FlatItem extends StatementItem {
  indent: number;
  isParent: boolean;
}

function buildFlatItems(items: StatementItem[]): FlatItem[] {
  const sorted = [...items].sort((a, b) => a.sort_order - b.sort_order);
  const childCodes = new Set(
    sorted.filter((i) => i.parent_code).map((i) => i.parent_code!),
  );

  const codeDepth: Record<string, number> = {};

  function getDepth(item: StatementItem): number {
    if (codeDepth[item.code] !== undefined) return codeDepth[item.code];
    if (!item.parent_code) {
      codeDepth[item.code] = 0;
      return 0;
    }
    const parent = sorted.find((i) => i.code === item.parent_code);
    if (!parent) {
      codeDepth[item.code] = 0;
      return 0;
    }
    codeDepth[item.code] = getDepth(parent) + 1;
    return codeDepth[item.code];
  }

  return sorted.map((item) => ({
    ...item,
    indent: getDepth(item),
    isParent: childCodes.has(item.code),
  }));
}

export function FinancialTable({ statement, loading }: FinancialTableProps) {
  const flatItems = useMemo(
    () => (statement ? buildFlatItems(statement.items) : []),
    [statement],
  );

  const columnDefs = useMemo<ColDef<FlatItem>[]>(
    () => [
      {
        field: 'code',
        headerName: 'Код',
        width: 100,
        cellStyle: (params: CellClassParams<FlatItem>) =>
          params.data?.isParent ? { fontWeight: 'bold' } : undefined,
      },
      {
        field: 'name_ru',
        headerName: 'Наименование',
        flex: 2,
        minWidth: 300,
        cellStyle: (params: CellClassParams<FlatItem>) => ({
          paddingLeft: `${(params.data?.indent ?? 0) * 20 + 12}px`,
          fontWeight: params.data?.isParent ? 'bold' : 'normal',
        }),
      },
      {
        field: 'value',
        headerName: 'Значение',
        flex: 1,
        minWidth: 150,
        type: 'numericColumn',
        valueFormatter: (params) => formatFinancialNumber(params.value),
        cellStyle: (params: CellClassParams<FlatItem>) =>
          params.data?.isParent ? { fontWeight: 'bold' } : undefined,
      },
    ],
    [],
  );

  return (
    <DataGrid<FlatItem>
      columnDefs={columnDefs}
      rowData={flatItems}
      loading={loading}
      height={700}
    />
  );
}
