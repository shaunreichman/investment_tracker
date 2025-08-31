import React, { useState, useCallback, useMemo } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Typography,
  Paper,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert
} from '@mui/material';
import {
  Check as CheckIcon,
  NavigateNext as NavigateNextIcon,
  NavigateBefore as NavigateBeforeIcon
} from '@mui/icons-material';
import { useConditionalFields, ConditionalFieldConfig } from '../../hooks/forms/useConditionalFields';

/**
 * Step configuration for progressive disclosure
 */
export interface FormStep {
  /** Unique identifier for the step */
  id: string;
  /** Display label for the step */
  label: string;
  /** Description of what this step accomplishes */
  description: string;
  /** Fields that belong to this step */
  fields: string[];
  /** Whether this step is required to proceed */
  required: boolean;
  /** Custom validation function for this step */
  validateStep?: (values: Record<string, any>) => string | undefined;
  /** Whether to show a summary of this step */
  showSummary?: boolean;
}

/**
 * Props for the ProgressiveDisclosureForm component
 */
interface ProgressiveDisclosureFormProps {
  /** Form steps configuration */
  steps: FormStep[];
  /** Conditional field configurations */
  fieldConfigs: ConditionalFieldConfig[];
  /** Current form values */
  values: Record<string, any>;
  /** Form validation errors */
  errors: Record<string, string | undefined>;
  /** Whether the form is currently submitting */
  isSubmitting?: boolean;
  /** Callback when a field value changes */
  onFieldChange: (field: string, value: any) => void;
  /** Callback when form is submitted */
  onSubmit: () => void;
  /** Custom render function for form fields */
  renderField: (field: string, config: ConditionalFieldConfig) => React.ReactNode;
  /** Whether to show step validation */
  showStepValidation?: boolean;
  /** Whether to allow going back to previous steps */
  allowBackNavigation?: boolean;
  /** Custom step completion logic */
  onStepComplete?: (stepId: string, values: Record<string, any>) => void;
}

/**
 * Component that implements progressive disclosure for complex forms
 * Shows fields progressively as users complete earlier steps
 */
const ProgressiveDisclosureForm: React.FC<ProgressiveDisclosureFormProps> = ({
  steps,
  fieldConfigs,
  values,
  errors,
  isSubmitting = false,
  onFieldChange,
  onSubmit,
  renderField,
  showStepValidation = true,
  allowBackNavigation = true,
  onStepComplete
}) => {
  // Current active step
  const [activeStep, setActiveStep] = useState(0);
  
  // Track completed steps
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());
  
  // Track step validation errors
  const [stepErrors, setStepErrors] = useState<Record<string, string>>({});

  // Use conditional fields hook to manage field visibility and requirements
  const {
    visibleFields,
    requiredFields,
    isFieldVisible,
    isFieldRequired,
    getConditionalValidationRules
  } = useConditionalFields({
    fieldConfigs,
    values,
    enableValidation: true
  });

  // Calculate overall form completion percentage
  const completionPercentage = useMemo(() => {
    const totalSteps = steps.length;
    const completedCount = completedSteps.size;
    return Math.round((completedCount / totalSteps) * 100);
  }, [steps.length, completedSteps.size]);

  // Get fields for the current step
  const currentStepFields = useMemo(() => {
    const currentStep = steps[activeStep];
    if (!currentStep) return [];
    
    return currentStep.fields.filter(field => isFieldVisible(field));
  }, [steps, activeStep, isFieldVisible]);

  // Check if current step is valid
  const isCurrentStepValid = useCallback(() => {
    const currentStep = steps[activeStep];
    if (!currentStep) return false;
    
    // Check if all required fields in this step have values
    const requiredFieldsInStep = currentStep.fields.filter(field => 
      isFieldVisible(field) && isFieldRequired(field)
    );
    
    const hasAllRequiredValues = requiredFieldsInStep.every(field => 
      values[field] !== undefined && values[field] !== null && values[field] !== ''
    );
    
    // Check for validation errors in this step
    const hasNoErrors = currentStep.fields.every(field => !errors[field]);
    
    // Run custom step validation if provided
    let customValidationPassed = true;
    if (currentStep.validateStep) {
      const customError = currentStep.validateStep(values);
      customValidationPassed = !customError;
      if (customError) {
        setStepErrors(prev => ({ ...prev, [currentStep.id]: customError }));
      }
    }
    
    return hasAllRequiredValues && hasNoErrors && customValidationPassed;
  }, [steps, activeStep, isFieldVisible, isFieldRequired, values, errors]);

  // Handle next step
  const handleNext = useCallback(() => {
    const currentStep = steps[activeStep];
    if (!currentStep) return;
    
    if (isCurrentStepValid()) {
      // Mark step as completed
      setCompletedSteps(prev => new Set([...prev, currentStep.id]));
      
      // Call step completion callback
      onStepComplete?.(currentStep.id, values);
      
      // Clear step errors
      setStepErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[currentStep.id];
        return newErrors;
      });
      
      // Move to next step
      if (activeStep < steps.length - 1) {
        setActiveStep(activeStep + 1);
      }
    }
  }, [steps, activeStep, isCurrentStepValid, values, onStepComplete]);

  // Handle previous step
  const handleBack = useCallback(() => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1);
    }
  }, [activeStep]);

  // Handle step click (for navigation)
  const handleStepClick = useCallback((stepIndex: number) => {
    if (stepIndex <= activeStep || allowBackNavigation) {
      setActiveStep(stepIndex);
    }
  }, [activeStep, allowBackNavigation]);

  // Check if a step is completed
  const isStepCompleted = useCallback((stepId: string) => {
    return completedSteps.has(stepId);
  }, [completedSteps]);

  // Check if a step is accessible (can be navigated to)
  const isStepAccessible = useCallback((stepIndex: number) => {
    if (stepIndex === 0) return true;
    if (stepIndex <= activeStep) return true;
    if (!allowBackNavigation) return false;
    
    // Check if all previous steps are completed
    for (let i = 0; i < stepIndex && i < steps.length; i++) {
      const step = steps[i];
      if (step && !isStepCompleted(step.id)) {
        return false;
      }
    }
    return true;
  }, [steps, activeStep, allowBackNavigation, isStepCompleted]);

  // Render step content
  const renderStepContent = useCallback((step: FormStep, stepIndex: number) => {
    const isActive = stepIndex === activeStep;
    const isCompleted = isStepCompleted(step.id);
    const isAccessible = isStepAccessible(stepIndex);
    
    if (!isActive && !isCompleted) return null;
    
    const stepFields = step.fields.filter(field => isFieldVisible(field));
    const stepConfigs = fieldConfigs.filter(config => stepFields.includes(config.field));
    
    return (
      <StepContent>
        <Box mb={2}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {step.description}
          </Typography>
          
          {/* Step validation error */}
          {showStepValidation && stepErrors[step.id] && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {stepErrors[step.id]}
            </Alert>
          )}
          
          {/* Step fields */}
          <Box display="flex" flexDirection="column" gap={2}>
            {stepConfigs.map(config => (
              <Box key={config.field}>
                {renderField(config.field, config)}
              </Box>
            ))}
          </Box>
          
          {/* Step summary if completed */}
          {isCompleted && step.showSummary && (
            <Card variant="outlined" sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>
                  Step Summary
                </Typography>
                <Box display="flex" gap={1} flexWrap="wrap">
                  {stepFields.map(field => (
                    <Chip
                      key={field}
                      label={`${field}: ${values[field] || 'Not set'}`}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          )}
        </Box>
        
        {/* Step navigation */}
        {isActive && (
          <Box display="flex" gap={1}>
            <Button
              disabled={stepIndex === 0}
              onClick={handleBack}
              startIcon={<NavigateBeforeIcon />}
            >
              Back
            </Button>
            
            <Box sx={{ flex: '1 1 auto' }} />
            
            {stepIndex === steps.length - 1 ? (
              <Button
                variant="contained"
                onClick={onSubmit}
                disabled={!isCurrentStepValid() || isSubmitting}
                endIcon={<CheckIcon />}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Form'}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!isCurrentStepValid()}
                endIcon={<NavigateNextIcon />}
              >
                Next
              </Button>
            )}
          </Box>
        )}
      </StepContent>
    );
  }, [
    activeStep,
    isStepCompleted,
    isStepAccessible,
    isFieldVisible,
    fieldConfigs,
    showStepValidation,
    stepErrors,
    renderField,
    values,
    handleBack,
    handleNext,
    onSubmit,
    isCurrentStepValid,
    isSubmitting,
    steps.length
  ]);

  return (
    <Box>
      {/* Overall progress */}
      <Box mb={3}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="h6">
            Form Progress
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {completionPercentage}% Complete
          </Typography>
        </Box>
        <LinearProgress 
          variant="determinate" 
          value={completionPercentage} 
          sx={{ height: 8, borderRadius: 4 }}
        />
      </Box>

      {/* Stepper */}
      <Paper elevation={1}>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => (
            <Step key={step.id} completed={isStepCompleted(step.id)}>
              <StepLabel
                onClick={() => handleStepClick(index)}
                sx={{
                  cursor: isStepAccessible(index) ? 'pointer' : 'default',
                  '&:hover': isStepAccessible(index) ? {
                    backgroundColor: 'action.hover',
                    borderRadius: 1
                  } : {}
                }}
              >
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="subtitle1">
                    {step.label}
                  </Typography>
                  
                  {step.required && (
                    <Chip label="Required" size="small" color="error" />
                  )}
                  
                  {isStepCompleted(step.id) && (
                    <CheckIcon color="success" />
                  )}
                </Box>
              </StepLabel>
              
              {renderStepContent(step, index)}
            </Step>
          ))}
        </Stepper>
      </Paper>
    </Box>
  );
};

export default ProgressiveDisclosureForm;
