/**
 * Shared Enums Barrel Export
 * 
 * Centralized export of all shared domain enums.
 * 
 * Usage:
 *   import { SortOrder, Currency, Country } from '@/shared/types/enums';
 */

export {
  // Shared enums
  SortOrder,
  EventOperation,
  Country,
  Currency,
  
  // Domain update event enums
  DomainObjectType,
  SortFieldDomainUpdateEvent,
  
  // Helper functions
  isReverseSortOrder,
  getCurrencyDecimalPlaces,
} from './sharedEnums';

