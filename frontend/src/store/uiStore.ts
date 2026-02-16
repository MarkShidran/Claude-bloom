import { create } from 'zustand';

interface UiState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  favoriteCompanyIds: number[];
  addFavorite: (id: number) => void;
  removeFavorite: (id: number) => void;
}

export const useUiStore = create<UiState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  favoriteCompanyIds: [],
  addFavorite: (id: number) =>
    set((state) => ({
      favoriteCompanyIds: state.favoriteCompanyIds.includes(id)
        ? state.favoriteCompanyIds
        : [...state.favoriteCompanyIds, id],
    })),
  removeFavorite: (id: number) =>
    set((state) => ({
      favoriteCompanyIds: state.favoriteCompanyIds.filter(
        (fid) => fid !== id,
      ),
    })),
}));
