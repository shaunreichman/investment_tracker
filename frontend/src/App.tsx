import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import OverallDashboard from './components/OverallDashboard';
import { EnhancedCompaniesPage } from './components/companies';
import FundDetail from './components/fund/detail/FundDetail';
import { AppStoreProvider } from './store';
import { DockerThemeProvider } from './theme/DockerThemeProvider';
import RouteLayout from './components/layout/RouteLayout';
import './App.css';

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
                <EnhancedCompaniesPage />
              </RouteLayout>
            } />
            <Route path="/funds/:fundId" element={
              <RouteLayout>
                <FundDetail />
              </RouteLayout>
            } />
          </Routes>
        </BrowserRouter>
      </AppStoreProvider>
    </DockerThemeProvider>
  );
}

export default App;
