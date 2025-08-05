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

const TableHeader: React.FC<TableHeaderProps> = ({
  isNavBasedFund,
  showTaxEvents
}) => {
  const headerCellStyle = {
    py: { xs: 1, sm: 1.5 },
    px: { xs: 1, sm: 2 },
    fontWeight: 600,
    fontSize: { xs: 12, sm: 13 },
    backgroundColor: 'grey.50',
    borderBottom: 2,
    borderColor: 'grey.300',
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

export default TableHeader; 