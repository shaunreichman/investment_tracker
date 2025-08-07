import { ExtendedFundEvent, EventType, DistributionType } from '../../../../types/api';

/**
 * Maps an existing event to its template selection state for edit mode
 * Uses the same logic as the create form to determine template selection
 */
export const mapEventToTemplates = (event: ExtendedFundEvent): {
  eventType: EventType | 'RETURN_OF_CAPITAL' | '';
  distributionType: string;
  subDistributionType: string;
  withholdingAmountType: 'gross' | 'net' | '';
  withholdingTaxType: 'amount' | 'rate' | '';
} => {
  // Map event type
  const eventType = event.event_type;
  
  // Map distribution type
  let distributionType = '';
  let subDistributionType = '';
  
  if (event.event_type === EventType.DISTRIBUTION) {
    // Map distribution type from event
    distributionType = event.distribution_type?.toLowerCase() || '';
    
    // Map sub-distribution type based on distribution type
    if (distributionType === 'interest') {
      // Check if this is a withholding tax event
      if (event.has_withholding_tax) {
        subDistributionType = 'WITHHOLDING_TAX';
      } else {
        subDistributionType = 'REGULAR';
      }
    } else if (distributionType === 'dividend') {
      // Map dividend type based on event data
      if (event.dividend_franked_income_amount && event.dividend_franked_income_amount > 0) {
        subDistributionType = 'DIVIDEND_FRANKED';
      } else {
        subDistributionType = 'DIVIDEND_UNFRANKED';
      }
    }
  }
  
  // Map withholding tax configuration
  let withholdingAmountType: 'gross' | 'net' | '' = '';
  let withholdingTaxType: 'amount' | 'rate' | '' = '';
  
  if (event.event_type === EventType.DISTRIBUTION && 
      event.distribution_type === DistributionType.INTEREST && 
      event.has_withholding_tax) {
    
    // Determine withholding amount type based on available data
    if (event.net_interest && event.amount) {
      // If both net interest and amount are available, determine which was the primary input
      // This is a heuristic - in practice, the form data would tell us
      withholdingAmountType = 'gross'; // Default assumption
    } else if (event.amount) {
      withholdingAmountType = 'gross';
    } else if (event.net_interest) {
      withholdingAmountType = 'net';
    }
    
    // Determine withholding tax type based on available data
    if (event.withholding_amount && event.withholding_rate) {
      // If both amount and rate are available, determine which was the primary input
      withholdingTaxType = 'amount'; // Default assumption
    } else if (event.withholding_amount) {
      withholdingTaxType = 'amount';
    } else if (event.withholding_rate) {
      withholdingTaxType = 'rate';
    }
  }
  
  return {
    eventType,
    distributionType,
    subDistributionType,
    withholdingAmountType,
    withholdingTaxType,
  };
};

/**
 * Maps an existing event to form field values for edit mode
 * Converts event data to form field structure used by create form
 */
export const mapEventToFormData = (event: ExtendedFundEvent): Record<string, string> => {
  const formData: Record<string, string> = {};
  
  // Basic event fields
  if (event.event_date) {
    formData.event_date = event.event_date;
  }
  
  if (event.amount !== null && event.amount !== undefined) {
    formData.amount = event.amount.toString();
  }
  
  if (event.description) {
    formData.description = event.description;
  }
  
  if (event.reference_number) {
    formData.reference_number = event.reference_number;
  }
  
  // NAV-based event fields
  if (event.units_purchased !== null && event.units_purchased !== undefined) {
    formData.units_purchased = event.units_purchased.toString();
  }
  
  if (event.units_sold !== null && event.units_sold !== undefined) {
    formData.units_sold = event.units_sold.toString();
  }
  
  if (event.unit_price !== null && event.unit_price !== undefined) {
    formData.unit_price = event.unit_price.toString();
  }
  
  if (event.brokerage_fee !== null && event.brokerage_fee !== undefined) {
    formData.brokerage_fee = event.brokerage_fee.toString();
  }
  
  if (event.nav_per_share !== null && event.nav_per_share !== undefined) {
    formData.nav_per_share = event.nav_per_share.toString();
  }
  
  // Distribution-specific fields
  if (event.event_type === EventType.DISTRIBUTION) {
    if (event.net_interest !== null && event.net_interest !== undefined) {
      formData.net_interest = event.net_interest.toString();
    }
    
    if (event.withholding_amount !== null && event.withholding_amount !== undefined) {
      formData.withholding_amount = event.withholding_amount.toString();
    }
    
    if (event.withholding_rate !== null && event.withholding_rate !== undefined) {
      formData.withholding_rate = event.withholding_rate.toString();
    }
  }
  
  // Tax statement fields - these are handled separately in the backend
  // The form doesn't directly edit tax statements, so we skip this for now
  
  return formData;
};

/**
 * Determines if an event can be edited (some events may have restrictions)
 */
export const canEditEvent = (event: ExtendedFundEvent): boolean => {
  // For now, all events can be edited
  // This could be expanded to check for business rules
  return true;
};

/**
 * Gets the display label for the current template in edit mode
 */
export const getTemplateDisplayLabel = (event: ExtendedFundEvent): string => {
  const { eventType, distributionType, subDistributionType } = mapEventToTemplates(event);
  
  if (!eventType) {
    return 'Unknown Event Type';
  }
  
  // Map event types to display labels
  const eventTypeLabels: Record<string, string> = {
    'CAPITAL_CALL': 'Capital Call',
    'RETURN_OF_CAPITAL': 'Capital Return',
    'UNIT_PURCHASE': 'Unit Purchase',
    'UNIT_SALE': 'Unit Sale',
    'NAV_UPDATE': 'NAV Update',
    'DISTRIBUTION': 'Distribution',
    'TAX_STATEMENT': 'Tax Statement',
  };
  
  let label = eventTypeLabels[eventType] || eventType;
  
  // Add distribution type for distributions
  if (eventType === 'DISTRIBUTION' && distributionType) {
    const distributionLabels: Record<string, string> = {
      'interest': 'Interest',
      'dividend': 'Dividend',
      'other': 'Other',
    };
    
    const distributionLabel = distributionLabels[distributionType] || distributionType;
    label += ` - ${distributionLabel}`;
    
    // Add sub-distribution type
    if (subDistributionType) {
      const subDistributionLabels: Record<string, string> = {
        'REGULAR': 'Regular',
        'WITHHOLDING_TAX': 'Withholding Tax',
        'DIVIDEND_FRANKED': 'Franked',
        'DIVIDEND_UNFRANKED': 'Unfranked',
      };
      
      const subDistributionLabel = subDistributionLabels[subDistributionType] || subDistributionType;
      label += ` (${subDistributionLabel})`;
    }
  }
  
  return label;
}; 