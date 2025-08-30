import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useConditionalFields, FieldDependencyResult } from '../../hooks/forms/useConditionalFields';

/**
 * Props for the ConditionalFieldVisualizer component
 */
interface ConditionalFieldVisualizerProps {
  /** Field configurations to visualize */
  fieldConfigs: any[];
  /** Current form values */
  values: Record<string, any>;
  /** Whether to show dependency details */
  showDetails?: boolean;
  /** Whether to show field states */
  showStates?: boolean;
  /** Custom title for the visualizer */
  title?: string;
  /** Whether to enable debugging mode */
  debugMode?: boolean;
}

/**
 * Component to visualize conditional field dependencies and states
 * Helps developers understand complex conditional logic and debug field behavior
 */
const ConditionalFieldVisualizer: React.FC<ConditionalFieldVisualizerProps> = ({
  fieldConfigs,
  values,
  showDetails = true,
  showStates = true,
  title = 'Conditional Field Dependencies',
  debugMode = false
}) => {
  // Use the conditional fields hook to get current field states
  const {
    visibleFields,
    requiredFields,
    disabledFields,
    getFieldDependencies,
    getDependentFields,
    getDependencyGraph
  } = useConditionalFields({
    fieldConfigs,
    values,
    enableVisualization: true,
    enableValidation: true
  });

  // Get dependency graph for visualization
  const dependencyGraph = getDependencyGraph();

  // Helper function to render dependency status
  const renderDependencyStatus = (dependencies: FieldDependencyResult[]) => {
    if (dependencies.length === 0) {
      return <Chip label="No Dependencies" size="small" variant="outlined" />;
    }

    return (
      <Box display="flex" gap={0.5} flexWrap="wrap">
        {dependencies.map((dep, index) => (
          <Tooltip
            key={index}
            title={`${dep.field} ${dep.operator} ${Array.isArray(dep.expectedValue) ? dep.expectedValue.join(', ') : dep.expectedValue} (actual: ${dep.actualValue})`}
          >
            <Chip
              icon={dep.isMet ? <CheckCircleIcon /> : <CancelIcon />}
              label={`${dep.field}: ${dep.actualValue}`}
              size="small"
              color={dep.isMet ? 'success' : 'error'}
              variant="outlined"
            />
          </Tooltip>
        ))}
      </Box>
    );
  };

  // Helper function to render field state indicators
  const renderFieldState = (field: string) => {
    const isVisible = visibleFields.includes(field);
    const isRequired = requiredFields.includes(field);
    const isDisabled = disabledFields.includes(field);

    return (
      <Box display="flex" gap={0.5} alignItems="center">
        <Tooltip title={isVisible ? 'Field is visible' : 'Field is hidden'}>
          <IconButton size="small" disabled>
            {isVisible ? <VisibilityIcon color="primary" /> : <VisibilityOffIcon color="action" />}
          </IconButton>
        </Tooltip>
        
        {isRequired && (
          <Tooltip title="Field is required">
            <Chip label="Required" size="small" color="error" />
          </Tooltip>
        )}
        
        {isDisabled && (
          <Tooltip title="Field is disabled">
            <Chip label="Disabled" size="small" color="warning" />
          </Tooltip>
        )}
      </Box>
    );
  };

  // Helper function to render dependency graph
  const renderDependencyGraph = () => {
    const fields = Object.keys(dependencyGraph);
    
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Dependency Graph
        </Typography>
        <Grid container spacing={2}>
          {fields.map(field => {
            const dependencies = dependencyGraph[field];
            const dependentFields = getDependentFields(field);
            
            return (
              <Grid key={field} sx={{ gridColumn: { xs: 'span 12', sm: 'span 6', md: 'span 4' } }}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      {field}
                    </Typography>
                    
                    {dependencies && dependencies.length > 0 && (
                      <Box mb={1}>
                        <Typography variant="caption" color="text.secondary">
                          Depends on:
                        </Typography>
                        <Box display="flex" gap={0.5} flexWrap="wrap" mt={0.5}>
                          {dependencies.map((dep, index) => (
                            <Chip
                              key={index}
                              label={dep}
                              size="small"
                              variant="outlined"
                              color="primary"
                            />
                          ))}
                        </Box>
                      </Box>
                    )}
                    
                    {dependentFields.length > 0 && (
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Affects:
                        </Typography>
                        <Box display="flex" gap={0.5} flexWrap="wrap" mt={0.5}>
                          {dependentFields.map((depField, index) => (
                            <Chip
                              key={index}
                              label={depField}
                              size="small"
                              variant="outlined"
                              color="secondary"
                            />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    );
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={1} mb={2}>
        <InfoIcon color="primary" />
        <Typography variant="h6">{title}</Typography>
        {debugMode && (
          <Chip label="Debug Mode" size="small" color="warning" />
        )}
      </Box>

      {/* Field States Summary */}
      {showStates && (
        <Box mb={3}>
          <Typography variant="subtitle1" gutterBottom>
            Field States
          </Typography>
          <Grid container spacing={2}>
            <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 4' } }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary">
                    {visibleFields.length}
                  </Typography>
                  <Typography variant="body2">Visible Fields</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 4' } }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="error">
                    {requiredFields.length}
                  </Typography>
                  <Typography variant="body2">Required Fields</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid sx={{ gridColumn: { xs: 'span 12', sm: 'span 4' } }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="warning">
                    {disabledFields.length}
                  </Typography>
                  <Typography variant="body2">Disabled Fields</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Field Details */}
      {showDetails && (
        <Box mb={3}>
          <Typography variant="subtitle1" gutterBottom>
            Field Details
          </Typography>
          {fieldConfigs.map((config, index) => {
            const dependencies = getFieldDependencies(config.field);
            const isVisible = visibleFields.includes(config.field);
            const isRequired = requiredFields.includes(config.field);
            const isDisabled = disabledFields.includes(config.field);

            return (
              <Accordion key={index} defaultExpanded={debugMode}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" gap={2} width="100%">
                    <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
                      {config.field}
                    </Typography>
                    
                    {showStates && renderFieldState(config.field)}
                    
                    <Chip
                      label={isVisible ? 'Visible' : 'Hidden'}
                      size="small"
                      color={isVisible ? 'success' : 'default'}
                      variant="outlined"
                    />
                  </Box>
                </AccordionSummary>
                
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Dependencies:
                      </Typography>
                      {renderDependencyStatus(dependencies)}
                    </Grid>
                    
                    <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Configuration:
                      </Typography>
                      <Box display="flex" gap={1} flexWrap="wrap">
                        <Chip
                          label={`Visible: ${config.visible}`}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          label={`Required: ${config.required}`}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          label={`Disabled: ${config.disabled}`}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    </Grid>
                    
                    {debugMode && (
                      <Grid sx={{ gridColumn: 'span 12' }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Current Values:
                        </Typography>
                        <Typography variant="body2" fontFamily="monospace">
                          {JSON.stringify(values, null, 2)}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            );
          })}
        </Box>
      )}

      {/* Dependency Graph */}
      {debugMode && renderDependencyGraph()}
    </Box>
  );
};

export default ConditionalFieldVisualizer;
