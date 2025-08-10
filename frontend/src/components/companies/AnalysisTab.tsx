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
  Chip,
} from '@mui/material';
import {
  Analytics,
  TrendingUp,
  BarChart,
  PieChart,
  Timeline,
  Assessment,
} from '@mui/icons-material';

// ============================================================================
// COMPONENT
// ============================================================================

export const AnalysisTab: React.FC = () => {
  const plannedFeatures = [
    {
      icon: <TrendingUp color="primary" />,
      title: 'Performance Analytics',
      description: 'Advanced performance metrics and trend analysis across all funds',
      status: 'planned',
    },
    {
      icon: <BarChart color="primary" />,
      title: 'Comparative Analysis',
      description: 'Side-by-side fund comparison with standardized metrics',
      status: 'planned',
    },
    {
      icon: <PieChart color="primary" />,
      title: 'Portfolio Allocation',
      description: 'Visual breakdown of portfolio allocation and diversification',
      status: 'planned',
    },
    {
      icon: <Timeline color="primary" />,
      title: 'Historical Trends',
      description: 'Long-term performance trends and pattern recognition',
      status: 'planned',
    },
    {
      icon: <Assessment color="primary" />,
      title: 'Risk Analysis',
      description: 'Risk metrics and volatility analysis for portfolio management',
      status: 'planned',
    },
  ];

  return (
    <Box p={3}>
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={3}>
            <Analytics sx={{ fontSize: 48, color: 'primary.main', mr: 2 }} />
            <Box>
              <Typography variant="h4" gutterBottom>
                Portfolio Analysis
              </Typography>
              <Typography variant="body1" color="textSecondary">
                Advanced analytics and performance insights for your investment portfolio
              </Typography>
            </Box>
          </Box>
          
          <Typography variant="body2" color="textSecondary" paragraph>
            This tab will provide comprehensive analytics and insights to help you make informed 
            investment decisions. We're working on bringing you powerful tools for portfolio 
            analysis and performance evaluation.
          </Typography>
        </CardContent>
      </Card>

      <Typography variant="h6" gutterBottom mb={3}>
        Planned Features
      </Typography>

      <List>
        {plannedFeatures.map((feature, index) => (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              <ListItem disablePadding>
                <ListItemIcon sx={{ minWidth: 48 }}>
                  {feature.icon}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={2}>
                      <Typography variant="h6">{feature.title}</Typography>
                      <Chip 
                        label={feature.status} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={feature.description}
                  secondaryTypographyProps={{ variant: 'body2', color: 'textSecondary' }}
                />
              </ListItem>
            </CardContent>
          </Card>
        ))}
      </List>

      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="body2" color="textSecondary" textAlign="center">
            These features are currently in development. Check back soon for updates!
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};
