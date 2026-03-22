/**
 * Entity Domain Routes
 * 
 * Defines React Router routes for the entity domain.
 * 
 * Usage:
 *   import { entityRoutes } from '@/entity/routes';
 */

import { RouteObject } from 'react-router-dom';
import RouteLayout from '@/shared/ui/layout/RouteLayout';
import { DomainErrorBoundary } from '@/shared/ui/feedback';
import { AllEntitiesPage } from './pages';

/**
 * Entity domain routes.
 * 
 * Defines routes for entity management pages.
 */
export const entityRoutes: RouteObject[] = [
  {
    path: '/entities',
    element: (
      <RouteLayout>
        <DomainErrorBoundary domain="entity" showDetails={process.env.NODE_ENV === 'development'}>
          <AllEntitiesPage />
        </DomainErrorBoundary>
      </RouteLayout>
    ),
  },
];

