import { Button } from '@mantine/core';
import { IconDownload } from '@tabler/icons-react';

interface ExportButtonProps {
  onClick: () => void | Promise<void>;
  label?: string;
  loading?: boolean;
}

export function ExportButton({
  onClick,
  label = 'Экспорт в Excel',
  loading = false,
}: ExportButtonProps) {
  return (
    <Button
      variant="outline"
      leftSection={<IconDownload size={16} />}
      onClick={onClick}
      loading={loading}
    >
      {label}
    </Button>
  );
}
