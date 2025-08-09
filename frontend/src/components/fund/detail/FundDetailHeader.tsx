import React from 'react';
import { Box, Breadcrumbs, IconButton, Link, Typography } from '@mui/material';
import { ChevronLeft, ChevronRight } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ExtendedFund } from '../../../types/api';

interface FundDetailHeaderProps {
  fund: ExtendedFund;
  sidebarVisible: boolean;
  onToggleSidebar: () => void;
}

const FundDetailHeader: React.FC<FundDetailHeaderProps> = ({ fund, sidebarVisible, onToggleSidebar }) => {
  const navigate = useNavigate();

  return (
    <>
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate('/')}
          sx={{ textDecoration: 'none', cursor: 'pointer' }}
        >
          Investment Companies
        </Link>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate(`/companies/${fund.investment_company_id}`)}
          sx={{ textDecoration: 'none', cursor: 'pointer' }}
        >
          {fund.investment_company}
        </Link>
        <Typography color="text.primary">{fund.name}</Typography>
      </Breadcrumbs>

      <Box sx={{ mb: 3, position: 'relative' }}>
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom
          sx={{ 
            fontWeight: 600,
            color: 'text.primary',
            letterSpacing: '-0.02em'
          }}
        >
          {fund.name}
        </Typography>
        <Typography 
          variant="subtitle1" 
          color="text.secondary" 
          gutterBottom
          sx={{ 
            fontWeight: 400,
            opacity: 0.8
          }}
        >
          {fund.fund_type} • {fund.entity} • {fund.investment_company}
        </Typography>

        <IconButton
          onClick={onToggleSidebar}
          sx={{ 
            position: 'absolute', 
            right: 0, 
            top: 0,
            zIndex: 1,
            bgcolor: 'background.paper',
            boxShadow: '0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.12)',
            borderRadius: 2,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              bgcolor: 'action.hover',
              transform: 'translateY(-2px)',
              boxShadow: '0 6px 20px rgba(0,0,0,0.12), 0 3px 8px rgba(0,0,0,0.16)'
            }
          }}
          aria-label={sidebarVisible ? 'Hide summary sidebar' : 'Show summary sidebar'}
        >
          {sidebarVisible ? <ChevronLeft /> : <ChevronRight />}
        </IconButton>
      </Box>
    </>
  );
};

export default FundDetailHeader;


