import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BrowserRouter } from 'react-router-dom';
import { AppStoreProvider } from '../store/AppStoreProvider';

// Create a consistent theme for testing
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// Base render function with common providers
const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <AppStoreProvider>
          {children}
        </AppStoreProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

// Custom render function with all providers
const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Render with only theme provider (for components that don't need router/store)
const renderWithTheme = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const ThemeWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  );
  
  return render(ui, { wrapper: ThemeWrapper, ...options });
};

// Render with only router (for components that need routing but not store)
const renderWithRouter = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const RouterWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        {children}
      </ThemeProvider>
    </BrowserRouter>
  );
  
  return render(ui, { wrapper: RouterWrapper, ...options });
};

// Export all render functions
export {
  customRender as render,
  renderWithTheme,
  renderWithRouter,
  AllTheProviders,
  theme,
};

// Re-export testing library utilities for convenience
export * from '@testing-library/react';
export * from '@testing-library/user-event';
