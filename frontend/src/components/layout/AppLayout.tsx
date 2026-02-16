import { AppShell } from '@mantine/core';
import { Outlet } from 'react-router-dom';
import { useUiStore } from '@/store/uiStore';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export function AppLayout() {
  const sidebarOpen = useUiStore((state) => state.sidebarOpen);

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 250,
        breakpoint: 'sm',
        collapsed: { mobile: !sidebarOpen, desktop: !sidebarOpen },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Header />
      </AppShell.Header>

      <AppShell.Navbar>
        <Sidebar />
      </AppShell.Navbar>

      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}
