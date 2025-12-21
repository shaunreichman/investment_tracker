/**
 * Fund display configuration shared across UI components.
 *
 * These MANUAL mappings keep presentation rules consistent across tables,
 * chips, and summary cards in the fund domain.
 */
import { EventType, FundStatus } from '@/fund/types';

export type EventDisplayColor =
  | 'primary'
  | 'success'
  | 'warning'
  | 'info'
  | 'error'
  | 'default';

export const EVENT_TYPE_COLORS: Record<string, EventDisplayColor> = {
  [EventType.CAPITAL_CALL]: 'primary',
  [EventType.DISTRIBUTION]: 'success',
  [EventType.RETURN_OF_CAPITAL]: 'warning',
  [EventType.NAV_UPDATE]: 'info',
  [EventType.UNIT_PURCHASE]: 'primary',
  [EventType.UNIT_SALE]: 'warning',
  [EventType.TAX_PAYMENT]: 'error',
  TAX_STATEMENT: 'info',
  INTEREST: 'success',
  DIVIDEND: 'success',
  OTHER: 'default',
};

export type FundStatusColor = 'success' | 'warning' | 'info';

export const FUND_STATUS_COLORS: Partial<Record<FundStatus, FundStatusColor>> = {
  [FundStatus.ACTIVE]: 'success',
  [FundStatus.SUSPENDED]: 'info',
  [FundStatus.REALIZED]: 'warning',
  [FundStatus.COMPLETED]: 'info',
};

