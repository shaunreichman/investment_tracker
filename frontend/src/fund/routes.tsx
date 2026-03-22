/**
 * Fund Domain Routes
 * 
 * Defines React Router routes for the fund domain.
 * 
 * Usage:
 *   import { fundRoutes } from '@/fund/routes';
 */

import { RouteObject } from 'react-router-dom';
import RouteLayout from '@/shared/ui/layout/RouteLayout';
import { DomainErrorBoundary } from '@/shared/ui/feedback';
import { FundPageWrapper } from './pages';

/**
 * Fund domain routes.
 * 
 * Defines routes for fund management pages.
 */
export const fundRoutes: RouteObject[] = [
  {
    path: '/funds/:fundId',
    element: (
      <RouteLayout>
        <DomainErrorBoundary domain="fund" showDetails={process.env.NODE_ENV === 'development'}>
          <FundPageWrapper />
        </DomainErrorBoundary>
      </RouteLayout>
    ),
  },
];

