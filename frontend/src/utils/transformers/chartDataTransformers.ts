import { ExtendedFund, ExtendedFundEvent } from '../../types/api';

export const prepareChartData = (events: ExtendedFundEvent[], fund: ExtendedFund) => {
  if (fund.tracking_type !== 'nav_based') {
    return { navData: [], purchaseData: [], saleData: [] } as const;
  }

  const navData: Array<{ date: string; nav: number }> = [];
  const purchaseData: Array<{ date: string; price: number; units: number }> = [];
  const saleData: Array<{ date: string; price: number; units: number }> = [];

  events.forEach((event) => {
    const date = event.event_date;

    if (event.event_type === 'NAV_UPDATE' && event.nav_per_share) {
      navData.push({ date, nav: event.nav_per_share });
    } else if (event.event_type === 'UNIT_PURCHASE' && event.unit_price && event.units_purchased) {
      purchaseData.push({ date, price: event.unit_price, units: event.units_purchased });
    } else if (event.event_type === 'UNIT_SALE' && event.unit_price && event.units_sold) {
      saleData.push({ date, price: event.unit_price, units: event.units_sold });
    }
  });

  return { navData, purchaseData, saleData } as const;
};

export const calculateDateRange = (events: ExtendedFundEvent[]) => {
  if (events.length === 0) {
    const today = new Date();
    const sixMonthsAgo = new Date(today.getFullYear(), today.getMonth() - 6, today.getDate());
    const startDateStr = sixMonthsAgo.toISOString().split('T')[0];
    const endDateStr = today.toISOString().split('T')[0];
    if (!startDateStr || !endDateStr) return { startDate: '', endDate: '' };
    return {
      startDate: startDateStr,
      endDate: endDateStr,
    } as const;
  }

  const dates = events.map((e) => new Date(e.event_date));
  const startDate = new Date(Math.min(...dates.map((d) => d.getTime())));
  const endDate = new Date(Math.max(...dates.map((d) => d.getTime())));

  startDate.setMonth(startDate.getMonth() - 1);
  endDate.setMonth(endDate.getMonth() + 1);

  const startDateStr = startDate.toISOString().split('T')[0];
  const endDateStr = endDate.toISOString().split('T')[0];
  if (!startDateStr || !endDateStr) return { startDate: '', endDate: '' };

  return {
    startDate: startDateStr,
    endDate: endDateStr,
  } as const;
};

export const generateChartTicks = (startDate: string, endDate: string): string[] => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const ticks: string[] = [];

  const current = new Date(start);
  while (current <= end) {
    const dateStr = current.toISOString().split('T')[0];
    if (dateStr) {
      ticks.push(dateStr);
    }
    current.setMonth(current.getMonth() + 1);
  }

  return ticks;
};


