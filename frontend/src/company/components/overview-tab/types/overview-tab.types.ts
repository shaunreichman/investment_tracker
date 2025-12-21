import type { CompanyOverviewResponse } from '@/company/types';

export interface OverviewTabProps {
  data: CompanyOverviewResponse;
  loading: boolean;
}

export interface PortfolioSummaryCardsProps {
  portfolioSummary: CompanyOverviewResponse['portfolio_summary'];
}

export interface QuickStatsGridProps {
  portfolioSummary: CompanyOverviewResponse['portfolio_summary'];
  lastActivity: CompanyOverviewResponse['last_activity'];
}

export interface PerformanceSummaryProps {
  performanceSummary: CompanyOverviewResponse['performance_summary'];
}
