/**
 * Centralized Routes Configuration
 * 
 * Single source of truth for all application routes.
 * Imports route definitions from domain route files and combines them.
 * 
 * Usage:
 *   import { appRoutes } from '@/routes';
 */

import { RouteObject } from 'react-router-dom';
import RouteLayout from '@/shared/ui/layout/RouteLayout';
import { DomainErrorBoundary } from '@/shared/ui/feedback';

// Domain route imports
import { companyRoutes } from '@/company/routes';
import { fundRoutes } from '@/fund/routes';
import { entityRoutes } from '@/entity/routes';
import { bankRoutes } from '@/bank/routes';
import { ratesRoutes } from '@/rates/routes';

// Page imports for root routes
import { AllCompaniesPage } from '@/company/pages';

/**
 * Root route definition.
 * Maps "/" to AllCompaniesPage as the landing page.
 */
const rootRoute: RouteObject = {
  path: '/',
  element: (
    <RouteLayout>
      <DomainErrorBoundary domain="company" showDetails={process.env.NODE_ENV === 'development'}>
        <AllCompaniesPage />
      </DomainErrorBoundary>
    </RouteLayout>
  ),
};

/**
 * Combined application routes.
 * 
 * Order matters: more specific routes should come before less specific ones.
 * React Router matches routes from top to bottom and uses the first match.
 */
export const appRoutes: RouteObject[] = [
  // Root route - landing page
  rootRoute,
  // Domain routes - imported from respective domain route files
  ...companyRoutes,
  ...fundRoutes,
  ...entityRoutes,
  ...bankRoutes,
  ...ratesRoutes,
];

