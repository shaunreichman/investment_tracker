/**
 * App Component
 * 
 * Main application component that sets up routing and provides context.
 * Uses centralized route configuration from routes/index.tsx.
 */

import React from 'react';
import { BrowserRouter, useRoutes } from 'react-router-dom';
import { DomainErrorBoundary } from '@/shared/ui/feedback';
import { DockerThemeProvider } from '@/theme/DockerThemeProvider';
import { AppStoreProvider } from '@/store';
import { appRoutes } from '@/routes';

/**
 * Routes component that renders routes using useRoutes hook.
 * Must be inside BrowserRouter context.
 */
const RoutesRenderer: React.FC = () => {
  const routes = useRoutes(appRoutes);
  return routes;
};

/**
 * Main App component.
 * Wraps application with providers and sets up routing.
 */
const App: React.FC = () => {
  return (
    <DomainErrorBoundary domain="general" showDetails={process.env.NODE_ENV === 'development'}>
      <DockerThemeProvider>
        <AppStoreProvider>
          <BrowserRouter
            future={{
              v7_startTransition: true,
              v7_relativeSplatPath: true
            }}
          >
            <RoutesRenderer />
          </BrowserRouter>
        </AppStoreProvider>
      </DockerThemeProvider>
    </DomainErrorBoundary>
  );
};

export default App;

