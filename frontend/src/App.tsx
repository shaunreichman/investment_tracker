import React from 'react';
import { BrowserRouter, Routes, Route, useParams } from 'react-router-dom';
import OverallDashboard from './components/OverallDashboard';
import { CompaniesPage } from './components/companies';
import FundDetail from './components/fund/detail/FundDetail';
import { AppStoreProvider } from './store';
import { DockerThemeProvider } from './theme/DockerThemeProvider';
import RouteLayout from './components/layout/RouteLayout';
import './App.css';

// Wrapper component to provide key for FundDetail
const FundDetailWrapper: React.FC = () => {
  const { fundId } = useParams<{ fundId: string }>();
  return <FundDetail key={fundId} />;
};

// Wrapper component to provide key for CompaniesPage
const CompaniesPageWrapper: React.FC = () => {
  const { companyId } = useParams<{ companyId: string }>();
  return <CompaniesPage key={companyId} />;
};

function App() {
  return (
    <DockerThemeProvider>
      <AppStoreProvider>
        <BrowserRouter
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true
          }}
        >
          <Routes>
            <Route path="/" element={
              <RouteLayout>
                <OverallDashboard />
              </RouteLayout>
            } />
            <Route path="/companies/:companyId" element={
              <RouteLayout>
                <CompaniesPageWrapper />
              </RouteLayout>
            } />
            <Route path="/funds/:fundId" element={
              <RouteLayout>
                <FundDetailWrapper />
              </RouteLayout>
            } />
          </Routes>
        </BrowserRouter>
      </AppStoreProvider>
    </DockerThemeProvider>
  );
}

export default App;
