// Store Index - Centralized State Management Exports
// This file provides a clean interface for importing all store-related functionality

// ============================================================================
// MAIN STORE
// ============================================================================

export { useAppStore } from './useAppStore';
export type { 
  AppStoreState, 
  UserPreferences, 
  UIState, 
  AppState 
} from './useAppStore';

// ============================================================================
// SELECTOR HOOKS
// ============================================================================

export { 
  useUserPreferences,
  useSidebarState,
  useTableFilters,
  useLoadingState,
  useErrorState
} from './useAppStore';

// ============================================================================
// PROVIDER COMPONENT
// ============================================================================

export { 
  AppStoreProvider,
  useAppStoreContext,
  useAppStoreDirect,
  useStoreInitialization
} from './AppStoreProvider';

// ============================================================================
// MIGRATION UTILITIES
// ============================================================================

export {
  migrateLocalStorageToStore,
  getLegacyStorageValue,
  setLegacyStorageValue,
  removeLegacyStorageItem,
  getMigrationStatus,
  isMigrationComplete,
  getMigrationSummary,
  cleanupLegacyStorage,
  exportMigrationStatus
} from './migration';

// ============================================================================
// STORE CONSTANTS
// ============================================================================

export const STORE_KEYS = {
  PERSISTENCE_KEY: 'investment-tracker-app-store',
  MIGRATION_KEYS: [
    'fundDetailSidebarVisible',
    'userPreferences',
    'theme',
    'language'
  ] as const,
} as const;

// ============================================================================
// STORE TYPES
// ============================================================================

export type StoreKey = typeof STORE_KEYS.MIGRATION_KEYS[number];
export type SidebarKey = 'fundDetail' | 'dashboard' | 'companies';
export type Theme = 'light' | 'dark';
export type DateFormat = 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';
export type NumberFormat = 'en-US' | 'en-GB' | 'custom';

