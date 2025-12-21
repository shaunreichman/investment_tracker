/**
 * EntityTable Component
 * 
 * Table view for displaying entities with sortable columns and delete actions.
 */

import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  useTheme
} from '@mui/material';
import {
  Delete as DeleteIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
} from '@mui/icons-material';
import type { Entity } from '@/entity/types';
import { SortFieldEntity } from '@/entity/types';
import { SortOrder } from '@/shared/types';
import { ConfirmDialog } from '@/shared/ui/overlays';

export interface EntityTableProps {
  entities: Entity[];
  onDelete: (entity: Entity) => Promise<void>;
  sortBy: SortFieldEntity;
  sortOrder: SortOrder;
  onSort: (field: SortFieldEntity) => void;
  isDeleting: boolean;
}

export const EntityTable: React.FC<EntityTableProps> = ({
  entities,
  onDelete,
  sortBy,
  sortOrder,
  onSort,
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

  const renderSortIcon = (field: SortFieldEntity) => {
    if (sortBy !== field) return null;
    return sortOrder === SortOrder.ASC ? (
      <ArrowUpwardIcon sx={{ fontSize: 16, ml: 0.5 }} />
    ) : (
      <ArrowDownwardIcon sx={{ fontSize: 16, ml: 0.5 }} />
    );
  };

  return (
    <>
      <TableContainer sx={{ maxHeight: 500 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell
                sx={{ fontWeight: 600, cursor: 'pointer' }}
                onClick={() => onSort(SortFieldEntity.NAME)}
              >
                Name {renderSortIcon(SortFieldEntity.NAME)}
              </TableCell>
              <TableCell
                sx={{ fontWeight: 600, cursor: 'pointer' }}
                onClick={() => onSort(SortFieldEntity.TYPE)}
              >
                Type {renderSortIcon(SortFieldEntity.TYPE)}
              </TableCell>
              <TableCell
                sx={{ fontWeight: 600, cursor: 'pointer' }}
                onClick={() => onSort(SortFieldEntity.TAX_JURISDICTION)}
              >
                Jurisdiction {renderSortIcon(SortFieldEntity.TAX_JURISDICTION)}
              </TableCell>
              <TableCell sx={{ fontWeight: 600 }}>Description</TableCell>
              <TableCell
                sx={{ fontWeight: 600, cursor: 'pointer' }}
                onClick={() => onSort(SortFieldEntity.CREATED_AT)}
              >
                Created {renderSortIcon(SortFieldEntity.CREATED_AT)}
              </TableCell>
              <TableCell sx={{ fontWeight: 600, width: 80 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {entities.map((entity, index) => (
              <TableRow
                key={entity.id}
                sx={{
                  backgroundColor:
                    index % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
                  '&:hover': {
                    backgroundColor: theme.palette.action.hover,
                  },
                }}
              >
                <TableCell sx={{ fontWeight: 500 }}>{entity.name}</TableCell>
                <TableCell>
                  <Chip
                    label={entity.entity_type}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={entity.tax_jurisdiction}
                    size="small"
                    color="secondary"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell
                  sx={{
                    maxWidth: 200,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {entity.description || '-'}
                </TableCell>
                <TableCell sx={{ fontSize: '0.875rem', color: 'text.secondary' }}>
                  {new Date(entity.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
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
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={!!deleteConfirm}
        title="Delete Entity?"
        description={`Are you sure you want to delete "${deleteConfirm?.name}"? This action cannot be undone.`}
        confirmAction={{
          label: 'Delete',
          variant: 'error',
          onClick: handleDeleteConfirm,
          loading: isDeleting,
        }}
        cancelAction={{
          label: 'Cancel',
          variant: 'outlined',
          onClick: () => setDeleteConfirm(null),
        }}
      />
    </>
  );
};

