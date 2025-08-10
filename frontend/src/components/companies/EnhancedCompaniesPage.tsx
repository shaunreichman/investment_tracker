import React, { useState, Suspense } from 'react';
import {
  Box,
  Typography,
  Link,
  Breadcrumbs,
  Button,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { ErrorDisplay } from '../ErrorDisplay';
import { ErrorType, ErrorSeverity, createErrorInfo } from '../../types/errors';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { TabNavigation } from './TabNavigation';
import { OverviewTab } from './overview-tab';
import { FundsTab } from './funds-tab';
import { CompanyDetailsTab } from './company-details-tab';
import { AnalysisTab } from './analysis-tab';
import { ActivityTab } from './activity-tab';
import {
  useCompanyOverview,
  useEnhancedFunds,
  useCompanyDetails,
} from '../../hooks/useInvestmentCompanies';

const CreateFundModal = React.lazy(() => import('../companies/create-fund/CreateFundModal'));

// ============================================================================
// TYPES
// ============================================================================

interface TabData {
  id: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const EnhancedCompaniesPage: React.FC = () => {
  const navigate = useNavigate();
  const { companyId } = useParams<{ companyId: string }>();
  const [activeTab, setActiveTab] = useState('overview');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [fundsParams, setFundsParams] = useState({
    sort_by: 'start_date',
    sort_order: 'desc' as 'asc' | 'desc',
    status_filter: 'all' as 'all' | 'active' | 'completed' | 'suspended',
    search: '',
    page: 1,
    per_page: 25,
  });

  // API hooks
  const { data: overviewData, loading: overviewLoading, error: overviewError, refetch: refetchOverview } = useCompanyOverview(
    parseInt(companyId || '0')
  );
  
  const { data: fundsData, loading: fundsLoading, error: fundsError, refetch: refetchFunds } = useEnhancedFunds(
    parseInt(companyId || '0'),
    fundsParams
  );
  
  const { data: detailsData, loading: detailsLoading, error: detailsError, refetch: refetchDetails } = useCompanyDetails(
    parseInt(companyId || '0')
  );

  // Tab configuration
  const tabs: TabData[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'funds', label: 'Funds' },
    { id: 'analysis', label: 'Analysis' },
    { id: 'activity', label: 'Activity' },
    { id: 'details', label: 'Company Details' },
  ];

  // Handle tab change
  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
  };

  // Handle funds parameters change
  const handleFundsParamsChange = (newParams: any) => {
    setFundsParams(newParams);
  };

  // Handle fund creation
  const handleFundCreated = () => {
    // Refresh the overview data
    // Note: The enhanced funds data will refresh automatically due to the params change
  };

  // Error handling - these functions are kept for future use when implementing tab-specific error/loading states
  // const getActiveTabError = () => {
  //   switch (activeTab) {
  //     case 'overview':
  //       return overviewError;
  //     case 'funds':
  //       return fundsError;
  //     case 'details':
  //       return detailsError;
  //     default:
  //       return null;
  //   }
  // };

  // const getActiveTabLoading = () => {
  //   switch (activeTab) {
  //     case 'overview':
  //       return overviewLoading;
  //     case 'funds':
  //       return fundsLoading;
  //     case 'details':
  //       return detailsLoading;
  //     default:
  //       return false;
  //   }
  // };

    // Handle errors from any of the API calls
    if (overviewError || fundsError || detailsError) {
      const errorMessage = overviewError || fundsError || detailsError || 'Unknown error';
      
      // Check if the error is already an ErrorInfo object
      let errorInfo;
      if (typeof errorMessage === 'object' && errorMessage !== null && 'retryable' in errorMessage) {
        errorInfo = errorMessage;
      } else {
        errorInfo = createErrorInfo(typeof errorMessage === 'string' ? errorMessage : 'Unknown error');
      }
      
      return (
        <Box p={3}>
          <ErrorDisplay
            error={errorInfo}
            canRetry={errorInfo.retryable}
            onRetry={() => {
              refetchOverview();
              refetchFunds();
              refetchDetails();
            }}
            onDismiss={() => window.location.reload()}
          />
        </Box>
      );
    }

  // Show loading for initial data
  if (overviewLoading && !overviewData) {
    return (
      <Box p={3}>
        <LoadingSpinner label="Loading company data..." />
      </Box>
    );
  }

  // Show error if company not found
  if (!overviewData?.company) {
    return (
      <Box p={3}>
        <ErrorDisplay
          error={{
            message: 'Company not found',
            type: ErrorType.NOT_FOUND,
            severity: ErrorSeverity.MEDIUM,
            retryable: false,
            userMessage: 'The requested company could not be found.',
            timestamp: new Date()
          }}
          canRetry={false}
          onDismiss={() => navigate('/')}
        />
      </Box>
    );
  }

  const company = overviewData.company;

  return (
    <Box>
      {/* Breadcrumb Navigation */}
      <Box p={3} pb={0}>
        <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
          <Link
            component="button"
            variant="body2"
            onClick={() => navigate('/')}
            sx={{ textDecoration: 'none', cursor: 'pointer' }}
          >
            Investment Companies
          </Link>
          <Typography color="text.primary">{company.name}</Typography>
        </Breadcrumbs>

        {/* Company Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h4" gutterBottom>
              {company.name}
            </Typography>
            
            <Typography variant="body1" color="textSecondary">
              {company.company_type ? `${company.company_type} Investment Company` : 'Investment Company'}
            </Typography>
          </Box>

          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateModalOpen(true)}
          >
            Create Fund
          </Button>
        </Box>
      </Box>

      {/* Tab Navigation */}
      <TabNavigation
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={handleTabChange}
      />

      {/* Tab Content */}
      <Box>
        {activeTab === 'overview' && (
          <Box
            role="tabpanel"
            id="overview-tabpanel"
            aria-labelledby="overview-tab"
            hidden={activeTab !== 'overview'}
          >
            <OverviewTab
              data={overviewData}
              loading={overviewLoading}
            />
          </Box>
        )}

        {activeTab === 'funds' && (
          <Box
            role="tabpanel"
            id="funds-tabpanel"
            aria-labelledby="funds-tab"
            hidden={activeTab !== 'funds'}
          >
            <FundsTab
              data={fundsData}
              loading={fundsLoading}
              onParamsChange={handleFundsParamsChange}
              currentParams={fundsParams}
            />
          </Box>
        )}

        {activeTab === 'analysis' && (
          <Box
            role="tabpanel"
            id="analysis-tabpanel"
            aria-labelledby="analysis-tab"
            hidden={activeTab !== 'analysis'}
          >
            <AnalysisTab />
          </Box>
        )}

        {activeTab === 'activity' && (
          <Box
            role="tabpanel"
            id="activity-tabpanel"
            aria-labelledby="activity-tab"
            hidden={activeTab !== 'activity'}
          >
            <ActivityTab />
          </Box>
        )}

        {activeTab === 'details' && (
          <Box
            role="tabpanel"
            id="details-tabpanel"
            aria-labelledby="details-tab"
            hidden={activeTab !== 'details'}
          >
            <CompanyDetailsTab
              data={detailsData!}
              loading={detailsLoading}
            />
          </Box>
        )}
      </Box>

      {/* Create Fund Modal */}
      <Suspense fallback={null}>
        <CreateFundModal
          open={createModalOpen}
          onClose={() => setCreateModalOpen(false)}
          onFundCreated={handleFundCreated}
          companyId={parseInt(companyId!)}
          companyName={company.name}
        />
      </Suspense>
    </Box>
  );
};
