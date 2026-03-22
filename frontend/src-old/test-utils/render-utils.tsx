import React from 'react';
import { render as originalRender, RenderOptions } from '@testing-library/react';
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
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
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
) => originalRender(ui, { wrapper: AllTheProviders, ...options });

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
  
  return originalRender(ui, { wrapper: ThemeWrapper, ...options });
};

// Render with only router (for components that need routing but not store)
const renderWithRouter = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const RouterWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <ThemeProvider theme={theme}>
        {children}
      </ThemeProvider>
    </BrowserRouter>
  );
  
  return originalRender(ui, { wrapper: RouterWrapper, ...options });
};

// Export all render functions
export {
  customRender as render,
  renderWithTheme,
  renderWithRouter,
  AllTheProviders,
  theme,
};

// Table-specific render functions
export const renderTableComponent = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <table>
      <tbody>
        {children}
      </tbody>
    </table>
  );

  return originalRender(ui, { wrapper: Wrapper, ...options });
};

export const renderTableComponentWithCustomWrapper = (
  ui: React.ReactElement,
  wrapperProps?: React.HTMLAttributes<HTMLTableElement>,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <table {...wrapperProps}>
      <tbody>
        {children}
      </tbody>
    </table>
  );

  return originalRender(ui, { wrapper: Wrapper, ...options });
};

// Re-export testing library utilities for convenience (but not render to avoid conflict)
export * from '@testing-library/user-event';
export { screen, waitFor, fireEvent, within, waitForElementToBeRemoved } from '@testing-library/react';
