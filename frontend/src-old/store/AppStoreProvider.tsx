// App Store Provider Component
// This component provides the centralized state store to the entire application
// and handles automatic migration of existing localStorage data

import React, { createContext, useContext, useEffect, ReactNode } from 'react';
import { useAppStore } from './useAppStore';
import { migrateLocalStorageToStore } from './migration';

// ============================================================================
// CONTEXT TYPES
// ============================================================================

interface AppStoreContextValue {
  store: ReturnType<typeof useAppStore>;
  isInitialized: boolean;
}

const AppStoreContext = createContext<AppStoreContextValue | null>(null);

// ============================================================================
// PROVIDER COMPONENT
// ============================================================================

interface AppStoreProviderProps {
  children: ReactNode;
}

export const AppStoreProvider: React.FC<AppStoreProviderProps> = ({ children }) => {
  const store = useAppStore();
  const [isInitialized, setIsInitialized] = React.useState(false);

  // ============================================================================
  // INITIALIZATION EFFECT
  // ============================================================================
  
  useEffect(() => {
    const initializeStore = async () => {
      try {
        // Migrate existing localStorage data to the centralized store
        migrateLocalStorageToStore();
        
        // Mark store as initialized
        setIsInitialized(true);
        
        console.log('✅ App Store Provider initialized successfully');
      } catch (error) {
        console.error('❌ App Store Provider initialization failed:', error);
        // Still mark as initialized to prevent app from hanging
        setIsInitialized(true);
      }
    };

    initializeStore();
  }, []);

  // ============================================================================
  // CONTEXT VALUE
  // ============================================================================
  
  const contextValue: AppStoreContextValue = {
    store,
    isInitialized,
  };

  // ============================================================================
  // RENDER
  // ============================================================================
  
  return (
    <AppStoreContext.Provider value={contextValue}>
      {children}
    </AppStoreContext.Provider>
  );
};

// ============================================================================
// HOOK FOR USING THE STORE CONTEXT
// ============================================================================

export const useAppStoreContext = (): AppStoreContextValue => {
  const context = useContext(AppStoreContext);
  
  if (!context) {
    throw new Error(
      'useAppStoreContext must be used within an AppStoreProvider'
    );
  }
  
  return context;
};

// ============================================================================
// HOOK FOR ACCESSING THE STORE DIRECTLY
// ============================================================================

export const useAppStoreDirect = () => {
  return useAppStore();
};

// ============================================================================
// HOOK FOR CHECKING STORE INITIALIZATION
// ============================================================================

export const useStoreInitialization = () => {
  const { isInitialized } = useAppStoreContext();
  return isInitialized;
};

// ============================================================================
// EXPORT DEFAULT
// ============================================================================

export default AppStoreProvider;
