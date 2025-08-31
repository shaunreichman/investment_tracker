import React from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Chip,
  LinearProgress,
  Alert
} from '@mui/material';
import { useEnhancedUnifiedForm } from '../../hooks/forms/useEnhancedUnifiedForm';

interface DemoFormData {
  name: string;
  email: string;
  description: string;
}

const initialFormValues: DemoFormData = {
  name: '',
  email: '',
  description: ''
};

const validators = {
  name: (value: string) => {
    if (!value.trim()) return 'Name is required';
    if (value.trim().length < 2) return 'Name must be at least 2 characters';
    return undefined;
  },
  email: (value: string) => {
    if (!value.trim()) return 'Email is required';
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(value.trim())) return 'Please enter a valid email address';
    return undefined;
  },
  description: (value: string) => {
    if (value && value.trim().length > 500) return 'Description must be less than 500 characters';
    return undefined;
  }
};

export const EnhancedFormDemo: React.FC = () => {
  const {
    values,
    errors,
    touched,
    isDirty,
    isValid,
    isSubmitting,
    dirtyFields,
    hasUnsavedChanges,
    lastModified,
    setFieldValue,
    handleSubmit,
    reset,
    lifecycle
  } = useEnhancedUnifiedForm<DemoFormData>({
    initialValues: initialFormValues,
    validators,
    onSubmit: async (values) => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log('Form submitted:', values);
    },
    onSuccess: () => {
      console.log('Form submitted successfully!');
    },
    onError: (error) => {
      console.error('Form submission failed:', error);
    },
    enableLifecycle: true,
    enableAutoSave: true,
    onAnalyticsEvent: (event, data) => {
      console.log('Analytics event:', event, data);
    }
  });

  return (
    <Paper sx={{ p: 3, maxWidth: 600, mx: 'auto', mt: 3 }}>
      <Typography variant="h5" gutterBottom>
        Enhanced Form Demo - Phase 2 Features
      </Typography>
      
      {/* Lifecycle Status */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Form Lifecycle: {lifecycle.currentState}
        </Typography>
        
        {/* Progress Bar */}
        {lifecycle.progress > 0 && (
          <Box sx={{ mb: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Progress: {Math.round(lifecycle.progress)}%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={lifecycle.progress} 
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        )}
        
        {/* State Indicators */}
        <Box display="flex" gap={1} flexWrap="wrap" sx={{ mb: 2 }}>
          <Chip 
            label={`Can Submit: ${lifecycle.canSubmit}`} 
            color={lifecycle.canSubmit ? 'success' : 'default'}
            size="small"
          />
          <Chip 
            label={`Can Cancel: ${lifecycle.canCancel}`} 
            color={lifecycle.canCancel ? 'success' : 'default'}
            size="small"
          />
          <Chip 
            label={`In Progress: ${lifecycle.isInProgress}`} 
            color={lifecycle.isInProgress ? 'warning' : 'default'}
            size="small"
          />
        </Box>
      </Box>
      
      {/* Dirty State Information */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Form State
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap" sx={{ mb: 2 }}>
          <Chip 
            label={`Dirty: ${isDirty}`} 
            color={isDirty ? 'warning' : 'default'}
            size="small"
          />
          <Chip 
            label={`Valid: ${isValid}`} 
            color={isValid ? 'success' : 'error'}
            size="small"
          />
          <Chip 
            label={`Has Unsaved Changes: ${hasUnsavedChanges}`} 
            color={hasUnsavedChanges ? 'warning' : 'default'}
            size="small"
          />
        </Box>
        
        {lastModified && (
          <Typography variant="caption" color="text.secondary">
            Last modified: {lastModified.toLocaleString()}
          </Typography>
        )}
        
        {/* Dirty Fields */}
        {Object.keys(dirtyFields).length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
              Modified fields:
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {Object.entries(dirtyFields)
                .filter(([_, isDirty]) => isDirty)
                .map(([fieldName, _]) => (
                  <Chip 
                    key={fieldName} 
                    label={fieldName.replace(/_/g, ' ')} 
                    size="small" 
                    variant="outlined"
                    color="warning"
                  />
                ))}
            </Box>
          </Box>
        )}
      </Box>
      
      {/* Form Fields */}
      <Box component="form" noValidate autoComplete="off" sx={{ mb: 3 }}>
        <Box display="grid" gap={2}>
          <TextField
            fullWidth
            label="Name"
            value={values.name}
            onChange={(e) => setFieldValue('name', e.target.value)}
            error={Boolean(errors.name && touched.name)}
            helperText={touched.name ? errors.name : ''}
            placeholder="Enter your name"
          />
          
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={values.email}
            onChange={(e) => setFieldValue('email', e.target.value)}
            error={Boolean(errors.email && touched.email)}
            helperText={touched.email ? errors.email : ''}
            placeholder="Enter your email"
          />
          
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={values.description}
            onChange={(e) => setFieldValue('description', e.target.value)}
            error={Boolean(errors.description && touched.description)}
            helperText={touched.description ? errors.description : ''}
            placeholder="Enter a description (optional)"
          />
        </Box>
      </Box>
      
      {/* Actions */}
      <Box display="flex" gap={2} justifyContent="flex-end">
        <Button 
          onClick={reset} 
          variant="outlined"
          disabled={isSubmitting}
        >
          Reset
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={isSubmitting || !isValid || !lifecycle.canSubmit}
        >
          {isSubmitting ? 'Submitting...' : 'Submit'}
        </Button>
      </Box>
      
      {/* Success/Error Messages */}
      {lifecycle.currentState === 'success' && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Form submitted successfully!
        </Alert>
      )}
      
      {lifecycle.currentState === 'error' && (
        <Alert severity="error" sx={{ mt: 2 }}>
          Form submission failed. Please try again.
        </Alert>
      )}
    </Paper>
  );
};
