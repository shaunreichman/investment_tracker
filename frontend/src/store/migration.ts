// State Management Migration Utility
// This utility helps migrate existing localStorage usage to the centralized Zustand store
// and provides backward compatibility during the transition period

import { useAppStore } from './useAppStore';

// ============================================================================
// MIGRATION MAP
// ============================================================================

/**
 * Maps old localStorage keys to new store properties
 */
const STORAGE_MIGRATION_MAP = {
  'fundDetailSidebarVisible': 'sidebars.fundDetail',
  'userPreferences': 'preferences',
  'theme': 'theme',
  'language': 'language',
  // Add more mappings as needed
} as const;

// ============================================================================
// MIGRATION FUNCTIONS
// ============================================================================

/**
 * Migrates existing localStorage data to the centralized store
 * This should be called once when the app initializes
 */
export const migrateLocalStorageToStore = (): void => {
  const store = useAppStore.getState();
  
  try {
    // Migrate sidebar visibility
    const fundDetailSidebar = localStorage.getItem('fundDetailSidebarVisible');
    if (fundDetailSidebar !== null) {
      const isVisible = JSON.parse(fundDetailSidebar);
      store.setSidebarVisible('fundDetail', isVisible);
      
      // Remove old localStorage item after successful migration
      localStorage.removeItem('fundDetailSidebarVisible');
    }

    // Migrate theme preference
    const theme = localStorage.getItem('theme');
    if (theme !== null) {
      const parsedTheme = JSON.parse(theme);
      if (parsedTheme === 'light' || parsedTheme === 'dark') {
        store.updatePreferences({ theme: parsedTheme });
        localStorage.removeItem('theme');
      }
    }

    // Migrate language preference
    const language = localStorage.getItem('language');
    if (language !== null) {
      const parsedLanguage = JSON.parse(language);
      if (typeof parsedLanguage === 'string') {
        store.updatePreferences({ language: parsedLanguage });
        localStorage.removeItem('language');
      }
    }

    // Migrate user preferences object
    const userPreferences = localStorage.getItem('userPreferences');
    if (userPreferences !== null) {
      try {
        const parsed = JSON.parse(userPreferences);
        if (parsed && typeof parsed === 'object') {
          // Migrate known preferences
          if (parsed.currency && typeof parsed.currency === 'string') {
            store.updatePreferences({ defaultCurrency: parsed.currency });
          }
          if (parsed.dateFormat && typeof parsed.dateFormat === 'string') {
            store.updatePreferences({ dateFormat: parsed.dateFormat });
          }
          if (parsed.numberFormat && typeof parsed.numberFormat === 'string') {
            store.updatePreferences({ numberFormat: parsed.numberFormat });
          }
          
          localStorage.removeItem('userPreferences');
        }
      } catch (error) {
        console.warn('Failed to parse userPreferences from localStorage:', error);
      }
    }

    console.log('✅ LocalStorage migration completed successfully');
  } catch (error) {
    console.error('❌ LocalStorage migration failed:', error);
  }
};

/**
 * Provides backward compatibility for components still using localStorage
 * This should be used during the transition period
 */
export const getLegacyStorageValue = <T>(key: string, defaultValue: T): T => {
  try {
    const item = localStorage.getItem(key);
    if (item !== null) {
      return JSON.parse(item);
    }
  } catch (error) {
    console.warn(`Failed to parse localStorage item '${key}':`, error);
  }
  return defaultValue;
};

/**
 * Sets a value in both the centralized store and localStorage for backward compatibility
 * This should be used during the transition period
 */
export const setLegacyStorageValue = <T>(key: string, value: T, storeSetter?: () => void): void => {
  try {
    // Set in localStorage for backward compatibility
    localStorage.setItem(key, JSON.stringify(value));
    
    // Also update the centralized store if a setter is provided
    if (storeSetter) {
      storeSetter();
    }
  } catch (error) {
    console.error(`Failed to set localStorage item '${key}':`, error);
  }
};

/**
 * Removes a legacy localStorage item
 */
export const removeLegacyStorageItem = (key: string): void => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error(`Failed to remove localStorage item '${key}':`, error);
  }
};

// ============================================================================
// MIGRATION STATUS TRACKING
// ============================================================================

/**
 * Tracks migration progress for different localStorage keys
 */
export const getMigrationStatus = (): Record<string, boolean> => {
  const status: Record<string, boolean> = {};
  
  Object.keys(STORAGE_MIGRATION_MAP).forEach((oldKey) => {
    status[oldKey] = localStorage.getItem(oldKey) === null;
  });
  
  return status;
};

/**
 * Checks if migration is complete
 */
export const isMigrationComplete = (): boolean => {
  const status = getMigrationStatus();
  return Object.values(status).every(Boolean);
};

/**
 * Gets a summary of migration status
 */
export const getMigrationSummary = (): {
  total: number;
  migrated: number;
  remaining: string[];
} => {
  const status = getMigrationStatus();
  const total = Object.keys(status).length;
  const migrated = Object.values(status).filter(Boolean).length;
  const remaining = Object.keys(status).filter(key => !status[key]);
  
  return { total, migrated, remaining };
};

// ============================================================================
// CLEANUP FUNCTIONS
// ============================================================================

/**
 * Cleans up all legacy localStorage items after migration is complete
 * This should be called after confirming all components are using the new store
 */
export const cleanupLegacyStorage = (): void => {
  if (!isMigrationComplete()) {
    console.warn('Cannot cleanup legacy storage: migration not complete');
    return;
  }
  
  try {
    Object.keys(STORAGE_MIGRATION_MAP).forEach((key) => {
      localStorage.removeItem(key);
    });
    console.log('✅ Legacy localStorage cleanup completed');
  } catch (error) {
    console.error('❌ Legacy localStorage cleanup failed:', error);
  }
};

/**
 * Exports current migration status for debugging
 */
export const exportMigrationStatus = (): string => {
  const summary = getMigrationSummary();
  const status = getMigrationStatus();
  
  return JSON.stringify({
    summary,
    status,
    timestamp: new Date().toISOString(),
  }, null, 2);
};

