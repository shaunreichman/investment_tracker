import React, { useState, Suspense } from 'react';
import {
  Box,
  Typography,
  Link,
  Button,
  useTheme,
} from '@mui/material';

import { Add as AddIcon } from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { ErrorDisplay, LoadingSpinner } from '../shared/feedback';
import { ErrorType, createErrorInfo } from '../../types/errors';
import { ConfirmDialog } from '../shared';
import { TabNavigation } from '../shared/navigation/Tabs';
import { OverviewTab } from './overview-tab';
import { CompanyDetailsTab } from './company-details-tab';
import { AnalysisTab } from './analysis-tab';
import { ActivityTab } from './activity-tab';
import { FundsTab } from './funds-tab';
import {
  useCompanyOverview,
  useCompanyDetails,
  useEnhancedFunds,
} from '../../hooks/useCompaniesold';
import { useDeleteFund } from '../../hooks/useFundsold';

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

export const CompaniesPage: React.FC = () => {
  const navigate = useNavigate();
  const { companyId } = useParams<{ companyId: string }>();
  const [activeTab, setActiveTab] = useState('overview');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedFund, setSelectedFund] = useState<{ id: number; name: string } | null>(null);
  const [isDeletingFund, setIsDeletingFund] = useState(false);
  const [deletionError, setDeletionError] = useState<string | null>(null);
  const theme = useTheme();

  // API hooks
  const { data: overviewData, loading: overviewLoading, error: overviewError, refetch: refetchOverview } = useCompanyOverview(
    parseInt(companyId || '0')
  );
  
  const { data: detailsData, loading: detailsLoading } = useCompanyDetails(
    parseInt(companyId || '0')
  );

  // Funds tab state
  const [fundsParams, setFundsParams] = useState({
    search: '',
    status_filter: 'all',
    currency_filter: 'all',
    fund_type_filter: 'all',
    page: 1,
    per_page: 25,
    sort_field: 'start_date',
    sort_direction: 'desc' as 'asc' | 'desc',
    view_mode: 'table' as 'table' | 'cards'
  });

  const { data: fundsData, loading: fundsLoading, refetch: refetchFunds } = useEnhancedFunds(
    parseInt(companyId || '0'),
    {
      sort_by: 'start_date',
      sort_order: 'desc',
      status_filter: 'all',
      search: '',
      page: 1,
      per_page: 25,
    }
  );

  // Fund deletion hook
  const { mutate: deleteFund, loading: deletingFund } = useDeleteFund();

  const handleFundsParamsChange = (newParams: any) => {
    setFundsParams(prev => ({ ...prev, ...newParams }));
  };

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
    // Add small delay before refetch to ensure backend has processed the fund creation
    setTimeout(() => {
      // Refresh the overview data
      refetchOverview();
      // Refresh the funds data (this is what displays the funds list!)
      refetchFunds();
    }, 500);
  };

  // Handle fund deletion request (opens confirmation dialog)
  const handleDeleteFund = (fundId: number, fundName: string) => {
    setSelectedFund({ id: fundId, name: fundName });
    setDeletionError(null); // Clear any previous errors
    setDeleteDialogOpen(true);
  };

  // Confirm fund deletion
  const confirmDeleteFund = async () => {
    if (!selectedFund) return;
    
    setIsDeletingFund(true);
    setDeletionError(null); // Clear any previous errors
    
    try {
      const result = await deleteFund(selectedFund.id);
      
      // Check if deletion was successful
      if (result !== undefined) {
        // Close dialog and clear selection
        setDeleteDialogOpen(false);
        setSelectedFund(null);
        
        // Add small delay before refetch to ensure backend has processed the deletion
        setTimeout(() => {
          // Refresh the overview data
          refetchOverview();
          // Refresh the funds data (this is what displays the funds list!)
          refetchFunds();
        }, 500);
      } else {
        // Set a generic error message since we can't get the specific error
        setDeletionError('Fund has associated events and cannot be deleted.');
      }
      
    } catch (error: any) {
      // Extract error message from the caught error
      const errorMessage = getErrorMessage(error);
      setDeletionError(errorMessage);
    } finally {
      setIsDeletingFund(false);
    }
  };

  // Cancel fund deletion
  const cancelDeleteFund = () => {
    setDeleteDialogOpen(false);
    setSelectedFund(null);
    setDeletionError(null);
  };

  // Helper function to extract error message from error object
  const getErrorMessage = (error: any): string => {
    if (!error) return 'Fund has associated events and cannot be deleted.';
    
    // Try different possible error message properties
    if (typeof error === 'string') return error;
    if (error.details) return error.details;
    if (error.message) return error.message;
    if (error.error?.message) return error.error.message;
    if (error.error?.details) return error.error.details;
    
    // Fallback
    return 'Fund has associated events and cannot be deleted.';
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
                color: theme.palette.text.primary,
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
                  color: theme.palette.text.secondary,
                  fontSize: '16px',
                  lineHeight: 1.5,
                  maxWidth: '600px'
                }}
              >
                {overviewData.company.company_type} Company
              </Typography>
            )}
          </Box>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateModalOpen(true)}
            size="large"
            sx={{
              backgroundColor: theme.palette.primary.main,
              '&:hover': {
                backgroundColor: theme.palette.primary.dark
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
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: '8px',
              px: 3,
              py: 2
            }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: theme.palette.text.secondary,
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
                  color: theme.palette.primary.main,
                  textDecoration: 'none',
                  fontWeight: 500,
                  '&:hover': {
                    color: theme.palette.primary.dark
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
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: '8px',
              px: 3,
              py: 2
            }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: theme.palette.text.secondary,
                  mr: 2,
                  fontWeight: 500
                }}
              >
                Contact:
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: theme.palette.text.primary,
                  fontWeight: 500
                }}
              >
                {overviewData.company.contacts[0]?.name}
                {overviewData.company.contacts[0]?.direct_email && (
                  <Box sx={{ mt: 0.5 }}>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: theme.palette.text.secondary,
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
        backgroundColor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.divider}`,
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
          <FundsTab
            data={fundsData}
            loading={fundsLoading}
            onParamsChange={handleFundsParamsChange}
            currentParams={fundsParams}
            onDeleteFund={handleDeleteFund}
          />
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

      {/* Fund Deletion Confirmation Dialog */}
      <ConfirmDialog
        open={deleteDialogOpen}
        title="Delete Fund"
        description={
          deletionError 
            ? `Cannot delete fund "${selectedFund?.name}". ${deletionError}`
            : `Are you sure you want to delete the fund "${selectedFund?.name}"? This action cannot be undone.`
        }
        confirmLabel={deletionError ? "OK" : "Delete"}
        cancelLabel={deletionError ? "" : "Cancel"}
        onConfirm={deletionError ? cancelDeleteFund : confirmDeleteFund}
        onCancel={deletionError ? () => {} : cancelDeleteFund}
        loading={isDeletingFund}
        confirmVariant={deletionError ? "primary" : "error"}
      />
    </Box>
  );
};
