/**
 * CompanyPageWrapper Component
 * 
 * Wrapper component that provides a key prop to CompanyPage based on companyId.
 * This ensures the component remounts when navigating between different companies,
 * resetting all local state (modals, dialogs, tabs, etc.).
 * 
 * Usage:
 *   Used in company/routes.tsx for the /companies/:companyId route.
 */

import React from 'react';
import { useParams } from 'react-router-dom';
import CompanyPage from './CompanyPage';

/**
 * Wrapper component to provide key for CompanyPage.
 * Forces remount when companyId changes, ensuring state resets.
 */
export const CompanyPageWrapper: React.FC = () => {
  const { companyId } = useParams<{ companyId: string }>();
  return <CompanyPage key={companyId} />;
};

