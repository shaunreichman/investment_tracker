import { ExtendedFund, FundStatus, FundType } from '../../types/api';

export const isActiveNavFund = (fund: ExtendedFund): boolean => {
  return fund.tracking_type === FundType.NAV_BASED && fund.status === FundStatus.ACTIVE;
};

/**
 * Get fund status information for display (FundDetail interface)
 * @param status - The fund status string
 * @returns Status info object with value, color, icon, and tooltip
 */
export const getStatusInfo = (status: string) => {
  if (!status) {
    return { 
      value: 'Unknown', 
      color: 'text.secondary', 
      icon: '📊',
      tooltip: 'Unknown fund status'
    };
  }
  
  switch (status.toLowerCase()) {
    case 'active':
      return { 
        value: 'Active', 
        color: '#4caf50', // Lighter green
        icon: '📊',
        tooltip: 'Fund is still invested and has capital at risk'
      };
    case 'realized':
      return { 
        value: 'Realized', 
        color: '#424242', // Dark gray
        icon: '📊',
        tooltip: 'All capital has been returned. Fund will be completed once the final tax statement is added.'
      };
    case 'completed':
      return { 
        value: 'Completed', 
        color: '#000000', // Black
        icon: '📊',
        tooltip: 'Fund is fully realized and all tax obligations are complete'
      };
    default:
      return { 
        value: 'Unknown', 
        color: 'text.secondary', 
        icon: '📊',
        tooltip: 'Unknown fund status'
      };
  }
};

/**
 * Get status tooltip text for display
 * @param status - The fund status string
 * @returns Tooltip text
 */
export const getStatusTooltip = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'active':
      return 'Fund is still invested and has capital at risk';
    case 'realized':
      return 'All capital has been returned. Fund will be completed once the final tax statement is added.';
    case 'completed':
      return 'Fund is fully realized and all tax obligations are complete';
    default:
      return 'Unknown fund status';
  }
};

/**
 * Get tracking type color for display
 * @param trackingType - The fund tracking type string
 * @returns Material-UI color value
 */
export const getTrackingTypeColor = (trackingType: string): 'primary' | 'secondary' | 'default' => {
  switch (trackingType.toLowerCase()) {
    case 'nav_based':
      return 'primary';
    case 'cost_based':
      return 'secondary';
    default:
      return 'default';
  }
};


