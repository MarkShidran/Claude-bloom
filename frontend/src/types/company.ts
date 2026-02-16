export interface Company {
  id: number;
  name: string;
  name_en?: string;
  ticker?: string;
  inn?: string;
  sector?: string;
  industry?: string;
  country: string;
  is_active: boolean;
  created_at: string;
}

export interface SecurityBrief {
  id: number;
  ticker: string;
  security_type: string;
  currency: string;
  exchange: string;
}

export interface CompanyDetail extends Company {
  ogrn?: string;
  description?: string;
  website?: string;
  edisclosure_id?: string;
  moex_secid?: string;
  updated_at: string;
  securities: SecurityBrief[];
}

export interface CompanyCreate {
  name: string;
  name_en?: string;
  ticker?: string;
  inn?: string;
  sector?: string;
  industry?: string;
  country?: string;
  description?: string;
  website?: string;
  edisclosure_id?: string;
  moex_secid?: string;
}
