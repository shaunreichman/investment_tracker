/**
 * Company Domain Routes
 * 
 * Defines React Router routes for the company domain.
 * 
 * Usage:
 *   import { companyRoutes } from '@/company/routes';
 */

import { RouteObject } from 'react-router-dom';
import RouteLayout from '@/shared/ui/layout/RouteLayout';
import { DomainErrorBoundary } from '@/shared/ui/feedback';
import { AllCompaniesPage, CompanyPageWrapper } from './pages';

/**
 * Company domain routes.
 * 
 * Defines routes for company management pages.
 */
export const companyRoutes: RouteObject[] = [
  {
    path: '/companies',
    element: (
      <RouteLayout>
        <DomainErrorBoundary domain="company" showDetails={process.env.NODE_ENV === 'development'}>
          <AllCompaniesPage />
        </DomainErrorBoundary>
      </RouteLayout>
    ),
  },
  {
    path: '/companies/:companyId',
    element: (
      <RouteLayout>
        <DomainErrorBoundary domain="company" showDetails={process.env.NODE_ENV === 'development'}>
          <CompanyPageWrapper />
        </DomainErrorBoundary>
      </RouteLayout>
    ),
  },
];

