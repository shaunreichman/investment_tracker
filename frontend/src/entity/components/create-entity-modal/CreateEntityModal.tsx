import React, { useEffect } from 'react';
import { Box, TextField, FormControl, InputLabel, Select, MenuItem, FormHelperText } from '@mui/material';
import { Controller } from 'react-hook-form';
import { FormProvider } from 'react-hook-form';
import { useCreateEntity } from '@/entity/hooks';
import { SuccessBanner, FormModal } from '@/shared/ui';
import { useForm } from '@/shared/hooks/forms';
import { createEntitySchema, type CreateEntityFormData } from '@/entity/hooks/schemas';
import { transformCreateEntityForm } from '@/entity/hooks/transformers';
import { EntityType } from '@/entity/types';
import { Country } from '@/shared/types';
import { ENTITY_TYPE_LABELS } from '@/entity/utils/labels';
import { COUNTRY_LABELS } from '@/shared/utils/formatters/labels';

interface CreateEntityModalProps {
  open: boolean;
  onClose: () => void;
  onEntityCreated: (entity: { id: number; name: string }) => void;
}

const CreateEntityModal: React.FC<CreateEntityModalProps> = ({
  open,
  onClose,
  onEntityCreated
}) => {
  // Centralized API hook
  const { mutate: createEntity, loading: isSubmitting, error: submitError, data: createdEntity } = useCreateEntity();

  // React Hook Form with Zod validation
  const form = useForm<CreateEntityFormData>({
    schema: createEntitySchema,
    defaultValues: {
      name: '',
      description: undefined,
      entity_type: EntityType.PERSON,
      tax_jurisdiction: Country.AU
    },
    onSubmit: async (data) => {
      // Transform form data to API request format
      const requestData = transformCreateEntityForm(data);
      await createEntity(requestData);
    }
  });

  // Handle success flow when entity is created
  useEffect(() => {
    if (createdEntity) {
      onEntityCreated({
        id: createdEntity.id,
        name: createdEntity.name
      });
      onClose();
      form.reset();
    }
  }, [createdEntity, onEntityCreated, onClose, form]);

  // Reset form when modal opens
  useEffect(() => {
    if (open) {
      form.reset({
        name: '',
        description: undefined,
        entity_type: EntityType.PERSON,
        tax_jurisdiction: Country.AU
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
        title="Create New Entity"
        subtitle="Enter the details for the new entity"
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
        {createdEntity && (
          <SuccessBanner 
            title="Entity created successfully!" 
            subtitle={`Entity ${createdEntity.name} added to the Investment Tracker!`}
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
            {/* Entity Name */}
            <Box sx={{ gridColumn: { xs: '1 / -1', sm: '1 / -1' } }}>
              <Controller
                name="name"
                control={form.control}
                render={({ field, fieldState }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Entity Name"
                    placeholder="Enter entity name"
                    required
                    disabled={isSubmitting || form.formState.isSubmitting}
                    error={!!fieldState.error && fieldState.isTouched}
                    helperText={
                      fieldState.error && fieldState.isTouched
                        ? fieldState.error.message
                        : 'Entity name must be 2-255 characters'
                    }
                    size="medium"
                  />
                )}
              />
            </Box>

            {/* Entity Type */}
            <Box>
              <Controller
                name="entity_type"
                control={form.control}
                render={({ field, fieldState }) => (
                  <FormControl 
                    fullWidth 
                    error={!!fieldState.error && fieldState.isTouched}
                  >
                    <InputLabel id="entity-type-select-label">Entity Type</InputLabel>
                    <Select
                      {...field}
                      labelId="entity-type-select-label"
                      id="entity-type-select"
                      label="Entity Type"
                      value={field.value}
                      disabled={isSubmitting || form.formState.isSubmitting}
                    >
                      {Object.entries(ENTITY_TYPE_LABELS).map(([value, label]) => (
                        <MenuItem key={value} value={value}>
                          {label}
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

            {/* Tax Jurisdiction */}
            <Box>
              <Controller
                name="tax_jurisdiction"
                control={form.control}
                render={({ field, fieldState }) => (
                  <FormControl 
                    fullWidth 
                    error={!!fieldState.error && fieldState.isTouched}
                  >
                    <InputLabel id="tax-jurisdiction-select-label">Tax Jurisdiction</InputLabel>
                    <Select
                      {...field}
                      labelId="tax-jurisdiction-select-label"
                      id="tax-jurisdiction-select"
                      label="Tax Jurisdiction"
                      value={field.value}
                      disabled={isSubmitting || form.formState.isSubmitting}
                    >
                      {Object.entries(COUNTRY_LABELS).map(([value, label]) => (
                        <MenuItem key={value} value={value}>
                          {label}
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
                    placeholder="Enter entity description (optional)"
                    helperText={
                      fieldState.error && fieldState.isTouched
                        ? fieldState.error.message
                        : 'Optional description for the entity (max 1000 characters)'
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

export default CreateEntityModal;

