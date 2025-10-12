/**
 * NAV Update Form (React Hook Form + Zod)
 * 
 * Migrated form component using enterprise-grade form management.
 * Demonstrates the new pattern for all form migrations.
 * 
 * Key Improvements over old implementation:
 * - Schema-based validation (Zod) with full type safety
 * - Self-contained form state (no parent state management)
 * - Direct mutation hook integration
 * - Consistent validation display rules
 * - Reduced code complexity
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import { useForm, navUpdateSchema, transformNavUpdateForm, type NavUpdateFormData } from '@/hooks/forms';
import { FormDateField, FormNumberField, FormTextField } from '@/components/forms';
import { useCreateNavUpdate } from '@/hooks/data/funds/useFundEvents';

interface NavUpdateFormProps {
  /** Fund ID for the NAV update */
  fundId: number;
  
  /** Callback when form is successfully submitted */
  onSuccess: () => void;
  
  /** Callback when form is cancelled */
  onCancel: () => void;
}

/**
 * Field configurations for NAV Update form
 * Defines UI metadata (labels, help text) separate from validation
 */
const navFieldConfig = {
  event_date: { 
    label: 'Event Date', 
    helpText: 'Date of the NAV update' 
  },
  nav_per_share: { 
    label: 'NAV per Share', 
    helpText: 'Net Asset Value per share (must be positive)' 
  },
  description: { 
    label: 'Description', 
    helpText: 'Optional notes about this NAV update' 
  },
  reference_number: {
    label: 'Reference Number',
    helpText: 'Optional reference or transaction ID'
  }
};

/**
 * NAV Update Form Component
 * 
 * Self-contained form that handles its own state, validation, and submission.
 * Uses React Hook Form + Zod for enterprise-grade form management.
 */
const NavUpdateForm: React.FC<NavUpdateFormProps> = ({
  fundId,
  onSuccess,
  onCancel
}) => {
  // Mutation hook for creating NAV updates
  const { mutate: createNavUpdate, loading: isSubmitting } = useCreateNavUpdate(fundId);
  
  // Form management with React Hook Form + Zod
  const form = useForm<NavUpdateFormData>({
    schema: navUpdateSchema,
    fieldConfig: navFieldConfig,
    defaultValues: {
      event_date: new Date().toISOString().slice(0, 10), // Today's date
      nav_per_share: 0,
      description: '',
      reference_number: ''
    },
    onSubmit: async (data) => {
      // Transform form data to API request using explicit transformer
      const request = transformNavUpdateForm(data);
      
      // Submit to backend via mutation hook
      await createNavUpdate(request);
      
      // Call success callback
      onSuccess();
    }
  });

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
        {/* Event Date Field - Required */}
        <FormDateField
          name="event_date"
          control={form.control}
          label={navFieldConfig.event_date.label}
          required={true}
          helperText={navFieldConfig.event_date.helpText}
          fullWidth
        />
        
        {/* Description Field - Optional */}
        <FormTextField
          name="description"
          control={form.control}
          label={navFieldConfig.description.label}
          required={false}
          helperText={navFieldConfig.description.helpText}
          textFieldProps={{
            multiline: true,
            rows: 1
          }}
        />
        
        {/* NAV per Share Field - Required */}
        <FormNumberField
          name="nav_per_share"
          control={form.control}
          label={navFieldConfig.nav_per_share.label}
          required={true}
          helperText={navFieldConfig.nav_per_share.helpText}
          allowDecimals={true}
          allowNegative={false}
          fullWidth
        />
        
        {/* Reference Number Field - Optional */}
        <FormTextField
          name="reference_number"
          control={form.control}
          label={navFieldConfig.reference_number.label}
          required={false}
          helperText={navFieldConfig.reference_number.helpText}
        />
      </Box>
    </Box>
  );
};

export default NavUpdateForm;

