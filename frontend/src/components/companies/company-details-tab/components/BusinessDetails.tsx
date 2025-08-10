import React from 'react';
import {
  Box,
  Typography,
  Divider,
} from '@mui/material';
import { LocationOn, Description } from '@mui/icons-material';
import { BusinessDetailsProps } from '../types/company-details-tab.types';

export const BusinessDetails: React.FC<BusinessDetailsProps> = ({ company }) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Business Details
      </Typography>
      
      {company.business_address && (
        <Box display="flex" alignItems="flex-start" mb={2}>
          <LocationOn sx={{ mr: 2, color: 'text.secondary', mt: 0.5 }} />
          <Box>
            <Typography variant="body2" color="textSecondary">
              {company.business_address}
            </Typography>
          </Box>
        </Box>
      )}
      

      
      <Divider sx={{ my: 2 }} />
    </Box>
  );
};
