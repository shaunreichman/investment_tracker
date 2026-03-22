import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Analytics,
  TrendingUp,
  PieChart,
  Timeline,
} from '@mui/icons-material';

export const AnalysisStub: React.FC = () => {
  const plannedFeatures = [
    'Fund performance comparison charts',
    'Risk-adjusted return analysis',
    'Portfolio allocation breakdowns',
    'Historical performance trends',
    'Benchmark comparisons',
    'Correlation analysis between funds',
    'Risk metrics and volatility analysis',
    'Cash flow timing analysis',
  ];

  return (
    <Box p={3}>
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={3}>
            <Analytics sx={{ mr: 2, color: 'primary.main', fontSize: 32 }} />
            <Typography variant="h4">Investment Analysis</Typography>
          </Box>
          
          <Typography variant="body1" color="textSecondary" paragraph>
            Advanced analytics and performance insights are coming soon! This tab will provide comprehensive 
            analysis tools to help you understand your investment performance and make informed decisions.
          </Typography>
          
          <Typography variant="h6" gutterBottom>
            Planned Features:
          </Typography>
          
          <List>
            {plannedFeatures.map((feature, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {index % 4 === 0 && <TrendingUp color="primary" />}
                  {index % 4 === 1 && <PieChart color="secondary" />}
                  {index % 4 === 2 && <Timeline color="success" />}
                  {index % 4 === 3 && <Analytics color="info" />}
                </ListItemIcon>
                <ListItemText primary={feature} />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  );
};

