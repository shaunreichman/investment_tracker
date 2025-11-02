import React from 'react';
import {
  Box,
  Typography,
  Link,
} from '@mui/material';
import {
  Language,
  Phone,
  Email,
} from '@mui/icons-material';
import { ContactInfoProps } from '../types/company-details-tab.types';

export const ContactInfo: React.FC<ContactInfoProps> = ({ contacts, website }) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Contact Information
      </Typography>
      
      {website && (
        <Box display="flex" alignItems="center" mb={2}>
          <Language sx={{ mr: 2, color: 'text.secondary' }} />
          <Link href={website} target="_blank" rel="noopener noreferrer">
            {website}
          </Link>
        </Box>
      )}

      {contacts && contacts.length > 0 && (
        <>
          {contacts.map((contact) => (
            <Box key={contact.id} mb={2}>
              {contact.name && (
                <Typography variant="subtitle2" gutterBottom>
                  {contact.name}
                  {contact.title && ` - ${contact.title}`}
                </Typography>
              )}
              
              {contact.direct_email && (
                <Box display="flex" alignItems="center" mb={1}>
                  <Email sx={{ mr: 2, color: 'text.secondary' }} />
                  <Link href={`mailto:${contact.direct_email}`}>
                    {contact.direct_email}
                  </Link>
                </Box>
              )}
              
              {contact.direct_number && (
                <Box display="flex" alignItems="center" mb={1}>
                  <Phone sx={{ mr: 2, color: 'text.secondary' }} />
                  <Link href={`tel:${contact.direct_number}`}>
                    {contact.direct_number}
                  </Link>
                </Box>
              )}
            </Box>
          ))}
        </>
      )}
    </Box>
  );
};
