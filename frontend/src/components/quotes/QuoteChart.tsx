import { useMemo } from 'react';
import type { Data, Layout } from 'plotly.js';
import { Chart } from '@/components/common/Chart';
import type { QuoteTimeSeries } from '@/types/quote';

interface QuoteChartProps {
  data: QuoteTimeSeries | undefined;
  chartType: 'candlestick' | 'line';
}

export function QuoteChart({ data, chartType }: QuoteChartProps) {
  const traces = useMemo<Data[]>(() => {
    if (!data || data.quotes.length === 0) return [];

    const dates = data.quotes.map((q) => q.trade_date);
    const volumes = data.quotes.map((q) => q.volume ?? 0);

    if (chartType === 'candlestick') {
      return [
        {
          type: 'candlestick' as const,
          x: dates,
          open: data.quotes.map((q) => q.open ?? q.close),
          high: data.quotes.map((q) => q.high ?? q.close),
          low: data.quotes.map((q) => q.low ?? q.close),
          close: data.quotes.map((q) => q.close),
          increasing: { line: { color: '#2b8a3e' } },
          decreasing: { line: { color: '#c92a2a' } },
          name: data.ticker,
          yaxis: 'y',
        },
        {
          type: 'bar' as const,
          x: dates,
          y: volumes,
          marker: { color: 'rgba(100, 100, 200, 0.3)' },
          name: 'Объём',
          yaxis: 'y2',
        },
      ];
    }

    return [
      {
        type: 'scatter' as const,
        mode: 'lines' as const,
        x: dates,
        y: data.quotes.map((q) => q.close),
        line: { color: '#1971c2', width: 2 },
        name: data.ticker,
        yaxis: 'y',
      },
      {
        type: 'bar' as const,
        x: dates,
        y: volumes,
        marker: { color: 'rgba(100, 100, 200, 0.3)' },
        name: 'Объём',
        yaxis: 'y2',
      },
    ];
  }, [data, chartType]);

  const layout = useMemo<Partial<Layout>>(
    () => ({
      xaxis: {
        rangeslider: { visible: false },
        rangeselector: {
          buttons: [
            { count: 1, label: '1М', step: 'month', stepmode: 'backward' },
            { count: 3, label: '3М', step: 'month', stepmode: 'backward' },
            { count: 6, label: '6М', step: 'month', stepmode: 'backward' },
            { count: 1, label: 'YTD', step: 'year', stepmode: 'todate' },
            { count: 1, label: '1Г', step: 'year', stepmode: 'backward' },
            { step: 'all', label: 'Все' },
          ],
        },
      },
      yaxis: {
        title: `Цена (${data?.currency ?? ''})`,
        domain: [0.25, 1],
      },
      yaxis2: {
        title: 'Объём',
        domain: [0, 0.2],
        showgrid: false,
      },
      legend: { orientation: 'h', y: 1.12 },
      grid: { rows: 2, columns: 1, pattern: 'independent' as const },
    }),
    [data?.currency],
  );

  if (!data || data.quotes.length === 0) {
    return null;
  }

  return (
    <Chart
      data={traces}
      layout={layout}
      title={`${data.ticker} — Котировки`}
      height={600}
    />
  );
}
