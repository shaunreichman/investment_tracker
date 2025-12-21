/**
 * AllEntitiesPage Component
 * 
 * Page component for displaying and managing entities.
 * Extracted from OverallDashboard - handles entity management section.
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  useTheme,
} from '@mui/material';
import { Add as AddIcon, Person as PersonIcon } from '@mui/icons-material';
import { EntityList, CreateEntityModal } from '../components';
import { useEntities } from '../hooks';

/**
 * AllEntitiesPage Component
 * 
 * Main page for entity management. This page:
 * - Fetches entity data using useEntities() hook
 * - Displays EntityList component with data passed via props
 * - Integrates CreateEntityModal for entity creation
 * - Handles modal state management and data refresh after entity creation
 */
const AllEntitiesPage: React.FC = () => {
  const theme = useTheme();
  const [showEntityModal, setShowEntityModal] = useState(false);

  // Fetch entity data
  const { data: entities, loading, error, refetch } = useEntities();

  // Handle entity creation - close modal and refresh data after creation
  const handleEntityCreated = async (entity: { id: number; name: string }) => {
    // Close modal
    setShowEntityModal(false);
    
    // Refresh entity list to show newly created entity
    await refetch();
  };

  // Button click handler
  const handleCreateEntityClick = () => {
    setShowEntityModal(true);
  };

  return (
    <Box sx={{ p: 0 }}>
      {/* Page Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h3" 
          sx={{ 
            color: theme.palette.text.primary,
            fontWeight: 600,
            mb: 1,
            letterSpacing: '-0.02em'
          }}
        >
          Entities
        </Typography>
        
        <Typography 
          variant="body1" 
          sx={{ 
            color: theme.palette.text.secondary,
            fontSize: '16px',
            lineHeight: 1.5
          }}
        >
          Manage entities (individuals, companies, trusts, and funds) in your investment portfolio
        </Typography>
      </Box>

      {/* Entity Management Card */}
      <Card sx={{ 
        backgroundColor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.divider}`,
        '&:hover': {
          boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
          transform: 'translateY(-2px)',
          transition: 'all 0.2s ease-in-out'
        }
      }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            mb: 2 
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PersonIcon sx={{ 
                mr: 2, 
                color: theme.palette.primary.main,
                fontSize: '28px'
              }} />
              <Typography 
                variant="h5" 
                sx={{ 
                  color: theme.palette.text.primary,
                  fontWeight: 600
                }}
              >
                Entity Management
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreateEntityClick}
              size="medium"
              sx={{
                backgroundColor: theme.palette.primary.main,
                '&:hover': {
                  backgroundColor: theme.palette.primary.dark
                },
                px: 3,
                py: 1
              }}
            >
              Create Entity
            </Button>
          </Box>
          
          {/* Entity List Component */}
          <EntityList 
            data={entities}
            loading={loading}
            error={error}
            onRefresh={refetch}
          />
        </CardContent>
      </Card>

      {/* Entity Creation Modal */}
      <CreateEntityModal
        open={showEntityModal}
        onClose={() => setShowEntityModal(false)}
        onEntityCreated={handleEntityCreated}
      />
    </Box>
  );
};

export default AllEntitiesPage;

