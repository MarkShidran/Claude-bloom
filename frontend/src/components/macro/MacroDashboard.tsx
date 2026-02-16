import { useMemo } from 'react';
import { Grid, Card, Title, Text, SimpleGrid, Stack } from '@mantine/core';
import type { Data, Layout } from 'plotly.js';
import { Chart } from '@/components/common/Chart';
import type { MacroTimeSeries } from '@/types/macro';

interface MacroDashboardProps {
  fxData?: Record<string, MacroTimeSeries>;
  ratesData?: MacroTimeSeries;
  latest?: Record<string, number>;
}

export function MacroDashboard({
  fxData,
  ratesData,
  latest,
}: MacroDashboardProps) {
  const fxTraces = useMemo<Data[]>(() => {
    if (!fxData) return [];
    return Object.entries(fxData).map(([pair, series]) => ({
      type: 'scatter' as const,
      mode: 'lines' as const,
      x: series.data.map((d) => d.date),
      y: series.data.map((d) => d.value),
      name: pair,
      line: { width: 2 },
    }));
  }, [fxData]);

  const ratesTraces = useMemo<Data[]>(() => {
    if (!ratesData) return [];
    return [
      {
        type: 'scatter' as const,
        mode: 'lines' as const,
        x: ratesData.data.map((d) => d.date),
        y: ratesData.data.map((d) => d.value),
        name: ratesData.name,
        line: { shape: 'hv' as const, color: '#c92a2a', width: 2 },
        fill: 'tozeroy' as const,
        fillcolor: 'rgba(201, 42, 42, 0.1)',
      },
    ];
  }, [ratesData]);

  const fxLayout = useMemo<Partial<Layout>>(
    () => ({
      yaxis: { title: 'Курс (руб.)' },
      xaxis: { title: 'Дата' },
      legend: { orientation: 'h' as const, y: 1.1 },
    }),
    [],
  );

  const ratesLayout = useMemo<Partial<Layout>>(
    () => ({
      yaxis: { title: 'Ставка (%)' },
      xaxis: { title: 'Дата' },
    }),
    [],
  );

  return (
    <Stack gap="lg">
      {latest && Object.keys(latest).length > 0 && (
        <div>
          <Title order={4} mb="md">
            Текущие значения
          </Title>
          <SimpleGrid cols={{ base: 2, sm: 3, md: 4 }} spacing="md">
            {Object.entries(latest).map(([key, value]) => (
              <Card key={key} shadow="xs" padding="md" radius="md" withBorder>
                <Text size="xs" c="dimmed">
                  {key}
                </Text>
                <Text size="lg" fw={700}>
                  {value.toLocaleString('ru-RU', {
                    maximumFractionDigits: 4,
                  })}
                </Text>
              </Card>
            ))}
          </SimpleGrid>
        </div>
      )}

      <Grid>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={4} mb="md">
              Валютные курсы
            </Title>
            {fxTraces.length > 0 ? (
              <Chart data={fxTraces} layout={fxLayout} height={400} />
            ) : (
              <Text c="dimmed">Нет данных</Text>
            )}
          </Card>
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={4} mb="md">
              Ключевая ставка ЦБ РФ
            </Title>
            {ratesTraces.length > 0 ? (
              <Chart data={ratesTraces} layout={ratesLayout} height={400} />
            ) : (
              <Text c="dimmed">Нет данных</Text>
            )}
          </Card>
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
