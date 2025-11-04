/**
 * Rates API
 * 
 * All rates-related API methods including:
 * - Risk-Free Rates (CRUD operations)
 * - FX Rates (CRUD operations)
 */

import { ApiClient } from '@/shared/api';
import {
  RiskFreeRate,
  FxRate,
  CreateRiskFreeRateRequest,
  CreateFxRateRequest,
  GetRiskFreeRatesResponse,
  GetRiskFreeRateResponse,
  GetFxRatesResponse,
  GetFxRateResponse,
  GetRiskFreeRatesQueryParams,
  GetFxRatesQueryParams
} from '@/rates/types';

export class RatesApi {
  constructor(private client: ApiClient) {}

  // ============================================================================
  // RISK-FREE RATES
  // ============================================================================

  /**
   * Get all risk-free rates with optional filters.
   */
  async getRiskFreeRates(params: GetRiskFreeRatesQueryParams = {}): Promise<GetRiskFreeRatesResponse> {
    return this.client.get<GetRiskFreeRatesResponse>('/api/risk-free-rates', params);
  }

  /**
   * Get a single risk-free rate by ID.
   */
  async getRiskFreeRate(riskFreeRateId: number): Promise<GetRiskFreeRateResponse> {
    return this.client.get<GetRiskFreeRateResponse>(`/api/risk-free-rates/${riskFreeRateId}`);
  }

  /**
   * Create a new risk-free rate.
   */
  async createRiskFreeRate(data: CreateRiskFreeRateRequest): Promise<RiskFreeRate> {
    return this.client.post<RiskFreeRate>('/api/risk-free-rates', data);
  }

  // Note: UPDATE functionality not yet implemented in backend
  // When backend implements PUT /api/risk-free-rates/<id>, add updateRiskFreeRate() method here

  /**
   * Delete a risk-free rate.
   */
  async deleteRiskFreeRate(riskFreeRateId: number): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(`/api/risk-free-rates/${riskFreeRateId}`);
  }

  // ============================================================================
  // FX RATES
  // ============================================================================

  /**
   * Get all FX rates with optional filters.
   */
  async getFxRates(params: GetFxRatesQueryParams = {}): Promise<GetFxRatesResponse> {
    return this.client.get<GetFxRatesResponse>('/api/fx-rates', params);
  }

  /**
   * Get a single FX rate by ID.
   */
  async getFxRate(fxRateId: number): Promise<GetFxRateResponse> {
    return this.client.get<GetFxRateResponse>(`/api/fx-rates/${fxRateId}`);
  }

  /**
   * Create a new FX rate.
   */
  async createFxRate(data: CreateFxRateRequest): Promise<FxRate> {
    return this.client.post<FxRate>('/api/fx-rates', data);
  }

  // Note: UPDATE functionality not yet implemented in backend
  // When backend implements PUT /api/fx-rates/<id>, add updateFxRate() method here

  /**
   * Delete an FX rate.
   */
  async deleteFxRate(fxRateId: number): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(`/api/fx-rates/${fxRateId}`);
  }
}

