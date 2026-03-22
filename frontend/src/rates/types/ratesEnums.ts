/**
 * Rates Domain Enums
 * 
 * TypeScript enums matching backend rates domain enums exactly.
 * Source: src/rates/enums/
 * 
 * DO NOT modify these enums without updating the corresponding Python enums.
 * These must remain in sync with the backend for API communication.
 */

// ============================================================================
// FX RATE ENUMS (src/rates/enums/fx_rate_enums.py)
// ============================================================================

/**
 * Sort field enum for FX rates.
 */
export enum SortFieldFxRate {
  DATE = 'DATE',
  FROM_CURRENCY = 'FROM_CURRENCY',
  TO_CURRENCY = 'TO_CURRENCY'
}

// ============================================================================
// RISK FREE RATE ENUMS (src/rates/enums/risk_free_rate_enums.py)
// ============================================================================

/**
 * Risk free rate type enum.
 */
export enum RiskFreeRateType {
  /** Government bond rate */
  GOVERNMENT_BOND = 'GOVERNMENT_BOND',
  /** London Interbank Offered Rate */
  LIBOR = 'LIBOR',
  /** Secured Overnight Financing Rate */
  SOFR = 'SOFR'
}

/**
 * Sort field enum for risk free rates.
 */
export enum SortFieldRiskFreeRate {
  DATE = 'DATE',
  CURRENCY = 'CURRENCY'
}

