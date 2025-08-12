import React, { useState, Suspense } from 'react';
import {
  Box,
  Typography,
  Link,
  Button,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { ErrorDisplay } from '../ErrorDisplay';
import { ErrorType, createErrorInfo } from '../../types/errors';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { TabNavigation } from './TabNavigation';
import { OverviewTab } from './overview-tab';
import { CompanyDetailsTab } from './company-details-tab';
import { AnalysisTab } from './analysis-tab';
import { ActivityTab } from './activity-tab';
import {
  useCompanyOverview,
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

  // API hooks
  const { data: overviewData, loading: overviewLoading, error: overviewError, refetch: refetchOverview } = useCompanyOverview(
    parseInt(companyId || '0')
  );
  
  const { data: detailsData, loading: detailsLoading } = useCompanyDetails(
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

  // Handle fund creation
  const handleFundCreated = () => {
    // Refresh the overview data
    refetchOverview();
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

  // Show loading state for overview data
  if (overviewLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <LoadingSpinner label="Loading company overview..." />
      </Box>
    );
  }

  // Show error state for overview data
  if (overviewError) {
    const errorInfo = typeof overviewError === 'string' ? createErrorInfo(overviewError) : overviewError;
    return (
      <Box sx={{ p: 3 }}>
        <ErrorDisplay
          error={errorInfo}
          canRetry={errorInfo.retryable}
          onRetry={refetchOverview}
          onDismiss={() => navigate('/')}
        />
      </Box>
    );
  }

  // Show error state if no company data
  if (!overviewData) {
    return (
      <Box sx={{ p: 3 }}>
        <ErrorDisplay
          error={createErrorInfo('Company not found', ErrorType.NOT_FOUND)}
          canRetry={false}
          onDismiss={() => navigate('/')}
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 0 }}>
      {/* Company Header Section */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'flex-start',
          mb: 3
        }}>
          <Box>
            <Typography 
              variant="h3" 
              sx={{ 
                color: '#FFFFFF',
                fontWeight: 600,
                mb: 1,
                letterSpacing: '-0.02em'
              }}
            >
              {overviewData.company.name}
            </Typography>
            
            {overviewData.company.company_type && (
              <Typography 
                variant="body1" 
                sx={{ 
                  color: '#8B949E',
                  fontSize: '16px',
                  lineHeight: 1.5,
                  maxWidth: '600px'
                }}
              >
                {overviewData.company.company_type} Investment Company
              </Typography>
            )}
          </Box>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateModalOpen(true)}
            size="large"
            sx={{
              backgroundColor: '#2496ED',
              '&:hover': {
                backgroundColor: '#1B7FC4'
              },
              px: 4,
              py: 1.5,
              fontSize: '14px',
              fontWeight: 500
            }}
          >
            Create Fund
          </Button>
        </Box>

        {/* Company Metadata */}
        <Box sx={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: 3,
          mb: 3
        }}>
          {overviewData.company.website && (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center',
              backgroundColor: '#1F2937',
              border: '1px solid #303234',
              borderRadius: '8px',
              px: 3,
              py: 2
            }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: '#8B949E',
                  mr: 2,
                  fontWeight: 500
                }}
              >
                Website:
              </Typography>
              <Link
                href={overviewData.company.website}
                target="_blank"
                rel="noopener noreferrer"
                sx={{
                  color: '#2496ED',
                  textDecoration: 'none',
                  fontWeight: 500,
                  '&:hover': {
                    color: '#1B7FC4'
                  }
                }}
              >
                {overviewData.company.website}
              </Link>
            </Box>
          )}
          
          {overviewData.company.contacts && overviewData.company.contacts.length > 0 && (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center',
              backgroundColor: '#1F2937',
              border: '1px solid #303234',
              borderRadius: '8px',
              px: 3,
              py: 2
            }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: '#8B949E',
                  mr: 2,
                  fontWeight: 500
                }}
              >
                Contact:
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: '#FFFFFF',
                  fontWeight: 500
                }}
              >
                {overviewData.company.contacts[0]?.name}
                {overviewData.company.contacts[0]?.direct_email && (
                  <Box sx={{ mt: 0.5 }}>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: '#8B949E',
                        fontSize: '12px'
                      }}
                    >
                      {overviewData.company.contacts[0]?.direct_email}
                    </Typography>
                  </Box>
                )}
              </Typography>
            </Box>
          )}
        </Box>
      </Box>

      {/* Tab Navigation */}
      <Box sx={{ mb: 3 }}>
        <TabNavigation
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={handleTabChange}
        />
      </Box>

      {/* Tab Content */}
      <Box sx={{ 
        backgroundColor: '#1F2937',
        border: '1px solid #303234',
        borderTop: 'none',
        borderRadius: '0 0 8px 8px',
        minHeight: '400px'
      }}>
        {activeTab === 'overview' && (
          <OverviewTab 
            data={overviewData}
            loading={overviewLoading}
          />
        )}
        
        {activeTab === 'funds' && (
          <Box sx={{ p: 3 }}>
            <Typography 
              variant="h6" 
              sx={{ 
                color: '#FFFFFF',
                fontWeight: 600,
                mb: 2
              }}
            >
              Funds Management
            </Typography>
            <Typography 
              variant="body1" 
              sx={{ 
                color: '#8B949E',
                lineHeight: 1.5
              }}
            >
              Funds management functionality will be implemented in the next phase. This tab will provide comprehensive fund overview, filtering, and management capabilities.
            </Typography>
          </Box>
        )}
        
        {activeTab === 'analysis' && (
          <AnalysisTab />
        )}
        
        {activeTab === 'activity' && (
          <ActivityTab />
        )}
        
        {activeTab === 'details' && detailsData && (
          <CompanyDetailsTab
            data={detailsData}
            loading={detailsLoading}
          />
        )}
      </Box>

      {/* Create Fund Modal */}
      <Suspense fallback={<LoadingSpinner label="Loading create fund form..." />}>
        <CreateFundModal
          open={createModalOpen}
          onClose={() => setCreateModalOpen(false)}
          onFundCreated={handleFundCreated}
          companyId={parseInt(companyId || '0')}
          companyName={overviewData.company.name}
        />
      </Suspense>
    </Box>
  );
};
