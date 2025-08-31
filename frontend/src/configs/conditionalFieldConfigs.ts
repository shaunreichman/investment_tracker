import { ConditionalFieldConfig } from '../hooks/forms/useConditionalFields';

/**
 * Conditional field configurations for fund event forms
 * This replaces imperative conditional logic with declarative configurations
 */

// Fund Event Form Conditional Field Configurations
export const fundEventConditionalFields: ConditionalFieldConfig[] = [
  // Distribution Type - only visible for DISTRIBUTION events
  {
    field: 'distribution_type',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'DISTRIBUTION', operator: 'equals' }
    ]
  },

  // Sub-Distribution Type - only visible for specific distribution types
  {
    field: 'sub_distribution_type',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'DISTRIBUTION', operator: 'equals' },
      { field: 'distribution_type', value: ['DIVIDEND_FRANKED', 'DIVIDEND_UNFRANKED', 'INTEREST'], operator: 'in' }
    ]
  },

  // Amount - required for capital events and distributions
  {
    field: 'amount',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: ['CAPITAL_CALL', 'DISTRIBUTION', 'RETURN_OF_CAPITAL'], operator: 'in' }
    ],
    customRequired: (values) => {
      // Skip amount validation for withholding tax scenarios
      if (values.event_type === 'DISTRIBUTION' && 
          values.distribution_type === 'INTEREST' && 
          values.sub_distribution_type === 'WITHHOLDING_TAX') {
        return false;
      }
      return ['CAPITAL_CALL', 'DISTRIBUTION', 'RETURN_OF_CAPITAL'].includes(values.event_type);
    }
  },

  // Units Purchased - only visible for UNIT_PURCHASE events
  {
    field: 'units_purchased',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'UNIT_PURCHASE', operator: 'equals' }
    ]
  },

  // Units Sold - only visible for UNIT_SALE events
  {
    field: 'units_sold',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'UNIT_SALE', operator: 'equals' }
    ]
  },

  // Unit Price - visible for unit transactions and NAV updates
  {
    field: 'unit_price',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: ['UNIT_PURCHASE', 'UNIT_SALE', 'NAV_UPDATE'], operator: 'in' }
    ]
  },

  // NAV Per Share - only visible for NAV_UPDATE events
  {
    field: 'nav_per_share',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'NAV_UPDATE', operator: 'equals' }
    ]
  },

  // Withholding Tax Checkbox - only visible for INTEREST distributions
  {
    field: 'has_withholding_tax',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'DISTRIBUTION', operator: 'equals' },
      { field: 'distribution_type', value: 'INTEREST', operator: 'equals' }
    ]
  },

  // Withholding Tax Amount - only visible when withholding tax is enabled
  {
    field: 'withholding_tax_amount',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'DISTRIBUTION', operator: 'equals' },
      { field: 'distribution_type', value: 'INTEREST', operator: 'equals' },
      { field: 'has_withholding_tax', value: true, operator: 'equals' }
    ]
  },

  // Withholding Tax Rate - only visible when withholding tax is enabled
  {
    field: 'withholding_tax_rate',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'DISTRIBUTION', operator: 'equals' },
      { field: 'distribution_type', value: 'INTEREST', operator: 'equals' },
      { field: 'has_withholding_tax', value: true, operator: 'equals' }
    ]
  },

  // Tax Statement Fields - only visible for TAX_STATEMENT events
  {
    field: 'financial_year',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ]
  },

  {
    field: 'statement_date',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ]
  },

  {
    field: 'eofy_debt_interest_deduction_rate',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ]
  },

  // Tax Statement Income Fields - only visible for TAX_STATEMENT events
  {
    field: 'interest_received_in_cash',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ]
  },

  {
    field: 'interest_receivable_this_fy',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ]
  },

  {
    field: 'interest_receivable_prev_fy',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ]
  },

  {
    field: 'interest_non_resident_withholding_tax_from_statement',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ]
  },

  {
    field: 'dividend_franked_income_amount',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ]
  },

  {
    field: 'dividend_unfranked_income_amount',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ]
  },

  {
    field: 'capital_gain_income_amount',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ]
  },

  // Tax Rate Fields - only visible for TAX_STATEMENT events with income amounts
  {
    field: 'interest_income_tax_rate',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ],
    customRequired: (values) => {
      return values.event_type === 'TAX_STATEMENT' && 
             (values.interest_received_in_cash || values.interest_receivable_this_fy || values.interest_receivable_prev_fy);
    }
  },

  {
    field: 'dividend_franked_income_tax_rate',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ],
    customRequired: (values) => {
      return values.event_type === 'TAX_STATEMENT' && values.dividend_franked_income_amount;
    }
  },

  {
    field: 'dividend_unfranked_income_tax_rate',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ],
    customRequired: (values) => {
      return values.event_type === 'TAX_STATEMENT' && values.dividend_unfranked_income_amount;
    }
  },

  {
    field: 'capital_gain_income_tax_rate',
    visible: true,
    required: false,
    disabled: false,
    dependencies: [
      { field: 'event_type', value: 'TAX_STATEMENT', operator: 'equals' }
    ],
    customRequired: (values) => {
      return values.event_type === 'TAX_STATEMENT' && values.capital_gain_income_amount;
    }
  }
];

// Fund Form Conditional Field Configurations
export const fundConditionalFields: ConditionalFieldConfig[] = [
  // Commitment Amount - optional but should be positive if provided
  {
    field: 'commitment_amount',
    visible: true,
    required: false,
    disabled: false,
    dependencies: []
  },

  // Expected IRR - optional but should be percentage if provided
  {
    field: 'expected_irr',
    visible: true,
    required: false,
    disabled: false,
    dependencies: []
  },

  // Expected Duration - optional but should be positive if provided
  {
    field: 'expected_duration_months',
    visible: true,
    required: false,
    disabled: false,
    dependencies: []
  },

  // Description - always optional
  {
    field: 'description',
    visible: true,
    required: false,
    disabled: false,
    dependencies: []
  }
];

// Entity Form Conditional Field Configurations
export const entityConditionalFields: ConditionalFieldConfig[] = [
  // Entity Type specific fields can be added here
  {
    field: 'tax_file_number',
    visible: true,
    required: false,
    disabled: false,
    dependencies: []
  }
];

// Investment Company Form Conditional Field Configurations
export const investmentCompanyConditionalFields: ConditionalFieldConfig[] = [
  // Company Type specific fields can be added here
  {
    field: 'abn',
    visible: true,
    required: false,
    disabled: false,
    dependencies: []
  }
];

/**
 * Get conditional field configuration for a specific form type
 */
export function getConditionalFieldConfig(formType: 'fund_event' | 'fund' | 'entity' | 'investment_company'): ConditionalFieldConfig[] {
  switch (formType) {
    case 'fund_event':
      return fundEventConditionalFields;
    case 'fund':
      return fundConditionalFields;
    case 'entity':
      return entityConditionalFields;
    case 'investment_company':
      return investmentCompanyConditionalFields;
    default:
      return [];
  }
}

/**
 * Create a custom conditional field configuration
 */
export function createConditionalFieldConfig(
  field: string,
  dependencies: Array<{ field: string; value: any; operator?: 'equals' | 'not_equals' | 'in' | 'not_in' | 'exists' | 'not_exists' }>,
  options: Partial<Omit<ConditionalFieldConfig, 'field' | 'dependencies'>> = {}
): ConditionalFieldConfig {
  return {
    field,
    visible: true,
    required: false,
    disabled: false,
    dependencies: dependencies.map(dep => ({
      field: dep.field,
      value: dep.value,
      operator: dep.operator || 'equals'
    })),
    ...options
  };
}
