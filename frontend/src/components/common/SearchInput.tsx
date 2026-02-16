import { useEffect, useState, useRef, useCallback } from 'react';
import { TextInput } from '@mantine/core';
import { IconSearch } from '@tabler/icons-react';

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  loading?: boolean;
}

export function SearchInput({
  value,
  onChange,
  placeholder = 'Поиск...',
  loading = false,
}: SearchInputProps) {
  const [internalValue, setInternalValue] = useState(value);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const debouncedOnChange = useCallback(
    (val: string) => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      timerRef.current = setTimeout(() => {
        onChange(val);
      }, 300);
    },
    [onChange],
  );

  useEffect(() => {
    setInternalValue(value);
  }, [value]);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newVal = event.currentTarget.value;
    setInternalValue(newVal);
    debouncedOnChange(newVal);
  };

  return (
    <TextInput
      value={internalValue}
      onChange={handleChange}
      placeholder={placeholder}
      leftSection={<IconSearch size={16} />}
      rightSection={loading ? undefined : undefined}
    />
  );
}
