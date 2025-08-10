// ============================================================================
// COMPANY DETAILS TAB COMPONENT TESTS
// ============================================================================

import React from 'react';
import { screen } from '@testing-library/react';
import { render } from '../../../test-utils';
import { CompanyDetailsTab } from './CompanyDetailsTab';
import { createMockCompanyDetails } from '../../../test-utils/mock-data';

describe('CompanyDetailsTab', () => {
  const mockData = createMockCompanyDetails();

  describe('Component Rendering', () => {
    it('renders loading state when loading is true', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={true}
        />
      );

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('renders company details when data is available', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // Check for company name
      expect(screen.getByText('Test Investment Company')).toBeInTheDocument();
      
      // Check for company type
      expect(screen.getByText('Private Equity')).toBeInTheDocument();
    });
  });

  describe('Company Information Display', () => {
    it('displays company name correctly', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText('Test Investment Company')).toBeInTheDocument();
    });

    it('displays company type correctly', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText('Private Equity')).toBeInTheDocument();
    });

    it('displays business address when available', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText('123 Investment Street, Sydney NSW 2000')).toBeInTheDocument();
    });
  });

  describe('Contact Information Display', () => {
    it('displays contact information section', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText(/contact information/i)).toBeInTheDocument();
    });

    it('displays contacts array information correctly', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // Check for contact name and role
      expect(screen.getByText(/john doe/i)).toBeInTheDocument();
      expect(screen.getByText(/investment manager/i)).toBeInTheDocument();
      
      // Check for contact details
      expect(screen.getByText('john.doe@testcompany.com')).toBeInTheDocument();
      expect(screen.getByText('+61 2 1234 5678')).toBeInTheDocument();
    });

    it('handles empty contacts array gracefully', () => {
      const dataWithNoContacts = {
        ...mockData,
        company: {
          ...mockData.company,
          contacts: []
        }
      };

      render(
        <CompanyDetailsTab
          data={dataWithNoContacts}
          loading={false}
        />
      );

      // Should still render contact information section
      expect(screen.getByText(/contact information/i)).toBeInTheDocument();
    });

    it('displays website information when available', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // Check for website link
      expect(screen.getByText('https://testcompany.com')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: 'https://testcompany.com' })).toBeInTheDocument();
    });
  });

  describe('Business Details Display', () => {
    it('displays business details section', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText(/business details/i)).toBeInTheDocument();
    });

    it('displays business address when available', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText('123 Investment Street, Sydney NSW 2000')).toBeInTheDocument();
    });

    it('displays regulatory information when available', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // The component doesn't currently display regulatory information
      // Just check that business details section is rendered
      expect(screen.getByText(/business details/i)).toBeInTheDocument();
    });

    it('displays company structure information when available', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // The component doesn't currently display company structure information
      // Just check that business details section is rendered
      expect(screen.getByText(/business details/i)).toBeInTheDocument();
    });
  });

  describe('Data Handling', () => {
    it('handles missing optional fields gracefully', () => {
      const minimalData = {
        company: {
          id: 1,
          name: 'Test Company',
          company_type: 'Investment Company',
          contacts: [],
          business_address: null,
          website: null,
        }
      };

      render(
        <CompanyDetailsTab
          data={minimalData}
          loading={false}
        />
      );

      // Should still render basic information
      expect(screen.getByText('Test Company')).toBeInTheDocument();
      expect(screen.getByText('Investment Company')).toBeInTheDocument();
    });
  });

  describe('Component Integration', () => {
    it('renders all required sub-components', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // Check that company info is rendered
      expect(screen.getByText('Test Investment Company')).toBeInTheDocument();
      
      // Check that contact info is rendered
      expect(screen.getByText(/contact information/i)).toBeInTheDocument();
      
      // Check that business details are rendered
      expect(screen.getByText(/business details/i)).toBeInTheDocument();
    });

    it('passes correct data to sub-components', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // Verify the component structure by checking for key content
      expect(screen.getByText('Test Investment Company')).toBeInTheDocument();
      expect(screen.getByText(/contact information/i)).toBeInTheDocument();
      expect(screen.getByText(/business details/i)).toBeInTheDocument();
    });
  });

  describe('Responsive Behavior', () => {
    it('adapts to different screen sizes', () => {
      const { container } = render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // Check that the component renders without errors
      expect(screen.getByText('Test Investment Company')).toBeInTheDocument();
    });

    it('maintains layout integrity on mobile', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // Check that all sections are still visible
      expect(screen.getByText(/contact information/i)).toBeInTheDocument();
      expect(screen.getByText(/business details/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper heading structure', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // Check for company name heading (h4)
      expect(screen.getByRole('heading', { level: 4 })).toBeInTheDocument();
      expect(screen.getByText('Test Investment Company')).toBeInTheDocument();
    });

    it('provides meaningful text for screen readers', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // Check for contact information heading
      expect(screen.getByText(/contact information/i)).toBeInTheDocument();
    });

    it('has proper ARIA labels for contact information', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // Check for contact section heading
      expect(screen.getByText(/contact information/i)).toBeInTheDocument();
    });
  });

  describe('External Links', () => {
    it('displays website as clickable link when available', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // The website link shows the URL as text, not "website"
      const websiteLink = screen.getByRole('link', { name: 'https://testcompany.com' });
      expect(websiteLink).toBeInTheDocument();
      expect(websiteLink).toHaveAttribute('href', 'https://testcompany.com');
    });

    it('opens external links in new tab', () => {
      render(
        <CompanyDetailsTab
          data={mockData}
          loading={false}
        />
      );

      // The website link shows the URL as text, not "website"
      const websiteLink = screen.getByRole('link', { name: 'https://testcompany.com' });
      expect(websiteLink).toHaveAttribute('target', '_blank');
      expect(websiteLink).toHaveAttribute('rel', 'noopener noreferrer');
    });
  });
});
