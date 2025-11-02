// Centralized Application State Store
// This store provides enterprise-grade state management for the entire application
// with automatic persistence, type safety, and centralized localStorage management

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// ============================================================================
// TYPES
// ============================================================================

/**
 * User preferences that should persist across sessions
 */
export interface UserPreferences {
  /** Theme preference (light/dark) */
  theme: 'light' | 'dark';
  /** Language preference */
  language: string;
  /** Default currency for displays */
  defaultCurrency: string;
  /** Date format preference */
  dateFormat: 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';
  /** Number format preference */
  numberFormat: 'en-US' | 'en-GB' | 'custom';
}

/**
 * UI state that should persist across sessions
 */
export interface UIState {
  /** Sidebar visibility states for different views */
  sidebars: {
    fundDetail: boolean;
    dashboard: boolean;
    companies: boolean;
  };
  /** Table filter preferences */
  tableFilters: {
    showTaxEvents: boolean;
    showNavUpdates: boolean;
    showDistributions: boolean;
    defaultDateRange: string;
  };
  /** Modal states and preferences */
  modals: {
    lastOpened: string | null;
    rememberSize: boolean;
    defaultPosition: { x: number; y: number };
  };
}

/**
 * Application state that doesn't need persistence
 */
export interface AppState {
  /** Current loading states */
  loading: {
    global: boolean;
    api: boolean;
    navigation: boolean;
  };
  /** Current error states */
  errors: {
    global: string | null;
    api: string | null;
    validation: string | null;
  };
  /** Navigation state */
  navigation: {
    currentRoute: string;
    previousRoute: string | null;
    breadcrumbs: string[];
  };
}

/**
 * Complete store state interface
 */
export interface AppStoreState extends UserPreferences, UIState, AppState {
  // Actions
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
  updateUIState: (uiState: Partial<UIState>) => void;
  updateAppState: (appState: Partial<AppState>) => void;
  
  // Sidebar actions
  toggleSidebar: (sidebarKey: keyof UIState['sidebars']) => void;
  setSidebarVisible: (sidebarKey: keyof UIState['sidebars'], visible: boolean) => void;
  
  // Table filter actions
  updateTableFilters: (filters: Partial<UIState['tableFilters']>) => void;
  resetTableFilters: () => void;
  
  // Loading actions
  setGlobalLoading: (loading: boolean) => void;
  setApiLoading: (loading: boolean) => void;
  
  // Error actions
  setGlobalError: (error: string | null) => void;
  setApiError: (error: string | null) => void;
  clearErrors: () => void;
  
  // Navigation actions
  updateNavigation: (route: string) => void;
  
  // Utility actions
  resetToDefaults: () => void;
  exportPreferences: () => string;
  importPreferences: (preferences: string) => void;
}

// ============================================================================
// DEFAULT VALUES
// ============================================================================

const DEFAULT_PREFERENCES: UserPreferences = {
  theme: 'light',
  language: 'en',
  defaultCurrency: 'USD',
  dateFormat: 'MM/DD/YYYY',
  numberFormat: 'en-US',
};

const DEFAULT_UI_STATE: UIState = {
  sidebars: {
    fundDetail: true,
    dashboard: true,
    companies: true,
  },
  tableFilters: {
    showTaxEvents: true,
    showNavUpdates: true,
    showDistributions: true,
    defaultDateRange: '1Y',
  },
  modals: {
    lastOpened: null,
    rememberSize: true,
    defaultPosition: { x: 100, y: 100 },
  },
};

const DEFAULT_APP_STATE: AppState = {
  loading: {
    global: false,
    api: false,
    navigation: false,
  },
  errors: {
    global: null,
    api: null,
    validation: null,
  },
  navigation: {
    currentRoute: '/',
    previousRoute: null,
    breadcrumbs: ['Dashboard'],
  },
};

// ============================================================================
// STORE CREATION
// ============================================================================

export const useAppStore = create<AppStoreState>()(
  persist(
    (set, get) => ({
      // Initial state
      ...DEFAULT_PREFERENCES,
      ...DEFAULT_UI_STATE,
      ...DEFAULT_APP_STATE,

      // ============================================================================
      // PREFERENCE ACTIONS
      // ============================================================================
      
      updatePreferences: (preferences: Partial<UserPreferences>) => {
        set((state) => ({
          ...state,
          ...preferences,
        }));
      },

      // ============================================================================
      // UI STATE ACTIONS
      // ============================================================================
      
      updateUIState: (uiState: Partial<UIState>) => {
        set((state) => ({
          ...state,
          ...uiState,
        }));
      },

      updateAppState: (appState: Partial<AppState>) => {
        set((state) => ({
          ...state,
          ...appState,
        }));
      },

      // ============================================================================
      // SIDEBAR ACTIONS
      // ============================================================================
      
      toggleSidebar: (sidebarKey: keyof UIState['sidebars']) => {
        set((state) => ({
          sidebars: {
            ...state.sidebars,
            [sidebarKey]: !state.sidebars[sidebarKey],
          },
        }));
      },

      setSidebarVisible: (sidebarKey: keyof UIState['sidebars'], visible: boolean) => {
        set((state) => ({
          sidebars: {
            ...state.sidebars,
            [sidebarKey]: visible,
          },
        }));
      },

      // ============================================================================
      // TABLE FILTER ACTIONS
      // ============================================================================
      
      updateTableFilters: (filters: Partial<UIState['tableFilters']>) => {
        set((state) => ({
          tableFilters: {
            ...state.tableFilters,
            ...filters,
          },
        }));
      },

      resetTableFilters: () => {
        set((state) => ({
          tableFilters: DEFAULT_UI_STATE.tableFilters,
        }));
      },

      // ============================================================================
      // LOADING ACTIONS
      // ============================================================================
      
      setGlobalLoading: (loading: boolean) => {
        set((state) => ({
          loading: {
            ...state.loading,
            global: loading,
          },
        }));
      },

      setApiLoading: (loading: boolean) => {
        set((state) => ({
          loading: {
            ...state.loading,
            api: loading,
          },
        }));
      },

      // ============================================================================
      // ERROR ACTIONS
      // ============================================================================
      
      setGlobalError: (error: string | null) => {
        set((state) => ({
          errors: {
            ...state.errors,
            global: error,
          },
        }));
      },

      setApiError: (error: string | null) => {
        set((state) => ({
          errors: {
            ...state.errors,
            api: error,
          },
        }));
      },

      clearErrors: () => {
        set((state) => ({
          errors: {
            global: null,
            api: null,
            validation: null,
          },
        }));
      },

      // ============================================================================
      // NAVIGATION ACTIONS
      // ============================================================================
      
      updateNavigation: (route: string) => {
        const currentRoute = get().navigation.currentRoute;
        set((state) => ({
          navigation: {
            ...state.navigation,
            previousRoute: currentRoute,
            currentRoute: route,
            breadcrumbs: [...state.navigation.breadcrumbs, route].slice(-5), // Keep last 5
          },
        }));
      },

      // ============================================================================
      // UTILITY ACTIONS
      // ============================================================================
      
      resetToDefaults: () => {
        set({
          ...DEFAULT_PREFERENCES,
          ...DEFAULT_UI_STATE,
          ...DEFAULT_APP_STATE,
        });
      },

      exportPreferences: () => {
        const state = get();
        const exportableState = {
          preferences: {
            theme: state.theme,
            language: state.language,
            defaultCurrency: state.defaultCurrency,
            dateFormat: state.dateFormat,
            numberFormat: state.numberFormat,
          },
          uiState: {
            sidebars: state.sidebars,
            tableFilters: state.tableFilters,
            modals: state.modals,
          },
        };
        return JSON.stringify(exportableState, null, 2);
      },

      importPreferences: (preferences: string) => {
        try {
          const imported = JSON.parse(preferences);
          if (imported.preferences) {
            set((state) => ({
              ...state,
              ...imported.preferences,
              ...imported.uiState,
            }));
          }
        } catch (error) {
          console.error('Failed to import preferences:', error);
          throw new Error('Invalid preferences format');
        }
      },
    }),
    {
      name: 'investment-tracker-app-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // Only persist user preferences and UI state, not app state
        theme: state.theme,
        language: state.language,
        defaultCurrency: state.defaultCurrency,
        dateFormat: state.dateFormat,
        numberFormat: state.numberFormat,
        sidebars: state.sidebars,
        tableFilters: state.tableFilters,
        modals: state.modals,
      }),
    }
  )
);

// ============================================================================
// SELECTOR HOOKS FOR COMMON USE CASES
// ============================================================================

/**
 * Hook for accessing user preferences
 */
export const useUserPreferences = () => {
  const store = useAppStore();
  return {
    theme: store.theme,
    language: store.language,
    defaultCurrency: store.defaultCurrency,
    dateFormat: store.dateFormat,
    numberFormat: store.numberFormat,
    updatePreferences: store.updatePreferences,
  };
};

/**
 * Hook for accessing sidebar state
 */
export const useSidebarState = (sidebarKey: keyof UIState['sidebars']) => {
  const store = useAppStore();
  return {
    isVisible: store.sidebars[sidebarKey],
    toggle: () => store.toggleSidebar(sidebarKey),
    setVisible: (visible: boolean) => store.setSidebarVisible(sidebarKey, visible),
  };
};

/**
 * Hook for accessing table filters
 */
export const useTableFilters = () => {
  const store = useAppStore();
  return {
    filters: store.tableFilters,
    updateFilters: store.updateTableFilters,
    resetFilters: store.resetTableFilters,
  };
};

/**
 * Hook for accessing loading states
 */
export const useLoadingState = () => {
  const store = useAppStore();
  return {
    global: store.loading.global,
    api: store.loading.api,
    navigation: store.loading.navigation,
    setGlobalLoading: store.setGlobalLoading,
    setApiLoading: store.setApiLoading,
  };
};

/**
 * Hook for accessing error states
 */
export const useErrorState = () => {
  const store = useAppStore();
  return {
    global: store.errors.global,
    api: store.errors.api,
    validation: store.errors.validation,
    setGlobalError: store.setGlobalError,
    setApiError: store.setApiError,
    clearErrors: store.clearErrors,
  };
};
