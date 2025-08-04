import { ExtendedFundEvent, ExtendedFund } from '../../../types/api';

// ============================================================================
// DEBUG UTILITIES FOR FUND DETAIL TABLE
// ============================================================================

export interface TableDebugInfo {
  totalEvents: number;
  eventTypes: string[];
  fundType: string;
  groupedEvents: { [key: string]: ExtendedFundEvent[] };
  individualEvents: ExtendedFundEvent[];
  showTaxEvents: boolean;
  showNavUpdates: boolean;
  tableStructure: {
    hasEquityColumn: boolean;
    hasNavColumn: boolean;
    hasTaxColumn: boolean;
    hasActionsColumn: boolean;
  };
}

export interface EventGroupingDebugInfo {
  dateGroups: { [key: string]: ExtendedFundEvent[] };
  interestWithholdingPairs: Array<{
    date: string;
    interestEvent: ExtendedFundEvent;
    withholdingEvent: ExtendedFundEvent;
  }>;
  standaloneEvents: ExtendedFundEvent[];
  skippedEvents: ExtendedFundEvent[];
}

/**
 * Debug utility to log comprehensive table state and events
 * Used to understand current table rendering behavior before extraction
 */
export const debugTableRendering = (
  events: ExtendedFundEvent[], 
  fund: ExtendedFund,
  showTaxEvents: boolean = true,
  showNavUpdates: boolean = true
): TableDebugInfo => {
  console.group('🔍 FundDetailTable Debug - Table Rendering');
  
  // Basic event statistics
  const eventTypes = Array.from(new Set(events.map(e => e.event_type)));
  const totalEvents = events.length;
  
  console.log('📊 Event Statistics:', {
    totalEvents,
    eventTypes,
    fundType: fund.tracking_type,
    showTaxEvents,
    showNavUpdates
  });

  // Group events by date for analysis
  const groupedEvents: { [key: string]: ExtendedFundEvent[] } = {};
  events.forEach(event => {
    const dateKey = event.event_date;
    if (!groupedEvents[dateKey]) {
      groupedEvents[dateKey] = [];
    }
    groupedEvents[dateKey].push(event);
  });

  // Analyze table structure based on fund type and toggles
  const tableStructure = {
    hasEquityColumn: true, // Always present
    hasNavColumn: fund.tracking_type === 'nav_based',
    hasTaxColumn: showTaxEvents,
    hasActionsColumn: true // Always present
  };

  console.log('🏗️ Table Structure:', tableStructure);

  // Log event distribution by date
  console.log('📅 Event Distribution by Date:');
  Object.entries(groupedEvents).forEach(([date, dateEvents]) => {
    console.log(`  ${date}: ${dateEvents.length} events - ${dateEvents.map(e => e.event_type).join(', ')}`);
  });

  const debugInfo: TableDebugInfo = {
    totalEvents,
    eventTypes,
    fundType: fund.tracking_type,
    groupedEvents,
    individualEvents: events,
    showTaxEvents,
    showNavUpdates,
    tableStructure
  };

  console.log('📋 Complete Debug Info:', debugInfo);
  console.groupEnd();
  
  return debugInfo;
};

/**
 * Debug utility to compare table rendering before and after changes
 * Used to validate that extraction doesn't change behavior
 */
export const compareTableRendering = (
  before: TableDebugInfo,
  after: TableDebugInfo,
  context: string = 'Table Rendering Comparison'
): boolean => {
  console.group(`🔍 ${context}`);
  
  let isIdentical = true;
  const differences: string[] = [];

  // Compare basic statistics
  if (before.totalEvents !== after.totalEvents) {
    differences.push(`Total events: ${before.totalEvents} → ${after.totalEvents}`);
    isIdentical = false;
  }

  if (before.fundType !== after.fundType) {
    differences.push(`Fund type: ${before.fundType} → ${after.fundType}`);
    isIdentical = false;
  }

  if (before.showTaxEvents !== after.showTaxEvents) {
    differences.push(`Show tax events: ${before.showTaxEvents} → ${after.showTaxEvents}`);
    isIdentical = false;
  }

  if (before.showNavUpdates !== after.showNavUpdates) {
    differences.push(`Show NAV updates: ${before.showNavUpdates} → ${after.showNavUpdates}`);
    isIdentical = false;
  }

  // Compare event types
  const beforeEventTypes = new Set(before.eventTypes);
  const afterEventTypes = new Set(after.eventTypes);
  
  if (beforeEventTypes.size !== afterEventTypes.size) {
    differences.push(`Event type count: ${beforeEventTypes.size} → ${afterEventTypes.size}`);
    isIdentical = false;
  }

  // Compare table structure
  const beforeStructure = JSON.stringify(before.tableStructure);
  const afterStructure = JSON.stringify(after.tableStructure);
  
  if (beforeStructure !== afterStructure) {
    differences.push(`Table structure changed`);
    isIdentical = false;
  }

  if (isIdentical) {
    console.log('✅ Table rendering is identical');
  } else {
    console.warn('⚠️ Table rendering differences detected:', differences);
  }

  console.groupEnd();
  return isIdentical;
};

/**
 * Debug utility to log event grouping logic
 * Used to understand how events are grouped and combined
 */
export const logEventGrouping = (
  events: ExtendedFundEvent[],
  fund: ExtendedFund
): EventGroupingDebugInfo => {
  console.group('🔍 FundDetailTable Debug - Event Grouping');
  
  // Group events by date
  const dateGroups: { [key: string]: ExtendedFundEvent[] } = {};
  events.forEach(event => {
    const dateKey = event.event_date;
    if (!dateGroups[dateKey]) {
      dateGroups[dateKey] = [];
    }
    dateGroups[dateKey].push(event);
  });

  console.log('📅 Events grouped by date:', dateGroups);

  // Find interest + withholding tax pairs
  const interestWithholdingPairs: Array<{
    date: string;
    interestEvent: ExtendedFundEvent;
    withholdingEvent: ExtendedFundEvent;
  }> = [];

  Object.entries(dateGroups).forEach(([date, dateEvents]) => {
    const interestEvent = dateEvents.find(e => 
      e.event_type === 'DISTRIBUTION' && e.distribution_type === 'INTEREST'
    );
    const withholdingEvent = dateEvents.find(e => 
      e.event_type === 'TAX_PAYMENT' && e.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING'
    );

    if (interestEvent && withholdingEvent) {
      interestWithholdingPairs.push({
        date,
        interestEvent,
        withholdingEvent
      });
      console.log(`🔗 Found interest + withholding pair for ${date}:`, {
        interest: interestEvent.amount,
        withholding: withholdingEvent.amount
      });
    }
  });

  // Find standalone events (not part of pairs)
  const allPairedEventIds = new Set(
    interestWithholdingPairs.flatMap(pair => [pair.interestEvent.id, pair.withholdingEvent.id])
  );
  
  const standaloneEvents = events.filter(event => !allPairedEventIds.has(event.id));
  const skippedEvents = events.filter(event => 
    event.event_type === 'TAX_PAYMENT' && 
    event.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING' &&
    !allPairedEventIds.has(event.id)
  );

  console.log('📊 Grouping Analysis:', {
    totalEvents: events.length,
    dateGroups: Object.keys(dateGroups).length,
    interestWithholdingPairs: interestWithholdingPairs.length,
    standaloneEvents: standaloneEvents.length,
    skippedEvents: skippedEvents.length
  });

  const debugInfo: EventGroupingDebugInfo = {
    dateGroups,
    interestWithholdingPairs,
    standaloneEvents,
    skippedEvents
  };

  console.log('📋 Complete Grouping Debug Info:', debugInfo);
  console.groupEnd();
  
  return debugInfo;
};

/**
 * Debug utility to validate table structure integrity
 * Used to ensure table rendering is consistent and complete
 */
export const validateTableStructure = (
  events: ExtendedFundEvent[],
  fund: ExtendedFund,
  showTaxEvents: boolean,
  showNavUpdates: boolean
): { isValid: boolean; issues: string[] } => {
  console.group('🔍 FundDetailTable Debug - Structure Validation');
  
  const issues: string[] = [];
  let isValid = true;

  // Validate fund type consistency
  if (!['nav_based', 'cost_based'].includes(fund.tracking_type)) {
    issues.push(`Invalid fund tracking type: ${fund.tracking_type}`);
    isValid = false;
  }

  // Validate event types
  const validEventTypes = [
    'CAPITAL_CALL', 'RETURN_OF_CAPITAL', 'DISTRIBUTION', 'TAX_PAYMENT',
    'UNIT_PURCHASE', 'UNIT_SALE', 'NAV_UPDATE', 'EOFY_DEBT_COST',
    'DAILY_RISK_FREE_INTEREST_CHARGE', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER'
  ];

  const invalidEventTypes = events
    .map(e => e.event_type)
    .filter(type => !validEventTypes.includes(type));

  if (invalidEventTypes.length > 0) {
    issues.push(`Invalid event types found: ${invalidEventTypes.join(', ')}`);
    isValid = false;
  }

  // Validate tax payment types
  const taxPaymentEvents = events.filter(e => e.event_type === 'TAX_PAYMENT');
  const validTaxPaymentTypes = [
    'EOFY_INTEREST_TAX', 'DIVIDENDS_FRANKED_TAX', 'DIVIDENDS_UNFRANKED_TAX',
    'CAPITAL_GAINS_TAX', 'NON_RESIDENT_INTEREST_WITHHOLDING'
  ];

  const invalidTaxPaymentTypes = taxPaymentEvents
    .map(e => e.tax_payment_type)
    .filter(type => type && !validTaxPaymentTypes.includes(type));

  if (invalidTaxPaymentTypes.length > 0) {
    issues.push(`Invalid tax payment types found: ${invalidTaxPaymentTypes.join(', ')}`);
    isValid = false;
  }

  // Validate distribution types
  const distributionEvents = events.filter(e => e.event_type === 'DISTRIBUTION');
  const validDistributionTypes = ['INTEREST', 'DIVIDEND', 'OTHER'];
  
  const invalidDistributionTypes = distributionEvents
    .map(e => e.distribution_type)
    .filter(type => type && !validDistributionTypes.includes(type));

  if (invalidDistributionTypes.length > 0) {
    issues.push(`Invalid distribution types found: ${invalidDistributionTypes.join(', ')}`);
    isValid = false;
  }

  // Validate NAV-based fund specific requirements
  if (fund.tracking_type === 'nav_based') {
    const navEvents = events.filter(e => e.event_type === 'NAV_UPDATE');
    const unitEvents = events.filter(e => 
      e.event_type === 'UNIT_PURCHASE' || e.event_type === 'UNIT_SALE'
    );

    if (navEvents.length === 0) {
      issues.push('NAV-based fund has no NAV_UPDATE events');
      isValid = false;
    }

    if (unitEvents.length === 0) {
      issues.push('NAV-based fund has no unit purchase/sale events');
      isValid = false;
    }
  }

  // Validate cost-based fund specific requirements
  if (fund.tracking_type === 'cost_based') {
    const capitalEvents = events.filter(e => 
      e.event_type === 'CAPITAL_CALL' || e.event_type === 'RETURN_OF_CAPITAL'
    );

    if (capitalEvents.length === 0) {
      issues.push('Cost-based fund has no capital call/return events');
      isValid = false;
    }
  }

  if (isValid) {
    console.log('✅ Table structure validation passed');
  } else {
    console.warn('⚠️ Table structure validation issues:', issues);
  }

  console.groupEnd();
  
  return { isValid, issues };
};

/**
 * Debug utility to log performance metrics for table rendering
 * Used to monitor performance during extraction process
 */
export const logTablePerformance = (
  events: ExtendedFundEvent[],
  fund: ExtendedFund,
  renderTime?: number
): void => {
  console.group('🔍 FundDetailTable Debug - Performance');
  
  console.log('📊 Performance Metrics:', {
    totalEvents: events.length,
    fundType: fund.tracking_type,
    renderTime: renderTime ? `${renderTime.toFixed(2)}ms` : 'Not measured',
    eventTypeDistribution: events.reduce((acc, event) => {
      acc[event.event_type] = (acc[event.event_type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>)
  });

  // Performance warnings
  if (events.length > 100) {
    console.warn('⚠️ Large dataset detected - consider virtualization for better performance');
  }

  if (renderTime && renderTime > 100) {
    console.warn('⚠️ Slow render time detected - consider optimization');
  }

  console.groupEnd();
};

/**
 * Debug utility to create a comprehensive debug report
 * Used for comprehensive analysis of table state
 */
export const createTableDebugReport = (
  events: ExtendedFundEvent[],
  fund: ExtendedFund,
  showTaxEvents: boolean,
  showNavUpdates: boolean
): void => {
  console.group('📋 FundDetailTable Debug Report');
  
  // Run all debug utilities
  const tableInfo = debugTableRendering(events, fund, showTaxEvents, showNavUpdates);
  const groupingInfo = logEventGrouping(events, fund);
  const validation = validateTableStructure(events, fund, showTaxEvents, showNavUpdates);
  
  console.log('📊 Summary:', {
    totalEvents: events.length,
    fundType: fund.tracking_type,
    showTaxEvents,
    showNavUpdates,
    isValid: validation.isValid,
    issues: validation.issues.length
  });
  
  console.groupEnd();
}; 