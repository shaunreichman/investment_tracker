/**
 * EntityCards Component
 * 
 * Card view for displaying entities in a responsive grid layout.
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  useTheme
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
} from '@mui/icons-material';
import { Entity } from '../../types/models/entity';
import { EntityType } from '../../types/enums/entity.enums';
import { ConfirmDialog } from '../ui/ConfirmDialog';

export interface EntityCardsProps {
  entities: Entity[];
  onDelete: (entity: Entity) => Promise<void>;
  isDeleting: boolean;
}

const getEntityIcon = (type: EntityType) => {
  switch (type) {
    case EntityType.PERSON:
      return <PersonIcon />;
    case EntityType.COMPANY:
    case EntityType.TRUST:
    case EntityType.FUND:
      return <BusinessIcon />;
    default:
      return <BusinessIcon />;
  }
};

export const EntityCards: React.FC<EntityCardsProps> = ({
  entities,
  onDelete,
  isDeleting,
}) => {
  const theme = useTheme();
  const [deleteConfirm, setDeleteConfirm] = useState<Entity | null>(null);

  const handleDeleteClick = (entity: Entity) => {
    setDeleteConfirm(entity);
  };

  const handleDeleteConfirm = async () => {
    if (deleteConfirm) {
      await onDelete(deleteConfirm);
      setDeleteConfirm(null);
    }
  };

  return (
    <>
      <Box 
        sx={{ 
          p: 2,
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(3, 1fr)',
          },
          gap: 2,
        }}
      >
        {entities.map((entity) => (
          <Card
            key={entity.id}
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              '&:hover': {
                boxShadow: theme.shadows[4],
                transform: 'translateY(-2px)',
                transition: 'all 0.2s ease-in-out',
              },
            }}
          >
            <CardContent sx={{ flexGrow: 1 }}>
              {/* Header */}
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  mb: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {getEntityIcon(entity.entity_type)}
                  <Typography variant="h6" component="div" noWrap>
                    {entity.name}
                  </Typography>
                </Box>
                <Tooltip title="Delete entity">
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteClick(entity)}
                    disabled={isDeleting}
                    color="error"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>

              {/* Type and Jurisdiction */}
              <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                <Chip
                  label={entity.entity_type}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={entity.tax_jurisdiction}
                  size="small"
                  color="secondary"
                  variant="outlined"
                />
              </Box>

              {/* Description */}
              {entity.description && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    mb: 2,
                  }}
                >
                  {entity.description}
                </Typography>
              )}

              {/* Created Date */}
              <Typography variant="caption" color="text.secondary">
                Created: {new Date(entity.created_at).toLocaleDateString()}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={!!deleteConfirm}
        title="Delete Entity?"
        description={`Are you sure you want to delete "${deleteConfirm?.name}"? This action cannot be undone.`}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteConfirm(null)}
        confirmLabel="Delete"
        confirmVariant="error"
      />
    </>
  );
};

