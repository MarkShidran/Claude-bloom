import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import CompaniesPage from './pages/CompaniesPage';
import CompanyDetailPage from './pages/CompanyDetailPage';
import MacroPage from './pages/MacroPage';
import MultiplesPage from './pages/MultiplesPage';
import PeerGroupsPage from './pages/PeerGroupsPage';
import NotFoundPage from './pages/NotFoundPage';
import { ROUTES } from './config/routes';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to={ROUTES.COMPANIES} replace />} />
          <Route path={ROUTES.COMPANIES} element={<CompaniesPage />} />
          <Route path={ROUTES.COMPANY_DETAIL} element={<CompanyDetailPage />} />
          <Route path={ROUTES.MACRO} element={<MacroPage />} />
          <Route path={ROUTES.MULTIPLES} element={<MultiplesPage />} />
          <Route path={ROUTES.PEER_GROUPS} element={<PeerGroupsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
