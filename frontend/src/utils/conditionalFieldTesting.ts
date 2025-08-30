import { ConditionalFieldConfig, FieldDependencyResult } from '../hooks/forms/useConditionalFields';

/**
 * Test scenario for conditional field validation
 */
export interface ConditionalFieldTestScenario {
  /** Description of the test scenario */
  description: string;
  /** Form values to test */
  values: Record<string, any>;
  /** Expected field states */
  expectedStates: {
    visible: string[];
    required: string[];
    disabled: string[];
  };
  /** Expected validation errors */
  expectedErrors?: Record<string, string>;
  /** Whether this scenario should pass validation */
  shouldPassValidation: boolean;
}

/**
 * Test result for a conditional field scenario
 */
export interface ConditionalFieldTestResult {
  /** Test scenario description */
  scenario: string;
  /** Whether the test passed */
  passed: boolean;
  /** Actual field states */
  actualStates: {
    visible: string[];
    required: string[];
    disabled: string[];
  };
  /** Expected field states */
  expectedStates: {
    visible: string[];
    required: string[];
    disabled: string[];
  };
  /** Validation errors found */
  validationErrors: Record<string, string>;
  /** Expected validation errors */
  expectedErrors?: Record<string, string>;
  /** Detailed failure reasons */
  failures: string[];
}

/**
 * Test configuration for conditional fields
 */
export interface ConditionalFieldTestConfig {
  /** Field configurations to test */
  fieldConfigs: ConditionalFieldConfig[];
  /** Test scenarios to run */
  scenarios: ConditionalFieldTestScenario[];
  /** Whether to run validation tests */
  runValidation?: boolean;
  /** Custom validation function */
  customValidator?: (field: string, value: any, values: Record<string, any>) => string | undefined;
}

/**
 * Evaluate field dependencies for testing
 */
function evaluateDependencyForTesting(
  dependency: { field: string; value: any; operator?: string },
  values: Record<string, any>
): boolean {
  const actualValue = values[dependency.field];
  const expectedValue = dependency.value;
  const operator = dependency.operator || 'equals';
  
  switch (operator) {
    case 'equals':
      return actualValue === expectedValue;
    case 'not_equals':
      return actualValue !== expectedValue;
    case 'in':
      return Array.isArray(expectedValue) && expectedValue.includes(actualValue);
    case 'not_in':
      return Array.isArray(expectedValue) && !expectedValue.includes(actualValue);
    case 'exists':
      return actualValue !== undefined && actualValue !== null && actualValue !== '';
    case 'not_exists':
      return actualValue === undefined || actualValue === null || actualValue === '';
    default:
      return false;
  }
}

/**
 * Calculate field states for testing
 */
function calculateFieldStatesForTesting(
  fieldConfigs: ConditionalFieldConfig[],
  values: Record<string, any>
): {
  visible: string[];
  required: string[];
  disabled: string[];
} {
  const visible: string[] = [];
  const required: string[] = [];
  const disabled: string[] = [];
  
  fieldConfigs.forEach(config => {
    // Check if field should be visible
    let isVisible = config.visible;
    
    if (config.customVisibility) {
      isVisible = config.customVisibility(values);
    } else if (config.dependencies.length > 0) {
      isVisible = config.dependencies.every(dep => 
        evaluateDependencyForTesting(dep, values)
      );
    }
    
    if (isVisible) {
      visible.push(config.field);
      
      // Check if field should be required
      let isRequired = config.required;
      
      if (config.customRequired) {
        isRequired = config.customRequired(values);
      }
      
      if (isRequired) {
        required.push(config.field);
      }
      
      // Check if field should be disabled
      let isDisabled = config.disabled;
      
      if (config.customDisabled) {
        isDisabled = config.customDisabled(values);
      }
      
      if (isDisabled) {
        disabled.push(config.field);
      }
    }
  });
  
  return { visible, required, disabled };
}

/**
 * Run validation tests for conditional fields
 */
function runValidationTests(
  fieldConfigs: ConditionalFieldConfig[],
  values: Record<string, any>,
  customValidator?: (field: string, value: any, values: Record<string, any>) => string | undefined
): Record<string, string> {
  const errors: Record<string, string> = {};
  
  fieldConfigs.forEach(config => {
    // Only validate visible fields
    let isVisible = config.visible;
    
    if (config.customVisibility) {
      isVisible = config.customVisibility(values);
    } else if (config.dependencies.length > 0) {
      isVisible = config.dependencies.every(dep => 
        evaluateDependencyForTesting(dep, values)
      );
    }
    
    if (isVisible) {
      const value = values[config.field];
      
      // Check if field is required
      let isRequired = config.required;
      
      if (config.customRequired) {
        isRequired = config.customRequired(values);
      }
      
      if (isRequired && (!value || value === '')) {
        errors[config.field] = `${config.field} is required`;
      }
      
      // Run custom validation if provided
      if (customValidator) {
        const customError = customValidator(config.field, value, values);
        if (customError) {
          errors[config.field] = customError;
        }
      }
    }
  });
  
  return errors;
}

/**
 * Test conditional field configurations
 */
export function testConditionalFields(config: ConditionalFieldTestConfig): ConditionalFieldTestResult[] {
  const results: ConditionalFieldTestResult[] = [];
  
  config.scenarios.forEach(scenario => {
    const actualStates = calculateFieldStatesForTesting(config.fieldConfigs, scenario.values);
    
    // Run validation if enabled
    let validationErrors: Record<string, string> = {};
    if (config.runValidation) {
      validationErrors = runValidationTests(
        config.fieldConfigs,
        scenario.values,
        config.customValidator
      );
    }
    
    // Check if test passed
    const visibleMatch = arraysMatch(actualStates.visible, scenario.expectedStates.visible);
    const requiredMatch = arraysMatch(actualStates.required, scenario.expectedStates.required);
    const disabledMatch = arraysMatch(actualStates.disabled, scenario.expectedStates.disabled);
    
    let validationMatch = true;
    if (scenario.expectedErrors) {
      validationMatch = objectsMatch(validationErrors, scenario.expectedErrors);
    }
    
    const passed = visibleMatch && requiredMatch && disabledMatch && validationMatch;
    
    // Collect failure reasons
    const failures: string[] = [];
    if (!visibleMatch) {
      failures.push(`Visible fields mismatch. Expected: [${scenario.expectedStates.visible.join(', ')}], Got: [${actualStates.visible.join(', ')}]`);
    }
    if (!requiredMatch) {
      failures.push(`Required fields mismatch. Expected: [${scenario.expectedStates.required.join(', ')}], Got: [${actualStates.required.join(', ')}]`);
    }
    if (!disabledMatch) {
      failures.push(`Disabled fields mismatch. Expected: [${scenario.expectedStates.disabled.join(', ')}], Got: [${actualStates.disabled.join(', ')}]`);
    }
    if (!validationMatch && scenario.expectedErrors) {
      failures.push(`Validation errors mismatch. Expected: ${JSON.stringify(scenario.expectedErrors)}, Got: ${JSON.stringify(validationErrors)}`);
    }
    
    results.push({
      scenario: scenario.description,
      passed,
      actualStates,
      expectedStates: scenario.expectedStates,
      validationErrors,
      expectedErrors: scenario.expectedErrors || {},
      failures
    });
  });
  
  return results;
}

/**
 * Helper function to check if arrays match (order-independent)
 */
function arraysMatch(a: string[], b: string[]): boolean {
  if (a.length !== b.length) return false;
  const sortedA = [...a].sort();
  const sortedB = [...b].sort();
  return sortedA.every((item, index) => item === sortedB[index]);
}

/**
 * Helper function to check if objects match
 */
function objectsMatch(a: Record<string, any>, b: Record<string, any>): boolean {
  const keysA = Object.keys(a);
  const keysB = Object.keys(b);
  
  if (keysA.length !== keysB.length) return false;
  
  return keysA.every(key => a[key] === b[key]);
}

/**
 * Create test scenarios for fund event forms
 */
export function createFundEventTestScenarios(): ConditionalFieldTestScenario[] {
  return [
    // Basic distribution event
    {
      description: 'Distribution event with INTEREST type',
      values: {
        event_type: 'DISTRIBUTION',
        distribution_type: 'INTEREST',
        sub_distribution_type: 'REGULAR'
      },
      expectedStates: {
        visible: ['distribution_type', 'sub_distribution_type', 'amount', 'has_withholding_tax'],
        required: ['amount'],
        disabled: []
      },
      shouldPassValidation: true
    },
    
    // Distribution event with withholding tax
    {
      description: 'Distribution event with withholding tax enabled',
      values: {
        event_type: 'DISTRIBUTION',
        distribution_type: 'INTEREST',
        sub_distribution_type: 'WITHHOLDING_TAX',
        has_withholding_tax: true
      },
      expectedStates: {
        visible: ['distribution_type', 'sub_distribution_type', 'amount', 'has_withholding_tax', 'withholding_tax_amount', 'withholding_tax_rate'],
        required: ['withholding_tax_amount', 'withholding_tax_rate'],
        disabled: []
      },
      shouldPassValidation: false // Missing required values
    },
    
    // Unit purchase event
    {
      description: 'Unit purchase event',
      values: {
        event_type: 'UNIT_PURCHASE'
      },
      expectedStates: {
        visible: ['amount', 'units_purchased', 'unit_price'],
        required: ['amount', 'units_purchased', 'unit_price'],
        disabled: []
      },
      shouldPassValidation: false // Missing required values
    },
    
    // NAV update event
    {
      description: 'NAV update event',
      values: {
        event_type: 'NAV_UPDATE'
      },
      expectedStates: {
        visible: ['unit_price', 'nav_per_share'],
        required: ['unit_price', 'nav_per_share'],
        disabled: []
      },
      shouldPassValidation: false // Missing required values
    },
    
    // Tax statement event
    {
      description: 'Tax statement event',
      values: {
        event_type: 'TAX_STATEMENT'
      },
      expectedStates: {
        visible: ['financial_year', 'statement_date', 'eofy_debt_interest_deduction_rate', 'interest_received_in_cash', 'interest_receivable_this_fy', 'interest_receivable_prev_fy', 'interest_non_resident_withholding_tax_from_statement', 'dividend_franked_income_amount', 'dividend_unfranked_income_amount', 'capital_gain_income_amount', 'interest_income_tax_rate', 'dividend_franked_income_tax_rate', 'dividend_unfranked_income_tax_rate', 'capital_gain_income_tax_rate'],
        required: [],
        disabled: []
      },
      shouldPassValidation: true
    }
  ];
}

/**
 * Create test scenarios for fund forms
 */
export function createFundTestScenarios(): ConditionalFieldTestScenario[] {
  return [
    // Basic fund creation
    {
      description: 'Basic fund with required fields only',
      values: {
        name: 'Test Fund',
        fund_type: 'PRIVATE_EQUITY',
        tracking_type: 'nav_based',
        currency: 'AUD'
      },
      expectedStates: {
        visible: ['name', 'fund_type', 'tracking_type', 'currency', 'commitment_amount', 'expected_irr', 'expected_duration_months', 'description'],
        required: ['name', 'fund_type', 'tracking_type', 'currency'],
        disabled: []
      },
      shouldPassValidation: true
    },
    
    // Fund with optional fields
    {
      description: 'Fund with all optional fields filled',
      values: {
        name: 'Test Fund',
        fund_type: 'PRIVATE_EQUITY',
        tracking_type: 'nav_based',
        currency: 'AUD',
        commitment_amount: '1000000',
        expected_irr: '15',
        expected_duration_months: '60',
        description: 'Test fund description'
      },
      expectedStates: {
        visible: ['name', 'fund_type', 'tracking_type', 'currency', 'commitment_amount', 'expected_irr', 'expected_duration_months', 'description'],
        required: ['name', 'fund_type', 'tracking_type', 'currency'],
        disabled: []
      },
      shouldPassValidation: true
    }
  ];
}

/**
 * Print test results in a readable format
 */
export function printTestResults(results: ConditionalFieldTestResult[]): void {
  console.log('\n=== Conditional Field Test Results ===\n');
  
  let passedCount = 0;
  let failedCount = 0;
  
  results.forEach(result => {
    if (result.passed) {
      console.log(`✅ ${result.scenario}`);
      passedCount++;
    } else {
      console.log(`❌ ${result.scenario}`);
      console.log(`   Failures: ${result.failures.join(', ')}`);
      failedCount++;
    }
  });
  
  console.log(`\nSummary: ${passedCount} passed, ${failedCount} failed`);
  
  if (failedCount > 0) {
    console.log('\nDetailed failures:');
    results.filter(r => !r.passed).forEach(result => {
      console.log(`\n${result.scenario}:`);
      result.failures.forEach(failure => console.log(`  - ${failure}`));
    });
  }
}
