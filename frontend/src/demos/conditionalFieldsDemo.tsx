import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Grid,
  Chip,
  Divider,
  Alert,
  Switch,
  FormControlLabel
} from '@mui/material';
import { useConditionalFields } from '../hooks/forms/useConditionalFields';
import { fundEventConditionalFields } from '../configs/conditionalFieldConfigs';
import ConditionalFieldVisualizer from '../components/forms/ConditionalFieldVisualizer';
import { testConditionalFields, createFundEventTestScenarios } from '../utils/conditionalFieldTesting';

/**
 * Demo component showcasing the conditional fields system
 */
const ConditionalFieldsDemo: React.FC = () => {
  // Form state
  const [formValues, setFormValues] = useState({
    event_type: '',
    distribution_type: '',
    sub_distribution_type: '',
    amount: '',
    units_purchased: '',
    units_sold: '',
    unit_price: '',
    nav_per_share: '',
    has_withholding_tax: false,
    withholding_tax_amount: '',
    withholding_tax_rate: '',
    financial_year: '',
    statement_date: '',
    eofy_debt_interest_deduction_rate: '',
    interest_received_in_cash: '',
    interest_receivable_this_fy: '',
    interest_receivable_prev_fy: '',
    interest_non_resident_withholding_tax_from_statement: '',
    dividend_franked_income_amount: '',
    dividend_unfranked_income_amount: '',
    capital_gain_income_amount: '',
    interest_income_tax_rate: '',
    dividend_franked_income_tax_rate: '',
    dividend_unfranked_income_tax_rate: '',
    capital_gain_income_tax_rate: ''
  });

  // Demo controls
  const [showVisualizer, setShowVisualizer] = useState(true);
  const [showDebugMode, setShowDebugMode] = useState(false);
  const [runTests, setRunTests] = useState(false);
  const [testResults, setTestResults] = useState<any[]>([]);

  // Use conditional fields hook
  const {
    visibleFields,
    requiredFields,
    disabledFields,
    isFieldVisible,
    isFieldRequired,
    isFieldDisabled,
    getFieldDependencies,
    getDependentFields,
    getDependencyGraph
  } = useConditionalFields({
    fieldConfigs: fundEventConditionalFields,
    values: formValues,
    enableVisualization: true,
    enableValidation: true
  });

  // Handle field value changes
  const handleFieldChange = (field: string, value: any) => {
    setFormValues(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Run conditional field tests
  const handleRunTests = () => {
    const scenarios = createFundEventTestScenarios();
    const results = testConditionalFields({
      fieldConfigs: fundEventConditionalFields,
      scenarios,
      runValidation: true
    });
    setTestResults(results);
    setRunTests(true);
  };

  // Get field dependencies for display
  const getFieldDependencyInfo = (field: string) => {
    const dependencies = getFieldDependencies(field);
    const dependentFields = getDependentFields(field);
    
    return {
      dependencies: dependencies.map(dep => ({
        field: dep.field,
        operator: dep.operator,
        expected: dep.expectedValue,
        actual: dep.actualValue,
        isMet: dep.isMet
      })),
      dependentFields
    };
  };

  // Render form field based on configuration
  const renderFormField = (field: string) => {
    const isVisible = isFieldVisible(field);
    const isRequired = isFieldRequired(field);
    const isDisabled = isFieldDisabled(field);
    
    if (!isVisible) return null;

    const fieldConfig = fundEventConditionalFields.find(config => config.field === field);
    if (!fieldConfig) return null;

    const commonProps = {
      fullWidth: true,
      disabled: isDisabled,
      error: isRequired && !formValues[field as keyof typeof formValues],
      helperText: isRequired && !formValues[field as keyof typeof formValues] ? 'This field is required' : undefined
    };

    switch (field) {
      case 'event_type':
        return (
          <FormControl {...commonProps}>
            <InputLabel>Event Type</InputLabel>
            <Select
              value={formValues.event_type}
              onChange={(e) => handleFieldChange('event_type', e.target.value)}
              label="Event Type"
            >
              <MenuItem value="">Select Event Type</MenuItem>
              <MenuItem value="CAPITAL_CALL">Capital Call</MenuItem>
              <MenuItem value="DISTRIBUTION">Distribution</MenuItem>
              <MenuItem value="RETURN_OF_CAPITAL">Return of Capital</MenuItem>
              <MenuItem value="UNIT_PURCHASE">Unit Purchase</MenuItem>
              <MenuItem value="UNIT_SALE">Unit Sale</MenuItem>
              <MenuItem value="NAV_UPDATE">NAV Update</MenuItem>
              <MenuItem value="TAX_STATEMENT">Tax Statement</MenuItem>
            </Select>
          </FormControl>
        );

      case 'distribution_type':
        return (
          <FormControl {...commonProps}>
            <InputLabel>Distribution Type</InputLabel>
            <Select
              value={formValues.distribution_type}
              onChange={(e) => handleFieldChange('distribution_type', e.target.value)}
              label="Distribution Type"
            >
              <MenuItem value="">Select Distribution Type</MenuItem>
              <MenuItem value="DIVIDEND_FRANKED">Dividend (Franked)</MenuItem>
              <MenuItem value="DIVIDEND_UNFRANKED">Dividend (Unfranked)</MenuItem>
              <MenuItem value="INTEREST">Interest</MenuItem>
              <MenuItem value="CAPITAL_GAIN">Capital Gain</MenuItem>
            </Select>
          </FormControl>
        );

      case 'sub_distribution_type':
        return (
          <FormControl {...commonProps}>
            <InputLabel>Sub-Distribution Type</InputLabel>
            <Select
              value={formValues.sub_distribution_type}
              onChange={(e) => handleFieldChange('sub_distribution_type', e.target.value)}
              label="Sub-Distribution Type"
            >
              <MenuItem value="">Select Sub-Type</MenuItem>
              <MenuItem value="FRANKED">Franked</MenuItem>
              <MenuItem value="UNFRANKED">Unfranked</MenuItem>
              <MenuItem value="REGULAR">Regular</MenuItem>
              <MenuItem value="WITHHOLDING_TAX">Withholding Tax</MenuItem>
            </Select>
          </FormControl>
        );

      case 'has_withholding_tax':
        return (
          <FormControlLabel
            control={
              <Switch
                checked={formValues.has_withholding_tax}
                onChange={(e) => handleFieldChange('has_withholding_tax', e.target.checked)}
                disabled={isDisabled}
              />
            }
            label="Has Withholding Tax"
          />
        );

      case 'financial_year':
        return (
          <TextField
            {...commonProps}
            label="Financial Year"
            value={formValues.financial_year}
            onChange={(e) => handleFieldChange('financial_year', e.target.value)}
            placeholder="e.g., 2024"
          />
        );

      case 'statement_date':
        return (
          <TextField
            {...commonProps}
            label="Statement Date"
            type="date"
            value={formValues.statement_date}
            onChange={(e) => handleFieldChange('statement_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        );

      default:
        // Handle numeric and text fields
        if (field.includes('amount') || field.includes('rate') || field.includes('price') || field.includes('units')) {
          return (
            <TextField
              {...commonProps}
              label={field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              type="number"
              value={formValues[field as keyof typeof formValues]}
              onChange={(e) => handleFieldChange(field, e.target.value)}
              placeholder="Enter value"
            />
          );
        }
        
        return (
          <TextField
            {...commonProps}
            label={field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            value={formValues[field as keyof typeof formValues]}
            onChange={(e) => handleFieldChange(field, e.target.value)}
            placeholder="Enter value"
          />
        );
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Conditional Fields Demo
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        This demo showcases the declarative conditional field system that replaces imperative conditional logic.
        Change the event type to see how fields appear/disappear based on dependencies.
      </Typography>

      {/* Demo Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Demo Controls
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid sx={{ gridColumn: 'span auto' }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={showVisualizer}
                    onChange={(e) => setShowVisualizer(e.target.checked)}
                  />
                }
                label="Show Field Visualizer"
              />
            </Grid>
            <Grid sx={{ gridColumn: 'span auto' }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={showDebugMode}
                    onChange={(e) => setShowDebugMode(e.target.checked)}
                  />
                }
                label="Debug Mode"
              />
            </Grid>
            <Grid sx={{ gridColumn: 'span auto' }}>
              <Button
                variant="outlined"
                onClick={handleRunTests}
                disabled={runTests}
              >
                {runTests ? 'Tests Completed' : 'Run Conditional Field Tests'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Test Results */}
      {runTests && testResults.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Test Results
            </Typography>
            <Grid container spacing={2}>
              {testResults.map((result, index) => (
                <Grid key={index} sx={{ gridColumn: 'span 12' }}>
                  <Alert severity={result.passed ? 'success' : 'error'}>
                    <Typography variant="subtitle2">
                      {result.passed ? '✅' : '❌'} {result.scenario}
                    </Typography>
                    {!result.passed && result.failures.length > 0 && (
                      <Box mt={1}>
                        <Typography variant="body2" color="error">
                          Failures: {result.failures.join(', ')}
                        </Typography>
                      </Box>
                    )}
                  </Alert>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Form */}
      <Grid container spacing={3}>
        <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Fund Event Form
              </Typography>
              
              <Box display="flex" flexDirection="column" gap={2}>
                {fundEventConditionalFields.map(config => (
                  <Box key={config.field}>
                    {renderFormField(config.field)}
                    
                    {/* Field dependency info */}
                    {showDebugMode && (
                      <Box mt={1} ml={2}>
                        <Typography variant="caption" color="text.secondary">
                          Dependencies: {getFieldDependencyInfo(config.field).dependencies.length > 0 
                            ? getFieldDependencyInfo(config.field).dependencies.map(dep => 
                                `${dep.field} ${dep.operator} ${Array.isArray(dep.expected) ? dep.expected.join(',') : dep.expected} (${dep.isMet ? '✓' : '✗'})`
                              ).join(', ')
                            : 'None'
                          }
                        </Typography>
                      </Box>
                    )}
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
          {/* Field States Summary */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Field States
              </Typography>
              <Grid container spacing={2}>
                <Grid sx={{ gridColumn: 'span 4' }}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {visibleFields.length}
                    </Typography>
                    <Typography variant="body2">Visible</Typography>
                  </Box>
                </Grid>
                <Grid sx={{ gridColumn: 'span 4' }}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="error">
                      {requiredFields.length}
                    </Typography>
                    <Typography variant="body2">Required</Typography>
                  </Box>
                </Grid>
                <Grid sx={{ gridColumn: 'span 4' }}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="warning">
                      {disabledFields.length}
                    </Typography>
                    <Typography variant="body2">Disabled</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Field Visualizer */}
          {showVisualizer && (
            <Card>
              <CardContent>
                <ConditionalFieldVisualizer
                  fieldConfigs={fundEventConditionalFields}
                  values={formValues}
                  showDetails={true}
                  showStates={true}
                  title="Field Dependencies"
                  debugMode={showDebugMode}
                />
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      {/* Dependency Graph */}
      {showDebugMode && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Dependency Graph
            </Typography>
            <Box fontFamily="monospace" fontSize="12px">
              <pre>{JSON.stringify(getDependencyGraph(), null, 2)}</pre>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ConditionalFieldsDemo;
