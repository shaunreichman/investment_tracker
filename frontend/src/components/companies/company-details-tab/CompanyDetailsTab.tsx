// ============================================================================
// COMPANY DETAILS TAB COMPONENT (REFACTORED)
// ============================================================================

import React from 'react';
import { Box, Card, CardContent, Typography } from '@mui/material';
import { CompanyDetailsTabProps } from './types/company-details-tab.types';
import { CompanyInfo } from './components/CompanyInfo';
import { ContactInfo } from './components/ContactInfo';
import { BusinessDetails } from './components/BusinessDetails';

export const CompanyDetailsTab: React.FC<CompanyDetailsTabProps> = ({ data, loading }) => {
  if (loading) {
    return (
      <Box p={3}>
        <Typography>Loading company details...</Typography>
      </Box>
    );
  }

  const { company } = data;

  return (
    <Box p={3}>
      {/* Company Information */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <CompanyInfo company={company} />
          
          {/* Company Details Grid */}
          <Box 
            display="grid" 
            gap={3} 
            sx={{ 
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }
            }}
          >
            {/* Contact Information */}
            <ContactInfo 
              contacts={company.contacts}
              website={company.website}
            />

            {/* Business Details */}
            <BusinessDetails company={company} />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
