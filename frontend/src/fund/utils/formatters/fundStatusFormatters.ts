import { FundStatus } from '@/fund/types';

export type FundStatusDisplay = {
  value: string;
  color: string;
  icon: string;
  tooltip: string;
};

export const getStatusInfo = (
  status: FundStatus | string | null | undefined
): FundStatusDisplay => {
  if (!status) {
    return getUnknownStatus();
  }

  switch (status.toString().toLowerCase()) {
    case FundStatus.ACTIVE.toLowerCase():
      return {
        value: 'Active',
        color: '#4caf50',
        icon: '📊',
        tooltip: 'Fund is still invested and has capital at risk',
      };
    case FundStatus.REALIZED.toLowerCase():
      return {
        value: 'Realized',
        color: '#424242',
        icon: '📊',
        tooltip:
          'All capital has been returned. Fund will be completed once the final tax statement is added.',
      };
    case FundStatus.COMPLETED.toLowerCase():
      return {
        value: 'Completed',
        color: '#000000',
        icon: '📊',
        tooltip: 'Fund is fully realized and all tax obligations are complete',
      };
    default:
      return getUnknownStatus();
  }
};

export const getStatusTooltip = (
  status: FundStatus | string | null | undefined
): string => {
  return getStatusInfo(status).tooltip;
};

const getUnknownStatus = (): FundStatusDisplay => ({
  value: 'Unknown',
  color: 'text.secondary',
  icon: '📊',
  tooltip: 'Unknown fund status',
});

