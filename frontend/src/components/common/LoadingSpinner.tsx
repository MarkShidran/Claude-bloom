import { Center, Loader, type MantineSize } from '@mantine/core';

interface LoadingSpinnerProps {
  size?: MantineSize;
}

export function LoadingSpinner({ size = 'lg' }: LoadingSpinnerProps) {
  return (
    <Center h={300}>
      <Loader size={size} />
    </Center>
  );
}
