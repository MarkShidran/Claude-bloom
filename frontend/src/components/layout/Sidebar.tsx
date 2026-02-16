import { NavLink, Stack } from '@mantine/core';
import {
  IconBuilding,
  IconChartBar,
  IconCurrencyRubel,
  IconUsers,
} from '@tabler/icons-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ROUTES } from '@/config/routes';

interface NavItem {
  label: string;
  icon: typeof IconBuilding;
  path: string;
}

const navItems: NavItem[] = [
  { label: 'Компании', icon: IconBuilding, path: ROUTES.COMPANIES },
  { label: 'Мультипликаторы', icon: IconChartBar, path: ROUTES.MULTIPLES },
  { label: 'Макроданные', icon: IconCurrencyRubel, path: ROUTES.MACRO },
  { label: 'Peer Groups', icon: IconUsers, path: ROUTES.PEER_GROUPS },
];

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <Stack gap={4} p="xs">
      {navItems.map((item) => (
        <NavLink
          key={item.path}
          label={item.label}
          leftSection={<item.icon size={20} stroke={1.5} />}
          active={location.pathname.startsWith(item.path)}
          onClick={() => navigate(item.path)}
          variant="filled"
        />
      ))}
    </Stack>
  );
}
