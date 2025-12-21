/**
 * Fund event templates and distribution presets.
 *
 * All templates are FUND_DOMAIN MANUAL configuration values surfaced in the
 * fund event creation workflows. Each template entry includes a short label,
 * the underlying event enum value, and the UI metadata required by the form.
 */
import { EventType } from '@/fund/types';

export type FundEventTrackingType = 'nav_based' | 'cost_based' | 'both';

export interface FundEventTemplate {
  label: string;
  value: EventType | 'TAX_STATEMENT';
  description: string;
  icon: string;
  trackingType: FundEventTrackingType;
}

export const EVENT_TEMPLATES: FundEventTemplate[] = [
  {
    label: 'Capital Call',
    value: EventType.CAPITAL_CALL,
    description: 'Add a capital call (cost-based funds)',
    icon: 'AccountBalance',
    trackingType: 'cost_based',
  },
  {
    label: 'Capital Return',
    value: EventType.RETURN_OF_CAPITAL,
    description: 'Return capital to investors (cost-based funds)',
    icon: 'AccountBalance',
    trackingType: 'cost_based',
  },
  {
    label: 'Unit Purchase',
    value: EventType.UNIT_PURCHASE,
    description: 'Buy units (NAV-based funds)',
    icon: 'Add',
    trackingType: 'nav_based',
  },
  {
    label: 'Unit Sale',
    value: EventType.UNIT_SALE,
    description: 'Sell units (NAV-based funds)',
    icon: 'TrendingUp',
    trackingType: 'nav_based',
  },
  {
    label: 'NAV Update',
    value: EventType.NAV_UPDATE,
    description: 'Update NAV per share (NAV-based funds)',
    icon: 'TrendingUp',
    trackingType: 'nav_based',
  },
  {
    label: 'Distribution',
    value: EventType.DISTRIBUTION,
    description: 'Add a distribution (all funds)',
    icon: 'MonetizationOn',
    trackingType: 'both',
  },
  {
    label: 'Tax Statement',
    value: 'TAX_STATEMENT',
    description: 'Add a tax statement (all funds)',
    icon: 'Receipt',
    trackingType: 'both',
  },
];

export interface DistributionTemplate<TValue extends string = string> {
  label: string;
  value: TValue;
  description: string;
  icon: string;
}

export type PrimaryDistributionType = 'INTEREST' | 'DIVIDEND' | 'OTHER';

export const DISTRIBUTION_TEMPLATES: DistributionTemplate<PrimaryDistributionType>[] = [
  {
    label: 'Interest',
    value: 'INTEREST',
    description: 'Interest distribution',
    icon: 'MonetizationOn',
  },
  {
    label: 'Dividend',
    value: 'DIVIDEND',
    description: 'Dividend distribution',
    icon: 'MonetizationOn',
  },
  {
    label: 'Other',
    value: 'OTHER',
    description: 'Other distribution',
    icon: 'MonetizationOn',
  },
];

export type SubDistributionType =
  | 'DIVIDEND_FRANKED'
  | 'DIVIDEND_UNFRANKED'
  | 'REGULAR'
  | 'WITHHOLDING_TAX';

export type DividendSubDistributionType = Extract<
  SubDistributionType,
  'DIVIDEND_FRANKED' | 'DIVIDEND_UNFRANKED'
>;

export type InterestSubDistributionType = Extract<
  SubDistributionType,
  'REGULAR' | 'WITHHOLDING_TAX'
>;

export const DIVIDEND_SUB_TEMPLATES: DistributionTemplate<DividendSubDistributionType>[] = [
  {
    label: 'Franked',
    value: 'DIVIDEND_FRANKED',
    description: 'Franked dividend',
    icon: 'MonetizationOn',
  },
  {
    label: 'Unfranked',
    value: 'DIVIDEND_UNFRANKED',
    description: 'Unfranked dividend',
    icon: 'MonetizationOn',
  },
];

export const INTEREST_SUB_TEMPLATES: DistributionTemplate<InterestSubDistributionType>[] = [
  {
    label: 'Regular',
    value: 'REGULAR',
    description: 'Regular interest',
    icon: 'MonetizationOn',
  },
  {
    label: 'Withholding Tax',
    value: 'WITHHOLDING_TAX',
    description: 'Interest with withholding tax',
    icon: 'MonetizationOn',
  },
];

