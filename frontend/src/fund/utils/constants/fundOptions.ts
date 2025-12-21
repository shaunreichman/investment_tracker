/**
 * Fund creation templates and selectable options.
 *
 * These MANUAL values power fund onboarding flows. Each entry describes the
 * option label shown to the user, the persisted value, and supporting copy.
 */
import { FundInvestmentType } from '@/fund/types';

export interface FundTemplate {
  label: string;
  value: 'cost_based' | 'nav_based';
  description: string;
  icon: string;
  trackingType: 'cost_based' | 'nav_based';
}

export const FUND_TEMPLATES: FundTemplate[] = [
  {
    label: 'Cost-Based Fund',
    value: 'cost_based',
    description: 'Track capital calls and returns',
    icon: 'Business',
    trackingType: 'cost_based',
  },
  {
    label: 'NAV-Based Fund',
    value: 'nav_based',
    description: 'Track unit purchases and NAV updates',
    icon: 'TrendingUp',
    trackingType: 'nav_based',
  },
];

export interface FundTypeOption {
  label: string;
  value: FundInvestmentType;
}

export const FUND_TYPES: FundTypeOption[] = [
  { label: 'Private Equity', value: FundInvestmentType.PRIVATE_EQUITY },
  { label: 'Venture Capital', value: FundInvestmentType.VENTURE_CAPITAL },
  { label: 'Private Debt', value: FundInvestmentType.PRIVATE_DEBT },
  { label: 'Real Estate', value: FundInvestmentType.REAL_ESTATE },
  { label: 'Infrastructure', value: FundInvestmentType.INFRASTRUCTURE },
  { label: 'Other', value: FundInvestmentType.OTHER },
];

