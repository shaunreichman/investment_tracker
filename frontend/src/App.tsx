import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import FundDetail from './components/FundDetail';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/fund/:fundId" element={<FundDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
