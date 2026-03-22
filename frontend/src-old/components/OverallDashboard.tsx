import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  useTheme,
} from '@mui/material';

import {
  Business,
  Add as AddIcon,
  Person as PersonIcon,
  Business as BusinessIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import CreateEntityModal from './CreateEntityModal';
import CreateCompanyModal from './CreateCompanyModal';
import { EntityList } from './entities';
import { CompanyList } from './companies';


const OverallDashboard: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [showEntityModal, setShowEntityModal] = useState(false);
  const [showCompanyModal, setShowCompanyModal] = useState(false);

  // Simplified entity creation handling - direct and reliable
  const handleEntityCreated = (entity: { id: number; name: string }) => {
    // Close modal - the modal will handle its own cleanup
    setShowEntityModal(false);
    
    // EntityList component will handle its own data refresh automatically
  };

  const handleCompanyCreated = (company: { id: number; name: string }) => {
    // Close modal - CompanyList component will handle its own data refresh automatically
    setShowCompanyModal(false);
  };

  // Button click handlers
  const handleCreateEntityClick = () => {
    setShowEntityModal(true);
  };

  const handleCreateCompanyClick = () => {
    setShowCompanyModal(true);
  };

  return (
    <Box sx={{ p: 0 }}>
      {/* Page Header Section - Add top margin to account for fixed TopBar */}
      <Box sx={{ mb: 4 }}> {/* Removed manual top margin since RouteLayout handles it */}
        <Typography 
          variant="h3" 
          sx={{ 
            color: theme.palette.text.primary,
            fontWeight: 600,
            mb: 1,
            letterSpacing: '-0.02em'
          }}
        >
          Companies
        </Typography>
        
        <Typography 
          variant="body1" 
          sx={{ 
            color: theme.palette.text.muted,
            fontSize: '16px',
            lineHeight: 1.5
          }}
        >
          Overview of all companies and their managed funds
        </Typography>
      </Box>

      {/* Data Management Section */}
      <Box 
        sx={{ 
          display: 'grid', 
          gap: 3, 
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
          mb: 4 
        }}
      >
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
            <EntityList />
          </CardContent>
        </Card>

        {/* Company Management Card */}
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
              alignItems: 'flex-start', 
              mb: 2,
              flexWrap: 'wrap',
              gap: 2
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, minWidth: 0 }}>
                <BusinessIcon sx={{ 
                  mr: 2, 
                  color: theme.palette.primary.main,
                  fontSize: '28px',
                  flexShrink: 0
                }} />
                <Typography 
                  variant="h5" 
                  sx={{ 
                    color: theme.palette.text.primary,
                    fontWeight: 600,
                    minWidth: 0
                  }}
                >
                  Company Management
                </Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleCreateCompanyClick}
                size="medium"
                sx={{
                  backgroundColor: theme.palette.primary.main,
                  '&:hover': {
                    backgroundColor: theme.palette.primary.dark
                  },
                  px: 3,
                  py: 1,
                  flexShrink: 0
                }}
              >
                Create Company
              </Button>
            </Box>
            <Typography 
              variant="body1" 
              sx={{ 
                color: theme.palette.text.muted,
                lineHeight: 1.6
              }}
            >
              Create and manage companies and fund managers
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Companies Portfolio - Using CompanyList Component */}
      <Card sx={{ 
        backgroundColor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.divider}`,
        mb: 4
      }}>
        <CardContent sx={{ p: 3 }}>
          <Typography 
            variant="h5" 
            sx={{ 
              color: theme.palette.text.primary,
              fontWeight: 600,
              mb: 3,
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <Business sx={{ mr: 2, color: theme.palette.primary.main, fontSize: '28px' }} />
            Companies Portfolio
          </Typography>
          
          {/* Reusable CompanyList Component */}
          <CompanyList />
        </CardContent>
      </Card>

      {/* Entity Creation Modal */}
      <CreateEntityModal
        open={showEntityModal}
        onClose={() => setShowEntityModal(false)}
        onEntityCreated={handleEntityCreated}
      />

      {/* Company Creation Modal */}
      <CreateCompanyModal
        open={showCompanyModal}
        onClose={() => setShowCompanyModal(false)}
        onCompanyCreated={handleCompanyCreated}
      />
    </Box>
  );
};

export default OverallDashboard; 