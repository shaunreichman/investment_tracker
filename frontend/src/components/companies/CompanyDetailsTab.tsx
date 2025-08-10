import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Link,
  Chip,
  Divider,
} from '@mui/material';
import {
  Business,
  Language,
  Phone,
  Email,
  LocationOn,
  Description,
} from '@mui/icons-material';
import { CompanyDetailsResponse } from '../../types/api';

// ============================================================================
// TYPES
// ============================================================================

interface CompanyDetailsTabProps {
  data: CompanyDetailsResponse;
  loading: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

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

          {/* Company Details Grid */}
          <Box 
            display="grid" 
            gap={3} 
            sx={{ 
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }
            }}
          >
            {/* Contact Information */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Contact Information
              </Typography>
              
              {company.website && (
                <Box display="flex" alignItems="center" mb={2}>
                  <Language sx={{ mr: 2, color: 'text.secondary' }} />
                  <Link href={company.website} target="_blank" rel="noopener noreferrer">
                    {company.website}
                  </Link>
                </Box>
              )}

              {company.direct_emails && (
                <Box display="flex" alignItems="center" mb={2}>
                  <Email sx={{ mr: 2, color: 'text.secondary' }} />
                  <Typography variant="body2">
                    {company.direct_emails}
                  </Typography>
                </Box>
              )}

              {company.direct_numbers && (
                <Box display="flex" alignItems="center" mb={2}>
                  <Phone sx={{ mr: 2, color: 'text.secondary' }} />
                  <Typography variant="body2">
                    {company.direct_numbers}
                  </Typography>
                </Box>
              )}

              {company.business_address && (
                <Box display="flex" alignItems="center" mb={2}>
                  <LocationOn sx={{ mr: 2, color: 'text.secondary' }} />
                  <Typography variant="body2">
                    {company.business_address}
                  </Typography>
                </Box>
              )}
            </Box>

            {/* Additional Information */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Additional Information
              </Typography>
              
              {company.contracts && (
                <Box display="flex" alignItems="center" mb={2}>
                  <Description sx={{ mr: 2, color: 'text.secondary' }} />
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Contract Information
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {company.contracts}
                    </Typography>
                  </Box>
                </Box>
              )}

              {/* Company Statistics */}
              <Box mt={3}>
                <Typography variant="h6" gutterBottom>
                  Company Statistics
                </Typography>
                <Box display="grid" gap={2} sx={{ gridTemplateColumns: '1fr 1fr' }}>
                  <Box textAlign="center" p={2} sx={{ bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="h6" color="primary.main">
                      {/* TODO: Add fund count when available */}
                      -
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Total Funds
                    </Typography>
                  </Box>
                  <Box textAlign="center" p={2} sx={{ bgcolor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="h6" color="success.main">
                      {/* TODO: Add active fund count when available */}
                      -
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Active Funds
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Empty State for No Additional Data */}
      {!company.website && !company.direct_emails && !company.direct_numbers && 
       !company.business_address && !company.contracts && (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <Business sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                Limited Company Information
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Additional company details can be added to provide more context.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};
