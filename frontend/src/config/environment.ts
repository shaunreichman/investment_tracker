// Environment Configuration
// This file provides type-safe environment variable handling

// ============================================================================
// ENVIRONMENT TYPES
// ============================================================================

export interface EnvironmentConfig {
  API_BASE_URL: string;
  NODE_ENV: 'development' | 'production' | 'test';
  REACT_APP_ENVIRONMENT: string;
}

// ============================================================================
// ENVIRONMENT CONFIGURATION
// ============================================================================

export const environment: EnvironmentConfig = {
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001',
  NODE_ENV: (process.env.NODE_ENV as EnvironmentConfig['NODE_ENV']) || 'development',
  REACT_APP_ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT || 'development',
};

// ============================================================================
// VALIDATION
// ============================================================================

export function validateEnvironment(): void {
  const requiredVars = ['API_BASE_URL'] as const;
  
  for (const varName of requiredVars) {
    if (!environment[varName]) {
      throw new Error(`Missing required environment variable: ${varName}`);
    }
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export function isDevelopment(): boolean {
  return environment.NODE_ENV === 'development';
}

export function isProduction(): boolean {
  return environment.NODE_ENV === 'production';
}

export function isTest(): boolean {
  return environment.NODE_ENV === 'test';
}

export function getApiBaseUrl(): string {
  return environment.API_BASE_URL;
}

// ============================================================================
// DEFAULT EXPORT
// ============================================================================

export default environment;
