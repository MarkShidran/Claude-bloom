import { useState, useCallback } from 'react';
import { Autocomplete } from '@mantine/core';
import { IconSearch } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { useCompanySearch } from '@/hooks/useCompanies';
import { companyDetailPath } from '@/config/routes';

export function CompanySearch() {
  const [searchValue, setSearchValue] = useState('');
  const navigate = useNavigate();
  const { data: results } = useCompanySearch(searchValue);

  const autocompleteData = (results ?? []).map((company) => ({
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
    <Autocomplete
      placeholder="Поиск компании..."
      leftSection={<IconSearch size={16} />}
      data={autocompleteData.map((item) => item.label)}
      value={searchValue}
      onChange={setSearchValue}
      onOptionSubmit={handleSelect}
      limit={10}
    />
  );
}
