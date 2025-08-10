import { useMemo } from 'react';
import { FundEvent, ExtendedFundEvent, GroupType } from '../../../../types/api';

// CALCULATED: Union type to handle both FundEvent and ExtendedFundEvent
type EventWithGrouping = FundEvent | ExtendedFundEvent;

export interface GroupedEvent {
  events: EventWithGrouping[];
  isGrouped: boolean;
  groupType?: GroupType;
  groupId?: number;
  displayDate: string;
  displayAmount: number;
  displayDescription: string;
}

export const useEventGrouping = (events: EventWithGrouping[]): GroupedEvent[] => {
  return useMemo(() => {
    if (!events || events.length === 0) return [];

    // SYSTEM: Sort events by date (newest first) for consistent display
    const sortedEvents = [...events].sort((a, b) => 
      new Date(b.event_date).getTime() - new Date(a.event_date).getTime()
    );

    const groupedEvents: GroupedEvent[] = [];
    const processedGroupIds = new Set<number>();

    for (const event of sortedEvents) {
      // CALCULATED: Check if this event is part of a group
      if (event.is_grouped && event.group_id && event.group_type) {
        // SYSTEM: Skip if we've already processed this group
        if (processedGroupIds.has(event.group_id)) {
          continue;
        }

        // CALCULATED: Find all events in this group
        const groupEvents = sortedEvents.filter(e => 
          e.group_id === event.group_id && e.is_grouped
        );

        // SYSTEM: Sort group events by position for proper ordering
        const sortedGroupEvents = groupEvents.sort((a, b) => 
          (a.group_position || 0) - (b.group_position || 0)
        );

        // CALCULATED: Create grouped event display
        const groupedEvent: GroupedEvent = {
          events: sortedGroupEvents,
          isGrouped: true,
          groupType: event.group_type,
          groupId: event.group_id,
          displayDate: sortedGroupEvents[0]?.event_date || event.event_date,
          displayAmount: sortedGroupEvents.reduce((sum, e) => sum + (e.amount || 0), 0),
          displayDescription: getGroupDescription(event.group_type, sortedGroupEvents)
        };

        groupedEvents.push(groupedEvent);
        processedGroupIds.add(event.group_id);
      } else {
        // CALCULATED: Single event (not grouped)
        const singleEvent: GroupedEvent = {
          events: [event],
          isGrouped: false,
          displayDate: event.event_date,
          displayAmount: event.amount || 0,
          displayDescription: event.description || getEventTypeDescription(event.event_type)
        };

        groupedEvents.push(singleEvent);
      }
    }

    return groupedEvents;
  }, [events]);
};

// CALCULATED: Generate descriptive text for grouped events
const getGroupDescription = (groupType: GroupType, events: EventWithGrouping[]): string => {
  switch (groupType) {
    case GroupType.INTEREST_WITHHOLDING:
      const interestEvent = events.find(e => e.event_type === 'DISTRIBUTION');
      const withholdingEvent = events.find(e => e.event_type === 'TAX_PAYMENT');
      
      if (interestEvent && withholdingEvent) {
        return `Interest Distribution + Withholding Tax (${interestEvent.amount || 0} + ${withholdingEvent.amount || 0})`;
      }
      return 'Interest + Withholding Tax Group';
      
    case GroupType.TAX_STATEMENT:
      return 'Tax Statement Group';
      
    default:
      return 'Grouped Events';
  }
};

// CALCULATED: Generate description for single events
const getEventTypeDescription = (eventType: string): string => {
  const descriptions: Record<string, string> = {
    'CAPITAL_CALL': 'Capital Call',
    'RETURN_OF_CAPITAL': 'Return of Capital',
    'UNIT_PURCHASE': 'Unit Purchase',
    'UNIT_SALE': 'Unit Sale',
    'NAV_UPDATE': 'NAV Update',
    'DISTRIBUTION': 'Distribution',
    'TAX_PAYMENT': 'Tax Payment',
    'EOFY_DEBT_COST': 'EOFY Debt Cost',
    'DAILY_RISK_FREE_INTEREST_CHARGE': 'Risk-Free Interest Charge',
    'MANAGEMENT_FEE': 'Management Fee',
    'CARRIED_INTEREST': 'Carried Interest',
    'OTHER': 'Other Event'
  };
  
  return descriptions[eventType] || eventType;
}; 