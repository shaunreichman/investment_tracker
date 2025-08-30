import { useCallback, useMemo, useState } from 'react';

/**
 * Field dependency configuration
 */
export interface FieldDependency {
  /** Field that this dependency is based on */
  field: string;
  /** Value(s) that trigger this dependency */
  value: any | any[];
  /** Operator for comparison (default: 'equals') */
  operator?: 'equals' | 'not_equals' | 'in' | 'not_in' | 'exists' | 'not_exists';
}

/**
 * Conditional field configuration
 */
export interface ConditionalFieldConfig {
  /** Field name */
  field: string;
  /** Whether the field should be visible */
  visible: boolean;
  /** Whether the field should be required when visible */
  required: boolean;
  /** Whether the field should be disabled when visible */
  disabled: boolean;
  /** Dependencies that control this field's behavior */
  dependencies: FieldDependency[];
  /** Custom visibility function (overrides dependencies if provided) */
  customVisibility?: (values: Record<string, any>) => boolean;
  /** Custom required function (overrides dependencies if provided) */
  customRequired?: (values: Record<string, any>) => boolean;
  /** Custom disabled function (overrides dependencies if provided) */
  customDisabled?: (values: Record<string, any>) => boolean;
}

/**
 * Field dependency evaluation result
 */
export interface FieldDependencyResult {
  /** The field that was evaluated */
  field: string;
  /** Whether the dependency condition is met */
  isMet: boolean;
  /** The actual value that was evaluated */
  actualValue: any;
  /** The expected value(s) for the dependency */
  expectedValue: any | any[];
  /** The operator used for comparison */
  operator: string;
}

/**
 * Configuration for the conditional fields hook
 */
export interface UseConditionalFieldsConfig {
  /** Conditional field configurations */
  fieldConfigs: ConditionalFieldConfig[];
  /** Current form values */
  values: Record<string, any>;
  /** Whether to enable dependency visualization (for debugging) */
  enableVisualization?: boolean;
  /** Whether to enable dependency validation */
  enableValidation?: boolean;
}

/**
 * Return type for the conditional fields hook
 */
export interface UseConditionalFieldsReturn {
  // Field state
  visibleFields: string[];
  requiredFields: string[];
  disabledFields: string[];
  
  // Field queries
  isFieldVisible: (field: string) => boolean;
  isFieldRequired: (field: string) => boolean;
  isFieldDisabled: (field: string) => boolean;
  
  // Dependency analysis
  getFieldDependencies: (field: string) => FieldDependencyResult[];
  getDependentFields: (field: string) => string[];
  
  // Validation helpers
  getConditionalValidationRules: () => Record<string, any>;
  
  // Visualization helpers
  getDependencyGraph: () => Record<string, string[]>;
  
  // Field updates
  updateFieldConfig: (field: string, config: Partial<ConditionalFieldConfig>) => void;
  addFieldConfig: (config: ConditionalFieldConfig) => void;
  removeFieldConfig: (field: string) => void;
}

/**
 * Evaluate a field dependency against current values
 */
function evaluateDependency(
  dependency: FieldDependency,
  values: Record<string, any>
): FieldDependencyResult {
  const actualValue = values[dependency.field];
  const expectedValue = dependency.value;
  const operator = dependency.operator || 'equals';
  
  let isMet = false;
  
  switch (operator) {
    case 'equals':
      isMet = actualValue === expectedValue;
      break;
    case 'not_equals':
      isMet = actualValue !== expectedValue;
      break;
    case 'in':
      isMet = Array.isArray(expectedValue) && expectedValue.includes(actualValue);
      break;
    case 'not_in':
      isMet = Array.isArray(expectedValue) && !expectedValue.includes(actualValue);
      break;
    case 'exists':
      isMet = actualValue !== undefined && actualValue !== null && actualValue !== '';
      break;
    case 'not_exists':
      isMet = actualValue === undefined || actualValue === null || actualValue === '';
      break;
    default:
      isMet = false;
  }
  
  return {
    field: dependency.field,
    isMet,
    actualValue,
    expectedValue,
    operator
  };
}

/**
 * Conditional field management hook that provides declarative field dependency
 * management and replaces imperative conditional logic throughout the codebase.
 * 
 * @param config - Configuration object for conditional fields
 * @returns Conditional field state and management functions
 */
export function useConditionalFields(
  config: UseConditionalFieldsConfig
): UseConditionalFieldsReturn {
  const {
    fieldConfigs,
    values,
    enableVisualization = false,
    enableValidation = false
  } = config;

  // Local state for dynamic field configurations
  const [localFieldConfigs, setLocalFieldConfigs] = useState<ConditionalFieldConfig[]>(fieldConfigs);

  // Merge local and prop configurations
  const allFieldConfigs = useMemo(() => {
    const merged = [...fieldConfigs];
    
    // Apply local overrides
    localFieldConfigs.forEach(localConfig => {
      const existingIndex = merged.findIndex(config => config.field === localConfig.field);
      if (existingIndex >= 0) {
        // Update existing config
        merged[existingIndex] = { ...merged[existingIndex], ...localConfig };
      } else {
        // Add new config
        merged.push(localConfig);
      }
    });
    
    return merged;
  }, [fieldConfigs, localFieldConfigs]);

  // Calculate visible fields based on dependencies
  const visibleFields = useMemo(() => {
    return allFieldConfigs
      .filter(config => {
        if (config.customVisibility) {
          return config.customVisibility(values);
        }
        
        if (config.dependencies.length === 0) {
          return config.visible;
        }
        
        return config.dependencies.every(dependency => 
          evaluateDependency(dependency, values).isMet
        );
      })
      .map(config => config.field);
  }, [allFieldConfigs, values]);

  // Calculate required fields based on dependencies
  const requiredFields = useMemo(() => {
    return allFieldConfigs
      .filter(config => {
        // Check if field should be visible first
        let isVisible = config.visible;
        
        if (config.customVisibility) {
          isVisible = config.customVisibility(values);
        } else if (config.dependencies.length > 0) {
          isVisible = config.dependencies.every(dependency => 
            evaluateDependency(dependency, values).isMet
          );
        }
        
        if (!isVisible) {
          return false;
        }
        
        if (config.customRequired) {
          return config.customRequired(values);
        }
        
        return config.required;
      })
      .map(config => config.field);
  }, [allFieldConfigs, values]);

  // Calculate disabled fields based on dependencies
  const disabledFields = useMemo(() => {
    return allFieldConfigs
      .filter(config => {
        // Check if field should be visible first
        let isVisible = config.visible;
        
        if (config.customVisibility) {
          isVisible = config.customVisibility(values);
        } else if (config.dependencies.length > 0) {
          isVisible = config.dependencies.every(dependency => 
            evaluateDependency(dependency, values).isMet
          );
        }
        
        if (!isVisible) {
          return false;
        }
        
        if (config.customDisabled) {
          return config.customDisabled(values);
        }
        
        return config.disabled;
      })
      .map(config => config.field);
  }, [allFieldConfigs, values]);

  // Check if a specific field is visible
  const isFieldVisible = useCallback((field: string): boolean => {
    return visibleFields.includes(field);
  }, [visibleFields]);

  // Check if a specific field is required
  const isFieldRequired = useCallback((field: string): boolean => {
    return requiredFields.includes(field);
  }, [requiredFields]);

  // Check if a specific field is disabled
  const isFieldDisabled = useCallback((field: string): boolean => {
    return disabledFields.includes(field);
  }, [disabledFields]);

  // Get dependency evaluation results for a field
  const getFieldDependencies = useCallback((field: string): FieldDependencyResult[] => {
    const config = allFieldConfigs.find(c => c.field === field);
    if (!config) return [];
    
    return config.dependencies.map(dependency => 
      evaluateDependency(dependency, values)
    );
  }, [allFieldConfigs, values]);

  // Get fields that depend on a specific field
  const getDependentFields = useCallback((field: string): string[] => {
    return allFieldConfigs
      .filter(config => 
        config.dependencies.some(dep => dep.field === field)
      )
      .map(config => config.field);
  }, [allFieldConfigs]);

  // Get conditional validation rules (respects field visibility)
  const getConditionalValidationRules = useCallback(() => {
    const rules: Record<string, any> = {};
    
    allFieldConfigs.forEach(config => {
      if (isFieldVisible(config.field)) {
        // Add validation rule based on field requirements
        if (isFieldRequired(config.field)) {
          rules[config.field] = (value: any) => {
            if (!value || value === '') {
              return `${config.field} is required`;
            }
            return undefined;
          };
        }
      }
    });
    
    return rules;
  }, [allFieldConfigs, isFieldVisible, isFieldRequired]);

  // Get dependency graph for visualization
  const getDependencyGraph = useCallback(() => {
    const graph: Record<string, string[]> = {};
    
    allFieldConfigs.forEach(config => {
      graph[config.field] = config.dependencies.map(dep => dep.field);
    });
    
    return graph;
  }, [allFieldConfigs]);

  // Update field configuration
  const updateFieldConfig = useCallback((field: string, updates: Partial<ConditionalFieldConfig>) => {
    setLocalFieldConfigs(prev => {
      const existingConfig = prev.find(config => config.field === field);
      if (existingConfig) {
        return prev.map(config => 
          config.field === field 
            ? { ...config, ...updates }
            : config
        );
      } else {
        // If field doesn't exist in local configs, add it
        const newConfig: ConditionalFieldConfig = {
          field,
          visible: true,
          required: false,
          disabled: false,
          dependencies: [],
          ...updates
        };
        return [...prev, newConfig];
      }
    });
  }, []);

  // Add new field configuration
  const addFieldConfig = useCallback((config: ConditionalFieldConfig) => {
    setLocalFieldConfigs(prev => [...prev, config]);
  }, []);

  // Remove field configuration
  const removeFieldConfig = useCallback((field: string) => {
    setLocalFieldConfigs(prev => {
      // Mark the field as removed by setting it to invisible
      const existingConfig = prev.find(config => config.field === field);
      if (existingConfig) {
        return prev.map(config => 
          config.field === field 
            ? { ...config, visible: false, required: false, disabled: false }
            : config
        );
      } else {
        // If not in local configs, add a removal marker
        const removalConfig: ConditionalFieldConfig = {
          field,
          visible: false,
          required: false,
          disabled: false,
          dependencies: []
        };
        return [...prev, removalConfig];
      }
    });
  }, []);

  return {
    // Field state
    visibleFields,
    requiredFields,
    disabledFields,
    
    // Field queries
    isFieldVisible,
    isFieldRequired,
    isFieldDisabled,
    
    // Dependency analysis
    getFieldDependencies,
    getDependentFields,
    
    // Validation helpers
    getConditionalValidationRules,
    
    // Visualization helpers
    getDependencyGraph,
    
    // Field updates
    updateFieldConfig,
    addFieldConfig,
    removeFieldConfig
  };
}
