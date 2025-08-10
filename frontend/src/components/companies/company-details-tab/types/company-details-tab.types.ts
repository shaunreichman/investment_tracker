import { CompanyDetailsResponse } from '../../../../types/api';

export interface CompanyDetailsTabProps {
  data: CompanyDetailsResponse;
  loading: boolean;
}

export interface CompanyInfoProps {
  company: CompanyDetailsResponse['company'];
}

export interface ContactInfoProps {
  contacts: CompanyDetailsResponse['company']['contacts'];
  website?: string | null;
}

export interface BusinessDetailsProps {
  company: CompanyDetailsResponse['company'];
}
