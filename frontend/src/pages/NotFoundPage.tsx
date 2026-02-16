import { Stack, Title, Text, Button, Center } from '@mantine/core';
import { IconArrowLeft } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@/config/routes';

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <Center h="60vh">
      <Stack align="center" gap="md">
        <Title order={1} size={80} c="dimmed">
          404
        </Title>
        <Title order={2}>Страница не найдена</Title>
        <Text c="dimmed" ta="center" maw={400}>
          Запрашиваемая страница не существует или была перемещена.
        </Text>
        <Button
          leftSection={<IconArrowLeft size={16} />}
          onClick={() => navigate(ROUTES.COMPANIES)}
          variant="outline"
        >
          На главную
        </Button>
      </Stack>
    </Center>
  );
}
