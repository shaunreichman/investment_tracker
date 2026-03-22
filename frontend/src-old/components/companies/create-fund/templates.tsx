import React from 'react';
import { AccountBalance as AccountBalanceIcon, TrendingUp as TrendingUpIcon } from '@mui/icons-material';

export interface FundTemplate {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  fund_type: string;
  tracking_type: 'nav_based' | 'cost_based';
  currency: string;
  commitment_amount?: number;
  expected_irr?: number;
  expected_duration_months?: number;
  description_template: string;
}

export const FUND_TEMPLATES: FundTemplate[] = [
  {
    id: 'cost-based',
    name: 'Cost-Based Fund',
    description: 'Track investments using capital calls and returns',
    icon: <AccountBalanceIcon />,
    fund_type: '',
    tracking_type: 'cost_based',
    currency: 'AUD',
    description_template: ''
  },
  {
    id: 'nav-based',
    name: 'NAV-Based Fund',
    description: 'Track investments using units and NAV per share',
    icon: <TrendingUpIcon />,
    fund_type: '',
    tracking_type: 'nav_based',
    currency: 'AUD',
    description_template: ''
  }
];


