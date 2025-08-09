import { ExtendedFundEvent } from '../../types/api';

export const getEventTypeLabel = (event: ExtendedFundEvent): string => {
  if (event.distribution_type) {
    return event.distribution_type.toUpperCase();
  }
  if (event.tax_payment_type) {
    return event.tax_payment_type;
  }
  return event.event_type.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
};

export const getEventTypeLabelSimple = (eventType: string): string => {
  switch (eventType) {
    case 'CAPITAL_CALL': return 'Capital Call';
    case 'RETURN_OF_CAPITAL': return 'Capital Return';
    case 'UNIT_PURCHASE': return 'Unit Purchase';
    case 'UNIT_SALE': return 'Unit Sale';
    case 'NAV_UPDATE': return 'NAV Update';
    case 'DISTRIBUTION': return 'Distribution';
    case 'TAX_STATEMENT': return 'Tax Statement';
    case 'TAX_PAYMENT': return 'Tax Payment';
    default: return eventType;
  }
};

export const combineInterestWithholdingEvents = (events: ExtendedFundEvent[]): ExtendedFundEvent[] => {
  const combinedEvents: ExtendedFundEvent[] = [];
  const processedEvents = new Set<number>();

  events.forEach((event) => {
    if (processedEvents.has(event.id)) return;

    if (event.event_type === 'DISTRIBUTION' && event.distribution_type === 'INTEREST') {
      const sameDateEvents = events.filter((e) => e.event_date === event.event_date);
      const withholdingEvent = sameDateEvents.find(
        (e) => e.event_type === 'TAX_PAYMENT' && e.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING'
      );

      if (withholdingEvent) {
        const combinedEvent = {
          ...event,
          has_withholding_tax: true,
          withholding_amount: withholdingEvent.amount,
          withholding_rate: 10,
          net_interest: (event.amount || 0) - (withholdingEvent.amount || 0),
        } as ExtendedFundEvent & { has_withholding_tax: boolean; withholding_amount?: number | null; withholding_rate?: number | null; net_interest?: number | null };
        combinedEvents.push(combinedEvent as ExtendedFundEvent);
        processedEvents.add(event.id);
        processedEvents.add(withholdingEvent.id);
      } else {
        combinedEvents.push(event);
        processedEvents.add(event.id);
      }
    } else if (event.event_type === 'TAX_PAYMENT' && event.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING') {
      if (!processedEvents.has(event.id)) {
        combinedEvents.push(event);
        processedEvents.add(event.id);
      }
    } else {
      combinedEvents.push(event);
      processedEvents.add(event.id);
    }
  });

  return combinedEvents;
};


