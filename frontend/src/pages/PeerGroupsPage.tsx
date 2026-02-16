import { Stack, Title, Text, Card } from '@mantine/core';
import { IconUsers } from '@tabler/icons-react';

export function PeerGroupsPage() {
  return (
    <Stack gap="md">
      <Title order={2}>Peer Groups</Title>
      <Card shadow="sm" padding="xl" radius="md" withBorder>
        <Stack align="center" gap="md">
          <IconUsers size={64} stroke={1} color="gray" />
          <Title order={3} c="dimmed">
            Раздел в разработке
          </Title>
          <Text c="dimmed" ta="center">
            Функционал сравнения компаний по группам аналогов будет доступен в
            следующей версии платформы.
          </Text>
        </Stack>
      </Card>
    </Stack>
  );
}
