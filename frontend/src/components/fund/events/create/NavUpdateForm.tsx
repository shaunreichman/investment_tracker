import React from 'react';
import { TextField, Box, Typography } from '@mui/material';

interface NavUpdateFormProps {
  formData: {
    nav_per_share?: string;
  };
  validationErrors: {
    nav_per_share?: string;
  };
  onInputChange: (field: string, value: string) => void;
}

const NavUpdateForm: React.FC<NavUpdateFormProps> = ({
  formData,
  validationErrors,
  onInputChange,
}) => {
  return (
    <Box>
      <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
        NAV Update Details
      </Typography>
      
      <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
        <TextField
          label={<span>NAV Per Share <span style={{ color: '#d32f2f' }}>*</span></span>}
          type="number"
          value={formData.nav_per_share || ''}
          onChange={e => onInputChange('nav_per_share', e.target.value)}
          fullWidth
          error={!!validationErrors.nav_per_share}
          helperText={validationErrors.nav_per_share}
          inputProps={{
            min: 0,
            step: 'any'
          }}
        />
      </Box>
    </Box>
  );
};

export default NavUpdateForm; 