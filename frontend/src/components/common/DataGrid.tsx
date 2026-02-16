import { useCallback, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef, GridReadyEvent, GridApi } from 'ag-grid-community';

export function formatFinancialNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  return value.toLocaleString('ru-RU', { maximumFractionDigits: 2 });
}

interface DataGridProps<T> {
  columnDefs: ColDef<T>[];
  rowData: T[] | undefined;
  loading?: boolean;
  onExportCsv?: () => void;
  height?: string | number;
  onRowClicked?: (data: T) => void;
}

export function DataGrid<T>({
  columnDefs,
  rowData,
  loading = false,
  height = 600,
  onRowClicked,
}: DataGridProps<T>) {
  const gridRef = useRef<AgGridReact<T>>(null);
  const gridApiRef = useRef<GridApi<T> | null>(null);

  const defaultColDef: ColDef<T> = {
    resizable: true,
    sortable: true,
    filter: true,
    minWidth: 80,
  };

  const onGridReady = useCallback((event: GridReadyEvent<T>) => {
    gridApiRef.current = event.api;
    event.api.sizeColumnsToFit();
  }, []);

  const handleRowClicked = useCallback(
    (event: { data: T | undefined }) => {
      if (onRowClicked && event.data) {
        onRowClicked(event.data);
      }
    },
    [onRowClicked],
  );

  return (
    <div className="ag-theme-alpine" style={{ height, width: '100%' }}>
      <AgGridReact<T>
        ref={gridRef}
        columnDefs={columnDefs}
        rowData={rowData ?? []}
        defaultColDef={defaultColDef}
        onGridReady={onGridReady}
        onRowClicked={handleRowClicked}
        loading={loading}
        animateRows
        pagination
        paginationPageSize={50}
        suppressCellFocus
      />
    </div>
  );
}
