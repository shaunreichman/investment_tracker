/**
 * AllCompaniesPage Component
 * 
 * Page component for displaying all companies.
 * Handles data fetching and passes data to CompanyList component.
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  useTheme,
} from '@mui/material';
import { Business } from '@mui/icons-material';
import { useCompanies } from '../hooks';
import { CompanyList } from '../components';

/**
 * AllCompaniesPage Component
 * 
 * Main page for displaying all companies. This page:
 * - Fetches company data using useCompanies() hook
 * - Passes data, loading, error, and onRefresh to CompanyList component
 * - Handles only company-related content (entity management removed)
 */
const AllCompaniesPage: React.FC = () => {
  const theme = useTheme();
  
  // Fetch companies data
  const { data, loading, error, refetch } = useCompanies();

  // Handle refresh callback
  const handleRefresh = async () => {
    await refetch();
  };

  return (
    <Box sx={{ p: 0 }}>
      {/* Page Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h3" 
          sx={{ 
            color: theme.palette.text.primary,
            fontWeight: 600,
            mb: 1,
            letterSpacing: '-0.02em'
          }}
        >
          Companies
        </Typography>
        
        <Typography 
          variant="body1" 
          sx={{ 
            color: theme.palette.text.secondary,
            fontSize: '16px',
            lineHeight: 1.5
          }}
        >
          Overview of all companies and their managed funds
        </Typography>
      </Box>

      {/* Companies Portfolio - Using CompanyList Component */}
      <Card sx={{ 
        backgroundColor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.divider}`,
        mb: 4
      }}>
        <CardContent sx={{ p: 3 }}>
          <Typography 
            variant="h5" 
            sx={{ 
              color: theme.palette.text.primary,
              fontWeight: 600,
              mb: 3,
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <Business sx={{ mr: 2, color: theme.palette.primary.main, fontSize: '28px' }} />
            Companies Portfolio
          </Typography>
          
          {/* CompanyList Component - receives data via props */}
          <CompanyList 
            data={data?.companies ?? null}
            loading={loading}
            error={error}
            onRefresh={handleRefresh}
          />
        </CardContent>
      </Card>
    </Box>
  );
};

export default AllCompaniesPage;

