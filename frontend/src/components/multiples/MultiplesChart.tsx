import { useMemo } from 'react';
import type { Data, Layout } from 'plotly.js';
import { Chart } from '@/components/common/Chart';
import type { MultipleOut } from '@/types/multiple';

interface MultiplesChartProps {
  multiples: MultipleOut[] | undefined;
  selectedMetrics: string[];
}

const METRIC_LABELS: Record<string, string> = {
  pe: 'P/E',
  ev_ebitda: 'EV/EBITDA',
  ev_sales: 'EV/Sales',
  pb: 'P/B',
  ps: 'P/S',
  roe: 'ROE',
  roa: 'ROA',
  debt_ebitda: 'Долг/EBITDA',
  dividend_yield: 'Дивидендная доходность',
};

const COLORS = [
  '#1971c2',
  '#2b8a3e',
  '#e8590c',
  '#9c36b5',
  '#0c8599',
  '#d6336c',
  '#5c940d',
  '#862e9c',
];

export function MultiplesChart({
  multiples,
  selectedMetrics,
}: MultiplesChartProps) {
  const traces = useMemo<Data[]>(() => {
    if (!multiples || multiples.length === 0 || selectedMetrics.length === 0) {
      return [];
    }

    const sorted = [...multiples].sort(
      (a, b) => new Date(a.calc_date).getTime() - new Date(b.calc_date).getTime(),
    );
    const dates = sorted.map((m) => m.calc_date);

    return selectedMetrics.map((metric, idx) => ({
      type: 'scatter' as const,
      mode: 'lines+markers' as const,
      x: dates,
      y: sorted.map(
        (m) => (m as unknown as Record<string, number | undefined>)[metric] ?? null,
      ),
      name: METRIC_LABELS[metric] ?? metric,
      line: { color: COLORS[idx % COLORS.length], width: 2 },
      marker: { size: 4 },
      yaxis: idx === 0 ? 'y' : 'y2',
    }));
  }, [multiples, selectedMetrics]);

  const layout = useMemo<Partial<Layout>>(() => {
    const hasSecondAxis = selectedMetrics.length > 1;
    return {
      yaxis: {
        title: METRIC_LABELS[selectedMetrics[0]] ?? selectedMetrics[0] ?? '',
      },
      ...(hasSecondAxis
        ? {
            yaxis2: {
              title:
                METRIC_LABELS[selectedMetrics[1]] ?? selectedMetrics[1] ?? '',
              overlaying: 'y' as const,
              side: 'right' as const,
            },
          }
        : {}),
      legend: { orientation: 'h' as const, y: 1.1 },
      xaxis: { title: 'Дата' },
    };
  }, [selectedMetrics]);

  if (!multiples || multiples.length === 0) return null;

  return (
    <Chart
      data={traces}
      layout={layout}
      title="Динамика мультипликаторов"
      height={450}
    />
  );
}
