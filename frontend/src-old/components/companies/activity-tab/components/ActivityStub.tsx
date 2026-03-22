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
  Timeline,
  Event,
  Notifications,
  History,
} from '@mui/icons-material';

export const ActivityStub: React.FC = () => {
  const plannedFeatures = [
    'Personal investment timeline',
    'Transaction history and tracking',
    'Distribution notifications',
    'Fund event updates',
    'Performance milestone tracking',
    'Document upload and management',
    'Communication history with companies',
    'Investment decision tracking',
  ];

  return (
    <Box p={3}>
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={3}>
            <Timeline sx={{ mr: 2, color: 'primary.main', fontSize: 32 }} />
            <Typography variant="h4">Investment Activity</Typography>
          </Box>
          
          <Typography variant="body1" color="textSecondary" paragraph>
            Track your personal investment journey and stay updated on all activities. This tab will provide 
            a comprehensive view of your investment timeline and transaction history.
          </Typography>
          
          <Typography variant="h6" gutterBottom>
            Planned Features:
          </Typography>
          
          <List>
            {plannedFeatures.map((feature, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {index % 4 === 0 && <Event color="primary" />}
                  {index % 4 === 1 && <Notifications color="secondary" />}
                  {index % 4 === 2 && <History color="success" />}
                  {index % 4 === 3 && <Timeline color="info" />}
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
