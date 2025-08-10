import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import OverallDashboard from './components/OverallDashboard';
import { EnhancedCompaniesPage } from './components/companies';
import FundDetail from './components/fund/detail/FundDetail';
import { AppStoreProvider } from './store';
import './App.css';

function App() {
  return (
    <AppStoreProvider>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true
        }}
      >
        <div className="App">
          <Routes>
            <Route path="/" element={<OverallDashboard />} />
            <Route path="/companies/:companyId" element={<EnhancedCompaniesPage />} />
            <Route path="/funds/:fundId" element={<FundDetail />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AppStoreProvider>
  );
}

export default App;
