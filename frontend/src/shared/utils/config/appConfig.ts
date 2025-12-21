/**
 * Shared application configuration constants.
 *
 * These SYSTEM values underpin API behaviour, form UX, and persisted
 * preferences. Keep overrides centralized to avoid drift across domains.
 */
export const API_CONFIG = {
  TIMEOUT: 30_000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1_000,
  CACHE_DURATION: 5 * 60 * 1_000,
} as const;

export const FORM_CONFIG = {
  DEBOUNCE_DELAY: 300,
  AUTO_SAVE_DELAY: 2_000,
  MAX_FILE_SIZE: 5 * 1024 * 1024,
  ALLOWED_FILE_TYPES: ['.csv', '.xlsx', '.xls'],
} as const;

export const STORAGE_KEYS = {
  SIDEBAR_VISIBLE: 'fundDetailSidebarVisible',
  USER_PREFERENCES: 'userPreferences',
  THEME: 'theme',
  LANGUAGE: 'language',
} as const;

