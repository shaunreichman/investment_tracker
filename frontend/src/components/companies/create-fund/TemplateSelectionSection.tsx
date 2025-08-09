import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

export interface FundTemplate {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  fund_type: string;
  tracking_type: 'nav_based' | 'cost_based';
  currency: string;
  commitment_amount?: number;
  expected_irr?: number;
  expected_duration_months?: number;
  description_template: string;
}

interface TemplateSelectionSectionProps {
  templates: FundTemplate[];
  onSelect: (template: FundTemplate) => void;
}

const TemplateSelectionSection: React.FC<TemplateSelectionSectionProps> = ({ templates, onSelect }) => {
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        Select a Tracking Type Template
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Choose how you want to track your fund investments.
      </Typography>
      <Box display="grid" gap={2} sx={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
        {templates.map((template) => (
          <Paper key={template.id} sx={{ cursor: 'pointer', p: 2, '&:hover': { bgcolor: 'primary.light' } }}>
            <Box onClick={() => onSelect(template)}>
              <Box display="flex" alignItems="center" gap={2} sx={{ mb: 1 }}>
                {template.icon}
                <Typography variant="h6">{template.name}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {template.description}
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                <Typography
                  variant="caption"
                  sx={{ bgcolor: 'primary.main', color: 'white', px: 1, py: 0.5, borderRadius: 1, fontSize: '0.75rem' }}
                >
                  {template.tracking_type}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{ bgcolor: 'grey.300', px: 1, py: 0.5, borderRadius: 1, fontSize: '0.75rem' }}
                >
                  {template.currency}
                </Typography>
              </Box>
            </Box>
          </Paper>
        ))}
      </Box>
    </Box>
  );
};

export default TemplateSelectionSection;


