import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Stack, Title, Group } from '@mantine/core';
import { DatePickerInput } from '@mantine/dates';
import dayjs from 'dayjs';
import { MacroDashboard } from '@/components/macro/MacroDashboard';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { macroApi } from '@/api/macro';

export function MacroPage() {
  const [dateRange, setDateRange] = useState<[Date | null, Date | null]>([
    dayjs().subtract(1, 'year').toDate(),
    new Date(),
  ]);

  const fromDate = dateRange[0]
    ? dayjs(dateRange[0]).format('YYYY-MM-DD')
    : undefined;
  const toDate = dateRange[1]
    ? dayjs(dateRange[1]).format('YYYY-MM-DD')
    : undefined;

  const {
    data: fxData,
    isLoading: fxLoading,
  } = useQuery({
    queryKey: ['macroFx', fromDate, toDate],
    queryFn: () => macroApi.getFx({ from_date: fromDate, to_date: toDate }),
    staleTime: 10 * 60 * 1000,
  });

  const {
    data: ratesData,
    isLoading: ratesLoading,
  } = useQuery({
    queryKey: ['macroRates', fromDate, toDate],
    queryFn: () =>
      macroApi.getRates({ from_date: fromDate, to_date: toDate }),
    staleTime: 10 * 60 * 1000,
  });

  const { data: latestData } = useQuery({
    queryKey: ['macroLatest'],
    queryFn: () => macroApi.getLatest(),
    staleTime: 5 * 60 * 1000,
  });

  const isLoading = fxLoading || ratesLoading;

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <Title order={2}>Макроданные</Title>
        <DatePickerInput
          type="range"
          label="Период"
          placeholder="Выберите период"
          value={dateRange}
          onChange={setDateRange}
          w={300}
        />
      </Group>

      {isLoading ? (
        <LoadingSpinner />
      ) : (
        <MacroDashboard
          fxData={fxData}
          ratesData={ratesData}
          latest={latestData}
        />
      )}
    </Stack>
  );
}
