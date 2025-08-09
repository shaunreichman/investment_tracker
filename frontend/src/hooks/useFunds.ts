// Fund-specific Custom Hooks
// This file provides hooks for fund-related API operations

import { useCallback } from 'react';
import { apiClient } from '../services/api';
import { useApiCall, useMutation, useApiCallWithDeps, useConditionalApiCall } from './useApiCall';
import {
  Fund,
  CreateFundData,
  CreateFundEventData,
  CreateTaxStatementData,
  TaxStatement,
  FundEvent,
} from '../types/api';

// ============================================================================
// FUNDS HOOKS
// ============================================================================

/**
 * Hook to get all funds
 */
export function useFunds(options?: { refetchOnWindowFocus?: boolean }) {
  const getFunds = useCallback(() => apiClient.getFunds(), []);
  
  return useApiCall(
    getFunds,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get a single fund by ID
 */
export function useFund(id: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    (fundId: number) => apiClient.getFund(fundId),
    [id],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get fund detail data (fund + events + statistics)
 */
export function useFundDetail(id: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    (fundId: number) => apiClient.getFundDetail(fundId),
    [id],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to create a new fund
 */
export function useCreateFund() {
  return useMutation<CreateFundData, Fund>(
    (data) => apiClient.createFund(data)
  );
}

// ============================================================================
// FUND EVENTS HOOKS
// ============================================================================

/**
 * Hook to get fund events
 */
export function useFundEvents(fundId: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    (fundId: number) => apiClient.getFundEvents(fundId),
    [fundId],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to create a fund event
 */
export function useCreateFundEvent(fundId: number) {
  return useMutation<CreateFundEventData, FundEvent>(
    (data) => apiClient.createFundEvent(fundId, data)
  );
}



/**
 * Hook to delete a fund event
 */
export function useDeleteFundEvent(fundId: number, eventId: number) {
  return useMutation<void, void>(
    () => apiClient.deleteFundEvent(fundId, eventId)
  );
}

// ============================================================================
// TAX STATEMENTS HOOKS
// ============================================================================

/**
 * Hook to create a tax statement
 */
export function useCreateTaxStatement(fundId: number) {
  return useMutation<CreateTaxStatementData, TaxStatement>(
    (data) => apiClient.createTaxStatement(fundId, data)
  );
}

/**
 * Hook to get fund tax statements
 */
export function useFundTaxStatements(fundId: number, options?: { refetchOnWindowFocus?: boolean }) {
  return useApiCallWithDeps(
    (fundId: number) => apiClient.getFundTaxStatements(fundId),
    [fundId],
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

// ============================================================================
// UTILITY HOOKS
// ============================================================================

/**
 * Hook to get fund with conditional loading
 */
export function useFundConditional(id: number | null, options?: { refetchOnWindowFocus?: boolean }) {
  const getFund = useCallback(() => apiClient.getFund(id!), [id]);
  
  return useConditionalApiCall(
    getFund,
    id !== null,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
}

/**
 * Hook to get fund events with conditional loading
 */
export function useFundEventsConditional(fundId: number | null, options?: { refetchOnWindowFocus?: boolean }) {
  const getFundEvents = useCallback(() => apiClient.getFundEvents(fundId!), [fundId]);
  
  return useConditionalApiCall(
    getFundEvents,
    fundId !== null,
    { refetchOnWindowFocus: options?.refetchOnWindowFocus }
  );
} 