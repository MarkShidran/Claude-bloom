import Plot from 'react-plotly.js';
import type { Data, Layout, Config } from 'plotly.js';

interface ChartProps {
  data: Data[];
  layout?: Partial<Layout>;
  title?: string;
  height?: number;
}

export function Chart({ data, layout, title, height = 500 }: ChartProps) {
  const defaultLayout: Partial<Layout> = {
    title: title ? { text: title } : undefined,
    autosize: true,
    height,
    margin: { l: 60, r: 30, t: title ? 50 : 20, b: 50 },
    xaxis: {
      rangeslider: { visible: false },
    },
    font: {
      family: 'system-ui, -apple-system, sans-serif',
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: '#fafafa',
    hovermode: 'x unified' as const,
    ...layout,
  };

  const config: Partial<Config> = {
    displayModeBar: true,
    displaylogo: false,
    responsive: true,
    locale: 'ru',
  };

  return (
    <Plot
      data={data}
      layout={defaultLayout}
      config={config}
      useResizeHandler
      style={{ width: '100%' }}
    />
  );
}
