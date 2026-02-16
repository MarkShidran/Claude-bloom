import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Stack, Group, Title, Select, Pagination } from '@mantine/core';
import { SearchInput } from '@/components/common/SearchInput';
import { CompanyList } from '@/components/companies/CompanyList';
import { useCompanies } from '@/hooks/useCompanies';
import { companyDetailPath } from '@/config/routes';
import type { Company } from '@/types/company';

const PAGE_SIZE = 50;

const SECTOR_OPTIONS = [
  { value: '', label: 'Все секторы' },
  { value: 'Нефть и газ', label: 'Нефть и газ' },
  { value: 'Финансы', label: 'Финансы' },
  { value: 'Металлургия', label: 'Металлургия' },
  { value: 'Электроэнергетика', label: 'Электроэнергетика' },
  { value: 'Телекоммуникации', label: 'Телекоммуникации' },
  { value: 'Транспорт', label: 'Транспорт' },
  { value: 'Ритейл', label: 'Ритейл' },
  { value: 'IT', label: 'IT' },
  { value: 'Химия', label: 'Химия' },
];

export function CompaniesPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [sector, setSector] = useState('');
  const [page, setPage] = useState(1);

  const offset = (page - 1) * PAGE_SIZE;

  const { data, isLoading } = useCompanies({
    search: search || undefined,
    sector: sector || undefined,
    offset,
    limit: PAGE_SIZE,
  });

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;

  const handleRowClick = useCallback(
    (company: Company) => {
      navigate(companyDetailPath(company.id));
    },
    [navigate],
  );

  const handleSectorChange = useCallback(
    (value: string | null) => {
      setSector(value ?? '');
      setPage(1);
    },
    [],
  );

  const handleSearchChange = useCallback(
    (value: string) => {
      setSearch(value);
      setPage(1);
    },
    [],
  );

  return (
    <Stack gap="md">
      <Title order={2}>Компании</Title>

      <Group>
        <SearchInput
          value={search}
          onChange={handleSearchChange}
          placeholder="Поиск по названию или тикеру..."
        />
        <Select
          placeholder="Сектор"
          data={SECTOR_OPTIONS}
          value={sector}
          onChange={handleSectorChange}
          clearable
          w={220}
        />
      </Group>

      <CompanyList
        companies={data?.items}
        loading={isLoading}
        onRowClick={handleRowClick}
      />

      {totalPages > 1 && (
        <Group justify="center">
          <Pagination value={page} onChange={setPage} total={totalPages} />
        </Group>
      )}
    </Stack>
  );
}
