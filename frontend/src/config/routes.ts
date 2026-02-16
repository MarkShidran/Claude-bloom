export const ROUTES = {
  COMPANIES: '/companies',
  COMPANY_DETAIL: '/companies/:id',
  MACRO: '/macro',
  MULTIPLES: '/multiples',
  PEER_GROUPS: '/peer-groups',
  NOT_FOUND: '*',
} as const;

export function companyDetailPath(id: number | string): string {
  return `/companies/${id}`;
}
