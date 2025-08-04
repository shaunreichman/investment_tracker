import { useMemo } from 'react';
import { ExtendedFundEvent, ExtendedFund } from '../../../types/api';
import { logEventGrouping } from './debug';

// ============================================================================
// EVENT GROUPING HOOK
// ============================================================================

export interface GroupedEvent {
  date: string;
  events: ExtendedFundEvent[];
  hasInterestWithholdingPair: boolean;
  interestEvent?: ExtendedFundEvent;
  withholdingEvent?: ExtendedFundEvent;
  otherEvents: ExtendedFundEvent[];
}

export interface EventGroupingResult {
  groupedEvents: GroupedEvent[];
  individualEvents: ExtendedFundEvent[];
  totalEvents: number;
  totalGroups: number;
  interestWithholdingPairs: number;
}

/**
 * Custom hook to group events by date and handle interest + withholding tax combinations
 * Extracted from FundDetail.tsx lines 650-680 for reusability and testing
 */
export const useEventGrouping = (
  events: ExtendedFundEvent[],
  fund: ExtendedFund,
  showTaxEvents: boolean = true,
  showNavUpdates: boolean = true
): EventGroupingResult => {
  
  return useMemo(() => {
    // Debug logging in development mode
    if (process.env.NODE_ENV === 'development') {
      logEventGrouping(events, fund);
    }

    // Group events by date
    const groupedByDate: { [key: string]: ExtendedFundEvent[] } = {};
    
    events.forEach(event => {
      const dateKey = event.event_date;
      if (!groupedByDate[dateKey]) {
        groupedByDate[dateKey] = [];
      }
      groupedByDate[dateKey].push(event);
    });

    // Process each date group to find interest + withholding pairs
    const groupedEvents: GroupedEvent[] = [];
    const individualEvents: ExtendedFundEvent[] = [];
    let interestWithholdingPairs = 0;

    Object.entries(groupedByDate).forEach(([date, dateEvents]) => {
      // Find interest distribution and related withholding tax for this date
      const interestEvent = dateEvents.find(e => 
        e.event_type === 'DISTRIBUTION' && e.distribution_type === 'INTEREST'
      );
      const withholdingEvent = dateEvents.find(e => 
        e.event_type === 'TAX_PAYMENT' && e.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING'
      );

      // If we have both interest and withholding on the same date, create a grouped event
      if (interestEvent && withholdingEvent) {
        const otherEvents = dateEvents.filter(event => 
          event.id !== interestEvent.id && event.id !== withholdingEvent.id
        );

        groupedEvents.push({
          date,
          events: dateEvents,
          hasInterestWithholdingPair: true,
          interestEvent,
          withholdingEvent,
          otherEvents
        });

        interestWithholdingPairs++;
      } else {
        // No interest + withholding pair, add as individual events
        dateEvents.forEach(event => {
          // Skip standalone withholding tax events (they should only appear when combined with interest distributions)
          if (event.event_type === 'TAX_PAYMENT' && 
              event.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING') {
            return;
          }

          // Skip tax and debt events if toggle is off
          if (!showTaxEvents && (event.event_type === 'TAX_PAYMENT' || event.event_type === 'EOFY_DEBT_COST')) {
            return;
          }

          // Skip NAV updates if toggle is off
          if (!showNavUpdates && event.event_type === 'NAV_UPDATE') {
            return;
          }

          individualEvents.push(event);
        });
      }
    });

    const result: EventGroupingResult = {
      groupedEvents,
      individualEvents,
      totalEvents: events.length,
      totalGroups: groupedEvents.length,
      interestWithholdingPairs
    };

    // Debug logging in development mode
    if (process.env.NODE_ENV === 'development') {
      console.group('🔍 useEventGrouping Debug');
      console.log('📊 Grouping Results:', {
        totalEvents: events.length,
        totalGroups: groupedEvents.length,
        individualEvents: individualEvents.length,
        interestWithholdingPairs,
        showTaxEvents,
        showNavUpdates
      });
      console.log('📅 Grouped Events:', groupedEvents);
      console.log('📋 Individual Events:', individualEvents);
      console.groupEnd();
    }

    return result;
  }, [events, fund, showTaxEvents, showNavUpdates]);
};

/**
 * Helper function to determine if an event should be shown based on filters
 * Extracted from FundDetail.tsx for reusability
 */
export const shouldShowEvent = (
  event: ExtendedFundEvent,
  showTaxEvents: boolean,
  showNavUpdates: boolean
): boolean => {
  // Skip standalone withholding tax events (they should only appear when combined with interest distributions)
  if (event.event_type === 'TAX_PAYMENT' && 
      event.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING') {
    return false;
  }

  // Skip tax and debt events if toggle is off
  if (!showTaxEvents && (event.event_type === 'TAX_PAYMENT' || event.event_type === 'EOFY_DEBT_COST')) {
    return false;
  }

  // Skip NAV updates if toggle is off
  if (!showNavUpdates && event.event_type === 'NAV_UPDATE') {
    return false;
  }

  return true;
};

/**
 * Helper function to determine if an event is an equity event based on fund type
 * Extracted from FundDetail.tsx for reusability
 */
export const isEquityEvent = (
  event: ExtendedFundEvent,
  fund: ExtendedFund
): boolean => {
  const isNavBased = fund.tracking_type === 'nav_based';
  
  if (isNavBased) {
    return event.event_type === 'UNIT_PURCHASE' || event.event_type === 'UNIT_SALE';
  } else {
    return event.event_type === 'CAPITAL_CALL' || event.event_type === 'RETURN_OF_CAPITAL';
  }
};

/**
 * Helper function to determine if an event is a distribution event
 * Extracted from FundDetail.tsx for reusability
 */
export const isDistributionEvent = (event: ExtendedFundEvent): boolean => {
  return event.event_type === 'DISTRIBUTION';
};

/**
 * Helper function to determine if an event is an "other" event (not equity or distribution)
 * Extracted from FundDetail.tsx for reusability
 */
export const isOtherEvent = (
  event: ExtendedFundEvent,
  fund: ExtendedFund
): boolean => {
  return !isEquityEvent(event, fund) && !isDistributionEvent(event);
}; 