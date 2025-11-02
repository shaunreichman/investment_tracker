/**
 * DependencyBlockedDialog Component
 * 
 * Dialog displayed when entity deletion is blocked due to existing dependencies.
 * Shows user-friendly error message with dependency counts and guidance.
 */

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  useTheme,
} from '@mui/material';
import {
  ErrorOutline as ErrorOutlineIcon,
  AccountBalance as AccountBalanceIcon,
  Description as DescriptionIcon,
  TrendingUp as TrendingUpIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { EntityDependencyError } from './EntityList';

export interface DependencyBlockedDialogProps {
  open: boolean;
  error: EntityDependencyError | null;
  onClose: () => void;
}

export const DependencyBlockedDialog: React.FC<DependencyBlockedDialogProps> = ({
  open,
  error,
  onClose,
}) => {
  const theme = useTheme();

  if (!error) return null;

  const hasDependencies =
    (error.details.funds && error.details.funds > 0) ||
    (error.details.bankAccounts && error.details.bankAccounts > 0) ||
    (error.details.taxStatements && error.details.taxStatements > 0);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: '12px',
          boxShadow: '0px 8px 32px rgba(0,0,0,0.4)',
        },
      }}
    >
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          color: theme.palette.error.main,
          fontWeight: 600,
          fontSize: '20px',
          borderBottom: `1px solid ${theme.palette.divider}`,
          backgroundColor: theme.palette.background.sidebar,
          borderRadius: '12px 12px 0 0',
        }}
      >
        <ErrorOutlineIcon />
        Cannot Delete Entity
      </DialogTitle>

      <DialogContent sx={{ p: 3 }}>
        {/* Entity Name */}
        <Typography variant="body1" gutterBottom sx={{ fontWeight: 500 }}>
          The entity "{error.entityName}" cannot be deleted.
        </Typography>

        {/* Explanation */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          This entity has dependencies that must be removed first:
        </Typography>

        {/* Dependencies List */}
        {hasDependencies && (
          <List sx={{ bgcolor: 'background.default', borderRadius: 1, mb: 2 }}>
            {error.details.funds && error.details.funds > 0 && (
              <ListItem>
                <ListItemIcon>
                  <TrendingUpIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={`${error.details.funds} fund${error.details.funds > 1 ? 's' : ''}`}
                  secondary="Funds owned by this entity"
                />
              </ListItem>
            )}

            {error.details.bankAccounts && error.details.bankAccounts > 0 && (
              <ListItem>
                <ListItemIcon>
                  <AccountBalanceIcon color="secondary" />
                </ListItemIcon>
                <ListItemText
                  primary={`${error.details.bankAccounts} bank account${
                    error.details.bankAccounts > 1 ? 's' : ''
                  }`}
                  secondary="Bank accounts owned by this entity"
                />
              </ListItem>
            )}

            {error.details.taxStatements && error.details.taxStatements > 0 && (
              <ListItem>
                <ListItemIcon>
                  <DescriptionIcon color="info" />
                </ListItemIcon>
                <ListItemText
                  primary={`${error.details.taxStatements} tax statement${
                    error.details.taxStatements > 1 ? 's' : ''
                  }`}
                  secondary="Tax statements for this entity"
                />
              </ListItem>
            )}
          </List>
        )}

        {/* Guidance */}
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2" gutterBottom>
            <strong>To delete this entity:</strong>
          </Typography>
          <Typography variant="body2" component="div">
            <ol style={{ margin: 0, paddingLeft: '20px' }}>
              {error.details.funds && error.details.funds > 0 && (
                <li>Delete or reassign all funds owned by this entity</li>
              )}
              {error.details.bankAccounts && error.details.bankAccounts > 0 && (
                <li>Delete all bank accounts owned by this entity</li>
              )}
              {error.details.taxStatements && error.details.taxStatements > 0 && (
                <li>Delete all tax statements for this entity</li>
              )}
            </ol>
          </Typography>
        </Alert>

        {/* Entity Immutability Note */}
        <Box sx={{ mt: 2, p: 1.5, bgcolor: 'action.hover', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary">
            💡 <strong>Note:</strong> Entities cannot be edited after creation. If you need to
            change entity details, create a new entity and migrate the dependencies.
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2, borderTop: `1px solid ${theme.palette.divider}` }}>
        <Button
          onClick={onClose}
          variant="contained"
          startIcon={<CloseIcon />}
          sx={{
            backgroundColor: theme.palette.primary.main,
            '&:hover': {
              backgroundColor: theme.palette.primary.dark,
            },
          }}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

