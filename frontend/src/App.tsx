import React, { useEffect, useState } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

function App() {
  const [apiStatus, setApiStatus] = useState<string>('');
  const [apiMessage, setApiMessage] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/health`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        setApiStatus(data.status);
        setApiMessage(data.message);
      })
      .catch((err) => {
        setError(err.message);
      });
  }, []);

  return (
    <div className="App">
      <h1>Investment Tracker UI</h1>
      <div style={{ marginTop: 32 }}>
        <h2>Flask API Health Check</h2>
        {error ? (
          <p style={{ color: 'red' }}>Error: {error}</p>
        ) : apiStatus ? (
          <>
            <p>Status: <b>{apiStatus}</b></p>
            <p>Message: {apiMessage}</p>
          </>
        ) : (
          <p>Loading...</p>
        )}
      </div>
    </div>
  );
}

export default App;
