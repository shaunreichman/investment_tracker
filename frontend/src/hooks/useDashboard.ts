// Dashboard-specific Custom Hooks
// This file provides hooks for dashboard-related API operations

import { apiClient } from '../services/api';
import { useApiCall } from './useApiCall';
import {} from '../types/api';
import { useCallback } from 'react';

// ============================================================================
// DASHBOARD HOOKS
// ============================================================================

/**
 * Hook to get portfolio summary
 */
export function usePortfolioSummary(options?: { refetchOnWindowFocus?: boolean }) {
  const getPortfolioSummary = useCallback(() => apiClient.getPortfolioSummary(), []);
  
  return useApiCall(
    getPortfolioSummary,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get recent events
 */
export function useRecentEvents(options?: { refetchOnWindowFocus?: boolean }) {
  const getRecentEvents = useCallback(() => apiClient.getRecentEvents(), []);
  
  return useApiCall(
    getRecentEvents,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get dashboard performance data
 */
export function useDashboardPerformance(options?: { refetchOnWindowFocus?: boolean }) {
  const getDashboardPerformance = useCallback(() => apiClient.getDashboardPerformance(), []);
  
  return useApiCall(
    getDashboardPerformance,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get all dashboard data (portfolio summary, funds, recent events, performance)
 */
export function useDashboardData(options?: { refetchOnWindowFocus?: boolean }) {
  const getDashboardData = useCallback(() => apiClient.getDashboardData(), []);
  
  return useApiCall(
    getDashboardData,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
} 