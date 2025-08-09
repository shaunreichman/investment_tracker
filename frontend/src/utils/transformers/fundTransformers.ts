import { ExtendedFund, FundStatus } from '../../types/api';

export const isActiveNavFund = (fund: ExtendedFund): boolean => {
  return fund.tracking_type === 'nav_based' && fund.status === FundStatus.ACTIVE;
};


