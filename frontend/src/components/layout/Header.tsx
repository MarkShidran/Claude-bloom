import { Group, Burger, Title, Autocomplete } from '@mantine/core';
import { IconSearch } from '@tabler/icons-react';
import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCompanySearch } from '@/hooks/useCompanies';
import { companyDetailPath } from '@/config/routes';
import { useUiStore } from '@/store/uiStore';

export function Header() {
  const [searchValue, setSearchValue] = useState('');
  const navigate = useNavigate();
  const { sidebarOpen, toggleSidebar } = useUiStore();
  const { data: searchResults } = useCompanySearch(searchValue);

  const autocompleteData = (searchResults ?? []).map((company) => ({
    value: String(company.id),
    label: company.ticker
      ? `${company.name} (${company.ticker})`
      : company.name,
  }));

  const handleSelect = useCallback(
    (value: string) => {
      const selected = autocompleteData.find((item) => item.label === value);
      if (selected) {
        navigate(companyDetailPath(selected.value));
        setSearchValue('');
      }
    },
    [autocompleteData, navigate],
  );

  return (
    <Group h="100%" px="md" justify="space-between">
      <Group>
        <Burger
          opened={sidebarOpen}
          onClick={toggleSidebar}
          hiddenFrom="sm"
          size="sm"
        />
        <Title order={3} c="blue.7">
          Claude Bloom
        </Title>
      </Group>
      <Autocomplete
        placeholder="Поиск компании..."
        leftSection={<IconSearch size={16} />}
        data={autocompleteData.map((item) => item.label)}
        value={searchValue}
        onChange={setSearchValue}
        onOptionSubmit={handleSelect}
        w={350}
        limit={10}
      />
    </Group>
  );
}
