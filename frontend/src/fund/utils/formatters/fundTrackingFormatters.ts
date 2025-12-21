import { Fund, FundStatus, FundTrackingType } from '@/fund/types';

export const isActiveNavFund = (
  fund: Pick<Fund, 'tracking_type' | 'status'>
): boolean => {
  return (
    fund.tracking_type === FundTrackingType.NAV_BASED &&
    fund.status === FundStatus.ACTIVE
  );
};

export const getTrackingTypeColor = (
  trackingType: FundTrackingType | string | null | undefined
): 'primary' | 'secondary' | 'default' => {
  if (!trackingType) {
    return 'default';
  }

  switch (trackingType.toString().toLowerCase()) {
    case FundTrackingType.NAV_BASED.toLowerCase():
      return 'primary';
    case FundTrackingType.COST_BASED.toLowerCase():
      return 'secondary';
    default:
      return 'default';
  }
};

