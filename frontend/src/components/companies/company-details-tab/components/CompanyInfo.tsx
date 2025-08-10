import React from 'react';
import {
  Box,
  Typography,
  Chip,
} from '@mui/material';
import { Business } from '@mui/icons-material';
import { CompanyInfoProps } from '../types/company-details-tab.types';

export const CompanyInfo: React.FC<CompanyInfoProps> = ({ company }) => {
  return (
    <Box display="flex" alignItems="center" mb={3}>
      <Business sx={{ mr: 2, color: 'primary.main', fontSize: 32 }} />
      <Box>
        <Typography variant="h4" gutterBottom>
          {company.name}
        </Typography>
        {company.company_type && (
          <Chip 
            label={company.company_type} 
            color="primary" 
            variant="outlined"
            size="small"
          />
        )}
      </Box>
    </Box>
  );
};
