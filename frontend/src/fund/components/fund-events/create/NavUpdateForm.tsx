import React from 'react';
import { TextField, Box, Typography, useTheme } from '@mui/material';
import { NumberInputField } from '@/shared/ui';

interface NavUpdateFormProps {
  formData: {
    event_date?: string;
    nav_per_share?: string;
    description?: string;
  };
  validationErrors: {
    event_date?: string;
    nav_per_share?: string;
    description?: string;
  };
  onInputChange: (field: string, value: string) => void;
}

const NavUpdateForm: React.FC<NavUpdateFormProps> = ({
  formData,
  validationErrors,
  onInputChange,
}) => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        animation: 'fadeInUp 0.5s ease-out 0.1s both',
        '@keyframes fadeInUp': {
          '0%': {
            opacity: 0,
            transform: 'translateY(30px)',
          },
          '100%': {
            opacity: 1,
            transform: 'translateY(0)',
          }
        }
      }}
    >
      <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
        NAV Update Details
      </Typography>
      
      <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
        <TextField
          label={<span>Event Date <span style={{ color: theme.palette.error.main }}>*</span></span>}
          type="date"
          value={formData.event_date || ''}
          onChange={(e) => onInputChange('event_date', e.target.value)}
          fullWidth
          error={!!validationErrors.event_date}
          helperText={validationErrors.event_date}
          InputLabelProps={{ shrink: true }}
        />
        
        <TextField
          label="Description (Optional)"
          value={formData.description || ''}
          onChange={(e) => onInputChange('description', e.target.value)}
          fullWidth
          error={!!validationErrors.description}
          helperText={validationErrors.description}
        />
        
        <NumberInputField
          label={<span>NAV per Share <span style={{ color: theme.palette.error.main }}>*</span></span>}
          value={formData.nav_per_share || ''}
          onInputChange={onInputChange}
          fieldName="nav_per_share"
          allowDecimals={true}
          allowNegative={false}
          fullWidth
          error={!!validationErrors.nav_per_share}
          helperText={validationErrors.nav_per_share}
        />
      </Box>
    </Box>
  );
};

export default NavUpdateForm; 