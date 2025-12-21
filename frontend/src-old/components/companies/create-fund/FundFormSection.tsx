import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  FormHelperText,
  Divider,
  InputAdornment,
  Typography
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { Controller, Control, FieldValues } from 'react-hook-form';
import { Entity } from '../../../types/api';
import { FundTrackingType, FundInvestmentType } from '@/fund/types';
import { Country, Currency } from '@/shared/types';
import { FUND_TYPES } from '@/fund/utils/constants/fundOptions';
import { COUNTRY_LABELS } from '@/shared/utils/formatters/labels';
import { CURRENCY_LABELS } from '@/shared/utils/formatters/labels';
import { NumberInputField } from '../../shared/forms';
import { useNumberInput } from '@/shared/hooks/forms';
import type { CreateFundFormData } from '@/fund/hooks/schemas';

interface FundFormSectionProps {
  control: Control<CreateFundFormData>;
  entities: Entity[] | undefined;
  onCreateEntity: () => void;
  trackingTypeLocked?: boolean;
}

const FundFormSection: React.FC<FundFormSectionProps> = ({
  control,
  entities,
  onCreateEntity,
  trackingTypeLocked
}) => {
  // Create options arrays for selects
  const entityOptions = entities?.map(entity => ({
    value: entity.id,
    label: entity.name
  })) || [];

  const trackingTypeOptions = [
    { value: FundTrackingType.NAV_BASED, label: 'NAV-Based (Units & NAV)' },
    { value: FundTrackingType.COST_BASED, label: 'Cost-Based (Capital Calls)' },
  ];

  const countryOptions = Object.entries(COUNTRY_LABELS).map(([value, label]) => ({
    value: value as Country,
    label
  }));

  const currencyOptions = Object.entries(CURRENCY_LABELS).map(([value, label]) => ({
    value: value as Currency,
    label: `${label} (${value})`
  }));

  return (
    <Box display="grid" gap={3} sx={{ gridTemplateColumns: '1fr 1fr' }}>
      {/* Entity Selection */}
      <Controller
        name="entity_id"
        control={control}
        render={({ field, fieldState }) => (
          <FormControl fullWidth error={!!fieldState.error && fieldState.isTouched} required>
            <InputLabel id="entity-select-label">Entity *</InputLabel>
            <Select
              {...field}
              labelId="entity-select-label"
              id="entity-select"
              label="Entity *"
              value={field.value || ''}
              onChange={(e) => field.onChange(Number(e.target.value))}
            >
              {entityOptions.map((option) => (
                <MenuItem key={String(option.value)} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
              <Divider />
              <MenuItem
                value="create_new"
                onClick={onCreateEntity}
                sx={{ color: 'primary.main', fontStyle: 'italic' }}
              >
                <AddIcon sx={{ mr: 1, fontSize: 16 }} />
                Create New Entity...
              </MenuItem>
            </Select>
            {fieldState.error && fieldState.isTouched && (
              <FormHelperText error>{fieldState.error.message}</FormHelperText>
            )}
          </FormControl>
        )}
      />

      {/* Fund Name */}
      <Controller
        name="name"
        control={control}
        render={({ field, fieldState }) => (
          <TextField
            {...field}
            fullWidth
            label="Fund Name *"
            error={!!fieldState.error && fieldState.isTouched}
            helperText={
              fieldState.error && fieldState.isTouched
                ? fieldState.error.message
                : 'Enter a unique fund name (2-255 characters)'
            }
            required
          />
        )}
      />

      {/* Fund Investment Type */}
      <Controller
        name="fund_investment_type"
        control={control}
        render={({ field, fieldState }) => (
          <FormControl fullWidth error={!!fieldState.error && fieldState.isTouched}>
            <InputLabel id="fund-investment-type-select-label">Fund Investment Type</InputLabel>
            <Select
              {...field}
              labelId="fund-investment-type-select-label"
              id="fund-investment-type-select"
              label="Fund Investment Type"
              value={field.value || ''}
            >
              {FUND_TYPES.map((option) => (
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

      {/* Tracking Type */}
      <Controller
        name="tracking_type"
        control={control}
        render={({ field, fieldState }) => (
          <FormControl fullWidth error={!!fieldState.error && fieldState.isTouched} required>
            <InputLabel id="tracking-type-select-label">Tracking Type *</InputLabel>
            <Select
              {...field}
              labelId="tracking-type-select-label"
              id="tracking-type-select"
              label="Tracking Type *"
              disabled={!!trackingTypeLocked}
            >
              {trackingTypeOptions.map((option) => (
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

      {/* Tax Jurisdiction */}
      <Controller
        name="tax_jurisdiction"
        control={control}
        render={({ field, fieldState }) => (
          <FormControl fullWidth error={!!fieldState.error && fieldState.isTouched} required>
            <InputLabel id="tax-jurisdiction-select-label">Tax Jurisdiction *</InputLabel>
            <Select
              {...field}
              labelId="tax-jurisdiction-select-label"
              id="tax-jurisdiction-select"
              label="Tax Jurisdiction *"
            >
              {countryOptions.map((option) => (
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

      {/* Currency */}
      <Controller
        name="currency"
        control={control}
        render={({ field, fieldState }) => (
          <FormControl fullWidth error={!!fieldState.error && fieldState.isTouched} required>
            <InputLabel id="currency-select-label">Currency *</InputLabel>
            <Select
              {...field}
              labelId="currency-select-label"
              id="currency-select"
              label="Currency *"
            >
              {currencyOptions.map((option) => (
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

      {/* Commitment Amount */}
      <Controller
        name="commitment_amount"
        control={control}
        render={({ field, fieldState }) => {
          const numberInput = useNumberInput(
            field.value?.toString() || '',
            { allowDecimals: true, allowNegative: false }
          );

          return (
            <Box>
              <TextField
                fullWidth
                label="Commitment Amount"
                type="text"
                value={numberInput.value}
                onChange={(e) => {
                  numberInput.onChange(e.target.value);
                  const numValue = numberInput.numericValue;
                  field.onChange(numValue > 0 ? numValue : undefined);
                }}
                onBlur={() => {
                  numberInput.onBlur();
                  const numValue = numberInput.numericValue;
                  field.onChange(numValue > 0 ? numValue : undefined);
                }}
                onFocus={numberInput.onFocus}
                error={!!fieldState.error && fieldState.isTouched}
                helperText={
                  fieldState.error && fieldState.isTouched
                    ? fieldState.error.message
                    : 'Total commitment amount (optional)'
                }
                inputProps={{
                  style: { textAlign: 'left' }
                }}
              />
            </Box>
          );
        }}
      />

      {/* Expected IRR */}
      <Controller
        name="expected_irr"
        control={control}
        render={({ field, fieldState }) => {
          const numberInput = useNumberInput(
            field.value?.toString() || '',
            { allowDecimals: true, allowNegative: false }
          );

          return (
            <TextField
              fullWidth
              label="Expected IRR (%)"
              type="text"
              value={numberInput.value}
              onChange={(e) => {
                numberInput.onChange(e.target.value);
                const numValue = numberInput.numericValue;
                field.onChange(numValue >= 0 ? numValue : undefined);
              }}
              onBlur={() => {
                numberInput.onBlur();
                const numValue = numberInput.numericValue;
                field.onChange(numValue >= 0 ? numValue : undefined);
              }}
              onFocus={numberInput.onFocus}
              error={!!fieldState.error && fieldState.isTouched}
              helperText={
                fieldState.error && fieldState.isTouched
                  ? fieldState.error.message
                  : 'Expected annual return 0-100% (optional)'
              }
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <Typography variant="body2" color="text.secondary">
                      %
                    </Typography>
                  </InputAdornment>
                )
              }}
            />
          );
        }}
      />

      {/* Expected Duration */}
      <Controller
        name="expected_duration_months"
        control={control}
        render={({ field, fieldState }) => {
          const numberInput = useNumberInput(
            field.value?.toString() || '',
            { allowDecimals: false, allowNegative: false }
          );

          return (
            <TextField
              fullWidth
              label="Expected Duration (months)"
              type="text"
              value={numberInput.value}
              onChange={(e) => {
                numberInput.onChange(e.target.value);
                const numValue = Math.floor(numberInput.numericValue);
                field.onChange(numValue >= 0 ? numValue : undefined);
              }}
              onBlur={() => {
                numberInput.onBlur();
                const numValue = Math.floor(numberInput.numericValue);
                field.onChange(numValue >= 0 ? numValue : undefined);
              }}
              onFocus={numberInput.onFocus}
              error={!!fieldState.error && fieldState.isTouched}
              helperText={
                fieldState.error && fieldState.isTouched
                  ? fieldState.error.message
                  : 'Expected fund duration 1-1200 months (optional)'
              }
            />
          );
        }}
      />

      {/* Description */}
      <Controller
        name="description"
        control={control}
        render={({ field, fieldState }) => (
          <TextField
            {...field}
            fullWidth
            label="Description"
            multiline
            minRows={3}
            maxRows={6}
            error={!!fieldState.error && fieldState.isTouched}
            helperText={
              fieldState.error && fieldState.isTouched
                ? fieldState.error.message
                : 'Optional fund description (max 1000 characters)'
            }
            sx={{ gridColumn: '1 / -1' }}
            variant="outlined"
          />
        )}
      />
    </Box>
  );
};

export default FundFormSection;
