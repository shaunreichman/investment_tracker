import React from 'react';
import {
  TableHead,
  TableRow,
  TableCell
} from '@mui/material';

export interface TableHeaderProps {
  isNavBasedFund: boolean;
  showTaxEvents: boolean;
}

const TableHeaderComponent: React.FC<TableHeaderProps> = ({
  isNavBasedFund,
  showTaxEvents
}) => {
  const headerCellStyle = {
    py: { xs: 1, sm: 1.5 },
    px: { xs: 1, sm: 2 },
    fontWeight: 600,
    fontSize: { xs: 12, sm: 13 },
    backgroundColor: 'background.sidebar',
    borderBottom: 2,
    borderColor: 'divider',
    color: 'text.primary'
  };

  const rightAlignedHeaderStyle = {
    ...headerCellStyle,
    align: 'right' as const,
    py: 1.5,
    px: 2,
    fontSize: 13
  };

  return (
    <TableHead>
      <TableRow>
        <TableCell sx={headerCellStyle}>
          Date
        </TableCell>
        <TableCell sx={headerCellStyle}>
          Type
        </TableCell>
        <TableCell sx={headerCellStyle}>
          Description
        </TableCell>
        <TableCell 
          align="center" 
          sx={headerCellStyle}
        >
          Equity
        </TableCell>
        {isNavBasedFund && (
          <TableCell 
            align="center" 
            sx={headerCellStyle}
          >
            Nav Update
          </TableCell>
        )}
        <TableCell 
          align="center" 
          sx={headerCellStyle}
        >
          Distributions
        </TableCell>
        {showTaxEvents && (
          <TableCell sx={rightAlignedHeaderStyle}>
            Tax
          </TableCell>
        )}
        <TableCell sx={rightAlignedHeaderStyle}>
          Actions
        </TableCell>
      </TableRow>
    </TableHead>
  );
};

/**
 * Custom comparator for React.memo to only compare fields that affect rendering
 * This prevents unnecessary re-renders when irrelevant fields change
 */
const tableHeaderPropsAreEqual = (prevProps: TableHeaderProps, nextProps: TableHeaderProps): boolean => {
  return (
    prevProps.isNavBasedFund === nextProps.isNavBasedFund &&
    prevProps.showTaxEvents === nextProps.showTaxEvents
  );
};

export default React.memo(TableHeaderComponent, tableHeaderPropsAreEqual);