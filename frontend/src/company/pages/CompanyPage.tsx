/**
 * CompanyPage Component
 * 
 * Main page for displaying a single company with tabbed navigation.
 * Handles data fetching and passes data to tab components.
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  Box,
  Typography,
  Link,
  Button,
  useTheme,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { ErrorDisplay, LoadingSpinner } from '@/shared/ui/feedback';
import { ErrorType } from '@/shared/types/errors';
import { createErrorInfo } from '@/shared/utils/errors';
import { ConfirmDialog } from '@/shared/ui/overlays';
import { TabNavigation } from '@/shared/ui/navigation';
import { OverviewTab } from '../components/overview-tab';
import { CompanyDetailsTab } from '../components/details-tab';
import { AnalysisTab } from '../components/analysis-tab';
import { ActivityTab } from '../components/activity-tab';
import { FundsTab } from '../components/funds-tab';
import { CreateFundModal } from '../components/create-fund';
import {
  useCompanyOverview,
  useCompanyDetails,
} from '../hooks';
import { useFunds } from '@/fund/hooks';
import { useDeleteFund } from '@/fund/hooks';
import { FundStatus, SortFieldFund } from '@/fund/types';
import { SortOrder } from '@/shared/types';
import type { FundsTabData } from '../components/funds-tab/types/funds-tab.types';

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

export const CompanyPage: React.FC = () => {
  const navigate = useNavigate();
  const { companyId } = useParams<{ companyId: string }>();
  const [activeTab, setActiveTab] = useState('overview');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedFund, setSelectedFund] = useState<{ id: number; name: string } | null>(null);
  const [fundIdToDelete, setFundIdToDelete] = useState<number>(0);
  const [isDeletingFund, setIsDeletingFund] = useState(false);
  const [deletionError, setDeletionError] = useState<string | null>(null);
  const theme = useTheme();

  const companyIdNum = parseInt(companyId || '0');

  // API hooks
  const { data: overviewData, loading: overviewLoading, error: overviewError, refetch: refetchOverview } = useCompanyOverview(
    companyIdNum
  );
  
  const { data: detailsData, loading: detailsLoading } = useCompanyDetails(
    companyIdNum
  );

  // Funds tab state - using FundsTabData structure
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

  // Map frontend params to backend API params
  const fundsApiParams = useMemo(() => {
    const params: {
      company_id: number;
      fund_status?: FundStatus;
      sort_by?: SortFieldFund;
      sort_order?: SortOrder;
      search?: string;
      page?: number;
      per_page?: number;
    } = {
      company_id: companyIdNum,
    };

    // Map status filter: 'all' means no filter, otherwise map to FundStatus enum
    if (fundsParams.status_filter && fundsParams.status_filter !== 'all') {
      // Map string to enum: 'active' -> FundStatus.ACTIVE, etc.
      const statusMap: Record<string, FundStatus> = {
        'active': FundStatus.ACTIVE,
        'suspended': FundStatus.SUSPENDED,
        'realized': FundStatus.REALIZED,
        'completed': FundStatus.COMPLETED,
      };
      params.fund_status = statusMap[fundsParams.status_filter] || FundStatus.ACTIVE;
    }

    // Map sort_by: string -> SortFieldFund enum
    if (fundsParams.sort_field) {
      const sortFieldMap: Record<string, SortFieldFund> = {
        'start_date': SortFieldFund.START_DATE,
        'name': SortFieldFund.NAME,
        'status': SortFieldFund.STATUS,
        'commitment_amount': SortFieldFund.COMMITMENT_AMOUNT,
        'current_equity_balance': SortFieldFund.CURRENT_EQUITY_BALANCE,
        'created_at': SortFieldFund.CREATED_AT,
        'updated_at': SortFieldFund.UPDATED_AT,
        'event_date': SortFieldFund.EVENT_DATE,
      };
      params.sort_by = sortFieldMap[fundsParams.sort_field] || SortFieldFund.START_DATE;
    }

    // Map sort_order: 'asc' | 'desc' -> SortOrder enum
    if (fundsParams.sort_direction) {
      params.sort_order = fundsParams.sort_direction.toUpperCase() as SortOrder;
    }

    // Add search if provided
    if (fundsParams.search) {
      params.search = fundsParams.search;
    }

    // Add pagination
    if (fundsParams.page) {
      params.page = fundsParams.page;
    }
    if (fundsParams.per_page) {
      params.per_page = fundsParams.per_page;
    }

    return params;
  }, [companyIdNum, fundsParams]);

  // Use useFunds hook instead of useEnhancedFunds
  const { data: fundsResponse, loading: fundsLoading, refetch: refetchFunds } = useFunds(
    fundsApiParams
  );

  // Transform funds response to FundsTabData format
  const fundsTabData: FundsTabData | null = useMemo(() => {
    if (!fundsResponse || !fundsResponse.funds) {
      return null;
    }

    return {
      funds: fundsResponse.funds, // Extract funds array from GetFundsResponse
      filters: {
        applied_status_filter: fundsParams.status_filter || 'all',
        applied_search: fundsParams.search || null,
      },
    };
  }, [fundsResponse, fundsParams.status_filter, fundsParams.search]);

  // Fund deletion hook - use fundIdToDelete state which updates when selectedFund changes
  // This ensures the hook always has the correct fundId when mutate is called
  const { mutate: deleteFund, loading: deletingFund } = useDeleteFund(fundIdToDelete);

  // Stabilize callback to prevent unnecessary re-renders
  // Supports both object updates and functional updates (like React's setState)
  const handleFundsParamsChange = useCallback((newParamsOrUpdater: any) => {
    if (typeof newParamsOrUpdater === 'function') {
      setFundsParams(newParamsOrUpdater);
    } else {
      setFundsParams(prev => ({ ...prev, ...newParamsOrUpdater }));
    }
  }, []);

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
    setFundIdToDelete(fundId); // Update fundId for the hook
    setDeletionError(null); // Clear any previous errors
    setDeleteDialogOpen(true);
  };

  // Confirm fund deletion
  const confirmDeleteFund = async () => {
    if (!selectedFund) return;
    
    setIsDeletingFund(true);
    setDeletionError(null); // Clear any previous errors
    
    try {
      // Call deleteFund - mutate only takes variables (undefined for void mutations)
      const result = await deleteFund(undefined);
      
      // Check if deletion was successful (result is not undefined)
      if (result !== undefined) {
        // Close dialog and clear selection
        setDeleteDialogOpen(false);
        setSelectedFund(null);
        setFundIdToDelete(0); // Reset fundId
        
        // Add small delay before refetch to ensure backend has processed the deletion
        setTimeout(() => {
          // Refresh the overview data
          refetchOverview();
          // Refresh the funds data (this is what displays the funds list!)
          refetchFunds();
        }, 500);
      } else {
        // Deletion failed - error is available from the hook's error state
        // We'll handle it in the error display
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
    setFundIdToDelete(0); // Reset fundId
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
          ariaLabel="Company navigation tabs"
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
            data={fundsTabData}
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
      <CreateFundModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onFundCreated={handleFundCreated}
        companyId={companyIdNum}
        companyName={overviewData.company.name}
      />

      {/* Fund Deletion Confirmation Dialog */}
      <ConfirmDialog
        open={deleteDialogOpen}
        title="Delete Fund"
        description={
          deletionError 
            ? `Cannot delete fund "${selectedFund?.name}". ${deletionError}`
            : `Are you sure you want to delete the fund "${selectedFund?.name}"? This action cannot be undone.`
        }
        confirmAction={{
          label: deletionError ? "OK" : "Delete",
          variant: deletionError ? "primary" : "error",
          onClick: deletionError ? cancelDeleteFund : confirmDeleteFund,
          loading: isDeletingFund || deletingFund,
        }}
        {...(deletionError ? {} : {
          cancelAction: {
            label: "Cancel",
            variant: "outlined",
            onClick: cancelDeleteFund,
          }
        })}
      />
    </Box>
  );
};

export default CompanyPage;

