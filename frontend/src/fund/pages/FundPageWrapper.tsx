/**
 * FundPageWrapper Component
 * 
 * Wrapper component that provides a key prop to FundPage based on fundId.
 * This ensures the component remounts when navigating between different funds,
 * resetting all local state (modals, dialogs, etc.).
 * 
 * Usage:
 *   Used in fund/routes.tsx for the /funds/:fundId route.
 */

import React from 'react';
import { useParams } from 'react-router-dom';
import { FundPage } from './FundPage';

/**
 * Wrapper component to provide key for FundPage.
 * Forces remount when fundId changes, ensuring state resets.
 */
export const FundPageWrapper: React.FC = () => {
  const { fundId } = useParams<{ fundId: string }>();
  return <FundPage key={fundId} />;
};

