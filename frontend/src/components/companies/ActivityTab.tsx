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
  Timeline,
  History,
  Receipt,
  AccountBalance,
  Notifications,
  TrendingUp,
} from '@mui/icons-material';

// ============================================================================
// COMPONENT
// ============================================================================

export const ActivityTab: React.FC = () => {
  const plannedFeatures = [
    {
      icon: <History color="primary" />,
      title: 'Personal Timeline',
      description: 'Chronological view of all your investment activities and transactions',
      status: 'planned',
    },
    {
      icon: <Receipt color="primary" />,
      title: 'Transaction History',
      description: 'Detailed record of all capital calls, distributions, and NAV updates',
      status: 'planned',
    },
    {
      icon: <AccountBalance color="primary" />,
      title: 'Balance Tracking',
      description: 'Real-time tracking of your equity balances across all funds',
      status: 'planned',
    },
    {
      icon: <Notifications color="primary" />,
      title: 'Activity Alerts',
      description: 'Get notified about important fund events and updates',
      status: 'planned',
    },
    {
      icon: <TrendingUp color="primary" />,
      title: 'Performance Tracking',
      description: 'Monitor your personal returns and performance metrics',
      status: 'planned',
    },
  ];

  return (
    <Box p={3}>
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={3}>
            <Timeline sx={{ fontSize: 48, color: 'primary.main', mr: 2 }} />
            <Box>
              <Typography variant="h4" gutterBottom>
                Personal Activity
              </Typography>
              <Typography variant="body1" color="textSecondary">
                Track your personal investment activities and transaction history
              </Typography>
            </Box>
          </Box>
          
          <Typography variant="body2" color="textSecondary" paragraph>
            This tab will provide a comprehensive view of your personal investment activities, 
            including all transactions, balance changes, and performance tracking across your 
            investment portfolio.
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
