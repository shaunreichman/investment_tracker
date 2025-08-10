import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import OverallDashboard from './components/OverallDashboard';
import CompaniesPage from './components/CompaniesPage';
import FundDetail from './components/fund/detail/FundDetail';
import './App.css';

function App() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <div className="App">
        <Routes>
          <Route path="/" element={<OverallDashboard />} />
          <Route path="/companies/:companyId" element={<CompaniesPage />} />
          <Route path="/funds/:fundId" element={<FundDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
