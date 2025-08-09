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
import { Entity } from '../../../types/api';
import { formatNumber, parseNumber } from '../../../utils/helpers';

export interface ValidationErrors {
  entity_id?: string;
  name?: string;
  fund_type?: string;
  tracking_type?: string;
  commitment_amount?: string;
  expected_irr?: string;
  expected_duration_months?: string;
  description?: string;
}

export interface CreateFundFormData {
  entity_id: string;
  name: string;
  fund_type: string;
  tracking_type: string;
  currency: string;
  commitment_amount: string;
  expected_irr: string;
  expected_duration_months: string;
  description: string;
}

interface FundFormSectionProps {
  formData: CreateFundFormData;
  validationErrors: ValidationErrors;
  entities: Entity[] | undefined;
  onInputChange: (field: string, value: string) => void;
  onCreateEntity: () => void;
}

const FundFormSection: React.FC<FundFormSectionProps> = ({
  formData,
  validationErrors,
  entities,
  onInputChange,
  onCreateEntity
}) => {
  return (
    <Box display="grid" gap={3} sx={{ gridTemplateColumns: '1fr 1fr' }}>
      {/* Entity Selection */}
      <FormControl fullWidth error={!!validationErrors.entity_id} required>
        <InputLabel>Entity *</InputLabel>
        <Select
          value={formData.entity_id}
          onChange={(e) => onInputChange('entity_id', e.target.value as string)}
          label="Entity *"
        >
          {entities?.map((entity) => (
            <MenuItem key={entity.id} value={entity.id}>
              {entity.name}
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
        {validationErrors.entity_id && (
          <FormHelperText error>{validationErrors.entity_id}</FormHelperText>
        )}
      </FormControl>

      {/* Fund Name */}
      <TextField
        fullWidth
        label="Fund Name *"
        value={formData.name}
        onChange={(e) => onInputChange('name', e.target.value)}
        error={!!validationErrors.name}
        helperText={validationErrors.name || 'Enter a unique fund name (2-255 characters)'}
        required
      />

      {/* Fund Type */}
      <FormControl fullWidth error={!!validationErrors.fund_type} required>
        <InputLabel>Fund Type *</InputLabel>
        <Select
          value={formData.fund_type}
          onChange={(e) => onInputChange('fund_type', e.target.value as string)}
          label="Fund Type *"
        >
          <MenuItem value="Private Equity">Private Equity</MenuItem>
          <MenuItem value="Private Debt">Private Debt</MenuItem>
          <MenuItem value="Venture Capital">Venture Capital</MenuItem>
          <MenuItem value="Real Estate">Real Estate</MenuItem>
          <MenuItem value="Infrastructure">Infrastructure</MenuItem>
          <MenuItem value="Hedge Fund">Hedge Fund</MenuItem>
          <MenuItem value="Equity - Consumer Discretionary">Equity - Consumer Discretionary</MenuItem>
          <MenuItem value="Equity - Technology">Equity - Technology</MenuItem>
          <MenuItem value="Equity - Financial">Equity - Financial</MenuItem>
          <MenuItem value="Other">Other</MenuItem>
        </Select>
        {validationErrors.fund_type && (
          <FormHelperText error>{validationErrors.fund_type}</FormHelperText>
        )}
      </FormControl>

      {/* Tracking Type */}
      <FormControl fullWidth error={!!validationErrors.tracking_type} required>
        <InputLabel>Tracking Type *</InputLabel>
        <Select
          value={formData.tracking_type}
          onChange={(e) => onInputChange('tracking_type', e.target.value as string)}
          label="Tracking Type *"
        >
          <MenuItem value="nav_based">NAV-Based (Units & NAV)</MenuItem>
          <MenuItem value="cost_based">Cost-Based (Capital Calls)</MenuItem>
        </Select>
        {validationErrors.tracking_type && (
          <FormHelperText error>{validationErrors.tracking_type}</FormHelperText>
        )}
      </FormControl>

      {/* Currency */}
      <FormControl fullWidth>
        <InputLabel>Currency</InputLabel>
        <Select
          value={formData.currency}
          onChange={(e) => onInputChange('currency', e.target.value as string)}
          label="Currency"
        >
          <MenuItem value="AUD">AUD</MenuItem>
          <MenuItem value="USD">USD</MenuItem>
          <MenuItem value="EUR">EUR</MenuItem>
          <MenuItem value="GBP">GBP</MenuItem>
        </Select>
      </FormControl>

      {/* Commitment Amount */}
      <TextField
        fullWidth
        label="Commitment Amount"
        value={formatNumber(formData.commitment_amount)}
        onChange={(e) => onInputChange('commitment_amount', parseNumber(e.target.value))}
        error={!!validationErrors.commitment_amount}
        helperText={validationErrors.commitment_amount || 'Total commitment amount (optional)'}
        inputProps={{
          style: { textAlign: 'left' }
        }}
      />

      {/* Expected IRR */}
      <TextField
        fullWidth
        label="Expected IRR (%)"
        type="number"
        value={formData.expected_irr}
        onChange={(e) => onInputChange('expected_irr', e.target.value)}
        error={!!validationErrors.expected_irr}
        helperText={validationErrors.expected_irr || 'Expected annual return 0-100% (optional)'}
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

      {/* Expected Duration */}
      <TextField
        fullWidth
        label="Expected Duration (months)"
        type="number"
        value={formData.expected_duration_months}
        onChange={(e) => onInputChange('expected_duration_months', e.target.value)}
        error={!!validationErrors.expected_duration_months}
        helperText={validationErrors.expected_duration_months || 'Expected fund duration 1-1200 months (optional)'}
      />

      {/* Description */}
      <TextField
        fullWidth
        label="Description"
        multiline
        minRows={3}
        maxRows={6}
        value={formData.description}
        onChange={(e) => onInputChange('description', e.target.value)}
        error={!!validationErrors.description}
        helperText={validationErrors.description || 'Optional fund description (max 1000 characters)'}
        sx={{ gridColumn: '1 / -1' }}
        variant="outlined"
      />
    </Box>
  );
};

export default FundFormSection;


