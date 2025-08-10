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


