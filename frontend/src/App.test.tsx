import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders investment tracker app', () => {
  render(<App />);
  // The app should render without crashing
  expect(screen.getByRole('progressbar')).toBeInTheDocument();
});
