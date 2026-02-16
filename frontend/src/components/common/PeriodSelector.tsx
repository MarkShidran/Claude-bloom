import { Group, SegmentedControl, Text } from '@mantine/core';

interface PeriodSelectorProps {
  standard: string;
  periodType: string;
  onStandardChange: (value: string) => void;
  onPeriodTypeChange: (value: string) => void;
}

export function PeriodSelector({
  standard,
  periodType,
  onStandardChange,
  onPeriodTypeChange,
}: PeriodSelectorProps) {
  return (
    <Group gap="lg">
      <div>
        <Text size="sm" fw={500} mb={4}>
          Стандарт
        </Text>
        <SegmentedControl
          value={standard}
          onChange={onStandardChange}
          data={[
            { label: 'РСБУ', value: 'RSBU' },
            { label: 'МСФО', value: 'IFRS' },
          ]}
        />
      </div>
      <div>
        <Text size="sm" fw={500} mb={4}>
          Период
        </Text>
        <SegmentedControl
          value={periodType}
          onChange={onPeriodTypeChange}
          data={[
            { label: 'Годовой', value: 'annual' },
            { label: 'Квартальный', value: 'quarterly' },
          ]}
        />
      </div>
    </Group>
  );
}
