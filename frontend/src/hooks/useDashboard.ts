// Dashboard-specific Custom Hooks
// This file provides hooks for dashboard-related API operations

import { apiClient } from '../services/api';
import { useApiCall } from './useApiCall';
import {
  PortfolioSummary,
  DashboardData,
  FundEventListResponse,
} from '../types/api';

// ============================================================================
// DASHBOARD HOOKS
// ============================================================================

/**
 * Hook to get portfolio summary
 */
export function usePortfolioSummary(options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCall(
    () => apiClient.getPortfolioSummary(),
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get recent events
 */
export function useRecentEvents(options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCall(
    () => apiClient.getRecentEvents(),
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get dashboard performance data
 */
export function useDashboardPerformance(options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCall(
    () => apiClient.getDashboardPerformance(),
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get all dashboard data (portfolio summary, funds, recent events, performance)
 */
export function useDashboardData(options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCall(
    () => apiClient.getDashboardData(),
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
} 