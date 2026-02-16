import { Card, SimpleGrid, Text, Stack } from '@mantine/core';
import type { QuoteStats as QuoteStatsType } from '@/types/quote';
import { formatFinancialNumber } from '@/components/common/DataGrid';
import dayjs from 'dayjs';

interface QuoteStatsProps {
  stats: QuoteStatsType | undefined;
}

interface StatCardProps {
  label: string;
  value: string;
  color?: string;
}

function StatCard({ label, value, color }: StatCardProps) {
  return (
    <Card shadow="xs" padding="md" radius="md" withBorder>
      <Stack gap={2}>
        <Text size="xs" c="dimmed">
          {label}
        </Text>
        <Text size="lg" fw={700} c={color}>
          {value}
        </Text>
      </Stack>
    </Card>
  );
}

function formatReturn(value: number | undefined): { text: string; color: string } {
  if (value === undefined || value === null)
    return { text: '—', color: 'dimmed' };
  const pct = (value * 100).toLocaleString('ru-RU', {
    maximumFractionDigits: 2,
  });
  const sign = value >= 0 ? '+' : '';
  return {
    text: `${sign}${pct}%`,
    color: value > 0 ? 'green' : value < 0 ? 'red' : 'dimmed',
  };
}

export function QuoteStatsDisplay({ stats }: QuoteStatsProps) {
  if (!stats) return null;

  const ret1m = formatReturn(stats.return_1m);
  const ret3m = formatReturn(stats.return_3m);
  const retYtd = formatReturn(stats.return_ytd);
  const ret1y = formatReturn(stats.return_1y);

  return (
    <SimpleGrid cols={{ base: 2, sm: 3, md: 4, lg: 6 }} spacing="md">
      <StatCard
        label="Последняя цена"
        value={
          stats.last_price !== undefined
            ? formatFinancialNumber(stats.last_price)
            : '—'
        }
      />
      <StatCard
        label="Дата"
        value={
          stats.last_date ? dayjs(stats.last_date).format('DD.MM.YYYY') : '—'
        }
      />
      <StatCard
        label="52w High"
        value={formatFinancialNumber(stats.high_52w)}
      />
      <StatCard
        label="52w Low"
        value={formatFinancialNumber(stats.low_52w)}
      />
      <StatCard
        label="Ср. объём (30д)"
        value={formatFinancialNumber(stats.avg_volume_30d)}
      />
      <StatCard label="Доходность 1М" value={ret1m.text} color={ret1m.color} />
      <StatCard label="Доходность 3М" value={ret3m.text} color={ret3m.color} />
      <StatCard label="Доходность YTD" value={retYtd.text} color={retYtd.color} />
      <StatCard label="Доходность 1Г" value={ret1y.text} color={ret1y.color} />
      <StatCard
        label="Волатильность 1Г"
        value={
          stats.volatility_1y !== undefined
            ? `${(stats.volatility_1y * 100).toLocaleString('ru-RU', { maximumFractionDigits: 1 })}%`
            : '—'
        }
      />
    </SimpleGrid>
  );
}
