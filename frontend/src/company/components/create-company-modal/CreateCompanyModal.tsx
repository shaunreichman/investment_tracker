import React, { useEffect } from 'react';
import { Box, TextField, FormControl, InputLabel, Select, MenuItem, FormHelperText } from '@mui/material';
import { Controller } from 'react-hook-form';
import { FormProvider } from 'react-hook-form';
import { useCreateCompany } from '@/company/hooks';
import { SuccessBanner, FormModal } from '@/shared/ui';
import { useForm } from '@/shared/hooks/forms';
import { createCompanySchema, type CreateCompanyFormData } from '@/company/hooks/schemas';
import { transformCreateCompanyForm } from '@/company/hooks/transformers';
import { CompanyType } from '@/company/types';

interface CreateCompanyModalProps {
  open: boolean;
  onClose: () => void;
  onCompanyCreated: (company: { id: number; name: string }) => void;
}

// Company type options for select dropdown
const COMPANY_TYPE_OPTIONS = Object.values(CompanyType).map(value => ({
  value,
  label: value
}));

const CreateCompanyModal: React.FC<CreateCompanyModalProps> = ({
  open,
  onClose,
  onCompanyCreated
}) => {
  // Centralized API hook
  const { mutate: createCompany, loading: isSubmitting, error: submitError, data: createdCompany } = useCreateCompany();

  // React Hook Form with Zod validation
  const form = useForm<CreateCompanyFormData>({
    schema: createCompanySchema,
    defaultValues: {
      name: '',
      description: undefined,
      company_type: undefined,
      website: undefined,
      business_address: undefined
    },
    onSubmit: async (data) => {
      // Transform form data to API request format
      const requestData = transformCreateCompanyForm(data);
      await createCompany(requestData);
    }
  });

  // Handle success flow when company is created
  useEffect(() => {
    if (createdCompany) {
      onCompanyCreated({
        id: createdCompany.id,
        name: createdCompany.name
      });
      onClose();
      form.reset();
    }
  }, [createdCompany, onCompanyCreated, onClose, form]);

  // Reset form when modal opens
  useEffect(() => {
    if (open) {
      form.reset({
        name: '',
        description: undefined,
        company_type: undefined,
        website: undefined,
        business_address: undefined
      });
    }
  }, [open, form]);

  // Handle form submission
  const handleFormSubmit = () => {
    form.handleSubmit();
  };

  // Handle modal close
  const handleClose = () => {
    if (!isSubmitting && !form.formState.isSubmitting) {
      onClose();
      form.reset();
    }
  };

  return (
    <FormProvider {...(form as any)}>
      <FormModal
        open={open}
        title="Create New Company"
        subtitle="Enter the details for the new company"
        onClose={handleClose}
        onSubmit={handleFormSubmit}
        isSubmitting={isSubmitting || form.formState.isSubmitting}
        isValid={form.formState.isValid}
        isDirty={form.formState.isDirty}
        showCloseConfirmation={true}
        maxWidth="md"
        fullWidth={true}
      >
        {/* Success Banner */}
        {createdCompany && (
          <SuccessBanner 
            title="Company created successfully!" 
            subtitle={`Company ${createdCompany.name} added to the Investment Tracker!`}
          />
        )}

        {/* Error Display */}
        {submitError && (
          <Box sx={{ mb: 2 }}>
            <Box sx={{ p: 2, bgcolor: 'error.light', borderRadius: 1 }}>
              {submitError.userMessage || submitError.message || 'An error occurred'}
            </Box>
          </Box>
        )}

        {/* Form Content */}
        <Box component="form" noValidate autoComplete="off">
          <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
            {/* Company Name */}
            <Box sx={{ gridColumn: { xs: '1 / -1', sm: '1 / -1' } }}>
              <Controller
                name="name"
                control={form.control}
                render={({ field, fieldState }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Company Name"
                    placeholder="Enter company name"
                    required
                    disabled={isSubmitting || form.formState.isSubmitting}
                    error={!!fieldState.error && fieldState.isTouched}
                    helperText={
                      fieldState.error && fieldState.isTouched
                        ? fieldState.error.message
                        : 'Company name must be 2-255 characters'
                    }
                    size="medium"
                  />
                )}
              />
            </Box>

            {/* Company Type */}
            <Box>
              <Controller
                name="company_type"
                control={form.control}
                render={({ field, fieldState }) => (
                  <FormControl 
                    fullWidth 
                    error={!!fieldState.error && fieldState.isTouched}
                  >
                    <InputLabel id="company-type-select-label">Company Type</InputLabel>
                    <Select
                      {...field}
                      labelId="company-type-select-label"
                      id="company-type-select"
                      label="Company Type"
                      value={field.value || ''}
                      disabled={isSubmitting || form.formState.isSubmitting}
                    >
                      <MenuItem value="">
                        <em>None</em>
                      </MenuItem>
                      {COMPANY_TYPE_OPTIONS.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                    {fieldState.error && fieldState.isTouched && (
                      <FormHelperText error>{fieldState.error.message}</FormHelperText>
                    )}
                  </FormControl>
                )}
              />
            </Box>

            {/* Website */}
            <Box>
              <Controller
                name="website"
                control={form.control}
                render={({ field, fieldState }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Website"
                    placeholder="https://example.com"
                    helperText={
                      fieldState.error && fieldState.isTouched
                        ? fieldState.error.message
                        : 'Company website URL (optional)'
                    }
                    disabled={isSubmitting || form.formState.isSubmitting}
                    error={!!fieldState.error && fieldState.isTouched}
                    size="medium"
                  />
                )}
              />
            </Box>

            {/* Business Address */}
            <Box sx={{ gridColumn: { xs: '1 / -1', sm: '1 / -1' } }}>
              <Controller
                name="business_address"
                control={form.control}
                render={({ field, fieldState }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Business Address"
                    placeholder="Enter business address"
                    helperText={
                      fieldState.error && fieldState.isTouched
                        ? fieldState.error.message
                        : 'Business address (optional, max 1000 characters)'
                    }
                    disabled={isSubmitting || form.formState.isSubmitting}
                    error={!!fieldState.error && fieldState.isTouched}
                    size="medium"
                  />
                )}
              />
            </Box>

            {/* Description */}
            <Box sx={{ gridColumn: '1 / -1' }}>
              <Controller
                name="description"
                control={form.control}
                render={({ field, fieldState }) => (
                  <TextField
                    {...field}
                    fullWidth
                    multiline
                    minRows={3}
                    maxRows={6}
                    label="Description"
                    placeholder="Describe the company's investment strategy and focus areas"
                    helperText={
                      fieldState.error && fieldState.isTouched
                        ? fieldState.error.message
                        : 'Company description and investment focus (max 1000 characters)'
                    }
                    disabled={isSubmitting || form.formState.isSubmitting}
                    error={!!fieldState.error && fieldState.isTouched}
                    size="medium"
                  />
                )}
              />
            </Box>
          </Box>
        </Box>
      </FormModal>
    </FormProvider>
  );
};

export default CreateCompanyModal;

