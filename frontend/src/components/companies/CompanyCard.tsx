import {
  Card,
  Group,
  Title,
  Text,
  Badge,
  Anchor,
  Stack,
  SimpleGrid,
} from '@mantine/core';
import type { CompanyDetail } from '@/types/company';

interface CompanyCardProps {
  company: CompanyDetail;
}

export function CompanyCard({ company }: CompanyCardProps) {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Group justify="space-between" mb="md">
        <div>
          <Title order={2}>{company.name}</Title>
          {company.name_en && (
            <Text c="dimmed" size="sm">
              {company.name_en}
            </Text>
          )}
        </div>
        {company.ticker && (
          <Badge size="xl" variant="filled" color="blue">
            {company.ticker}
          </Badge>
        )}
      </Group>

      <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md" mb="md">
        {company.sector && (
          <Stack gap={2}>
            <Text size="xs" c="dimmed">
              Сектор
            </Text>
            <Text size="sm" fw={500}>
              {company.sector}
            </Text>
          </Stack>
        )}
        {company.industry && (
          <Stack gap={2}>
            <Text size="xs" c="dimmed">
              Отрасль
            </Text>
            <Text size="sm" fw={500}>
              {company.industry}
            </Text>
          </Stack>
        )}
        <Stack gap={2}>
          <Text size="xs" c="dimmed">
            Страна
          </Text>
          <Text size="sm" fw={500}>
            {company.country}
          </Text>
        </Stack>
        {company.inn && (
          <Stack gap={2}>
            <Text size="xs" c="dimmed">
              ИНН
            </Text>
            <Text size="sm" fw={500}>
              {company.inn}
            </Text>
          </Stack>
        )}
      </SimpleGrid>

      {company.website && (
        <Anchor href={company.website} target="_blank" size="sm" mb="md">
          {company.website}
        </Anchor>
      )}

      {company.securities.length > 0 && (
        <div>
          <Text size="xs" c="dimmed" mb={4}>
            Ценные бумаги
          </Text>
          <Group gap="xs">
            {company.securities.map((sec) => (
              <Badge key={sec.id} variant="light" color="gray">
                {sec.ticker} ({sec.security_type} / {sec.exchange} /{' '}
                {sec.currency})
              </Badge>
            ))}
          </Group>
        </div>
      )}
    </Card>
  );
}
