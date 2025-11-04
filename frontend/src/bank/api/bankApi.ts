/**
 * Banking API
 * 
 * All banking-related API methods including:
 * - Banks (CRUD operations)
 * - Bank Accounts (CRUD operations)
 * - Bank Account Balances (CRUD operations)
 */

import { ApiClient } from '@/shared/api';
import {
  Bank,
  BankAccount,
  BankAccountBalance,
  CreateBankRequest,
  CreateBankAccountRequest,
  CreateBankAccountBalanceRequest,
  GetBanksResponse,
  GetBankResponse,
  GetBankAccountsResponse,
  GetBankAccountResponse,
  GetBankAccountBalancesResponse,
  GetBankAccountBalanceResponse,
  GetBanksQueryParams,
  GetBankAccountsQueryParams,
  GetBankAccountBalancesQueryParams
} from '../types';

export class BankingApi {
  constructor(private client: ApiClient) {}

  // ============================================================================
  // BANKS
  // ============================================================================

  /**
   * Get all banks with optional filters.
   */
  async getBanks(params: GetBanksQueryParams = {}): Promise<GetBanksResponse> {
    return this.client.get<GetBanksResponse>('/api/banks', params);
  }

  /**
   * Get a single bank by ID.
   */
  async getBank(
    bankId: number, 
    params: {
      include_bank_accounts?: boolean;
      include_bank_account_balances?: boolean;
    } = {}
  ): Promise<GetBankResponse> {
    return this.client.get<GetBankResponse>(`/api/banks/${bankId}`, params);
  }

  /**
   * Create a new bank.
   */
  async createBank(data: CreateBankRequest): Promise<Bank> {
    return this.client.post<Bank>('/api/banks', data);
  }

  // Note: UPDATE functionality not yet implemented in backend
  // When backend implements PUT /api/banks/<id>, add updateBank() method here

  /**
   * Delete a bank.
   */
  async deleteBank(bankId: number): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(`/api/banks/${bankId}`);
  }

  // ============================================================================
  // BANK ACCOUNTS
  // ============================================================================

  /**
   * Get all bank accounts with optional filters.
   */
  async getBankAccounts(params: GetBankAccountsQueryParams = {}): Promise<GetBankAccountsResponse> {
    return this.client.get<GetBankAccountsResponse>('/api/bank-accounts', params);
  }

  /**
   * Get all bank accounts for a specific bank (nested endpoint).
   */
  async getBankAccountsByBankId(
    bankId: number,
    params: {
      include_bank_account_balances?: boolean;
    } = {}
  ): Promise<GetBankAccountsResponse> {
    return this.client.get<GetBankAccountsResponse>(`/api/banks/${bankId}/bank-accounts`, params);
  }

  /**
   * Get a single bank account by ID (nested endpoint).
   */
  async getBankAccount(
    bankId: number,
    bankAccountId: number,
    params: {
      include_bank_account_balances?: boolean;
    } = {}
  ): Promise<GetBankAccountResponse> {
    return this.client.get<GetBankAccountResponse>(`/api/banks/${bankId}/bank-accounts/${bankAccountId}`, params);
  }

  /**
   * Create a new bank account for a specific bank.
   */
  async createBankAccount(bankId: number, data: CreateBankAccountRequest): Promise<BankAccount> {
    return this.client.post<BankAccount>(`/api/banks/${bankId}/bank-accounts`, data);
  }

  // Note: UPDATE functionality not yet implemented in backend
  // When backend implements PUT /api/banks/<bank_id>/bank-accounts/<id>, add updateBankAccount() method here

  /**
   * Delete a bank account.
   */
  async deleteBankAccount(bankId: number, bankAccountId: number): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(`/api/banks/${bankId}/bank-accounts/${bankAccountId}`);
  }

  // ============================================================================
  // BANK ACCOUNT BALANCES
  // ============================================================================

  /**
   * Get all bank account balances with optional filters.
   */
  async getBankAccountBalances(params: GetBankAccountBalancesQueryParams = {}): Promise<GetBankAccountBalancesResponse> {
    return this.client.get<GetBankAccountBalancesResponse>('/api/bank-account-balances', params);
  }

  /**
   * Get all bank account balances for a specific bank account (nested endpoint).
   */
  async getBankAccountBalancesByBankAccount(
    bankId: number,
    bankAccountId: number
  ): Promise<GetBankAccountBalancesResponse> {
    return this.client.get<GetBankAccountBalancesResponse>(`/api/banks/${bankId}/bank-accounts/${bankAccountId}/bank-account-balances`);
  }

  /**
   * Get a single bank account balance by ID (nested endpoint).
   */
  async getBankAccountBalance(
    bankId: number,
    bankAccountId: number,
    balanceId: number
  ): Promise<GetBankAccountBalanceResponse> {
    return this.client.get<GetBankAccountBalanceResponse>(`/api/banks/${bankId}/bank-accounts/${bankAccountId}/bank-account-balances/${balanceId}`);
  }

  /**
   * Create a new bank account balance for a specific bank account.
   */
  async createBankAccountBalance(
    bankId: number,
    bankAccountId: number,
    data: CreateBankAccountBalanceRequest
  ): Promise<BankAccountBalance> {
    return this.client.post<BankAccountBalance>(`/api/banks/${bankId}/bank-accounts/${bankAccountId}/bank-account-balances`, data);
  }

  // Note: UPDATE functionality not yet implemented in backend
  // When backend implements PUT /api/banks/<bank_id>/bank-accounts/<bank_account_id>/bank-account-balances/<id>, add updateBankAccountBalance() method here

  /**
   * Delete a bank account balance.
   */
  async deleteBankAccountBalance(
    bankId: number,
    bankAccountId: number,
    balanceId: number
  ): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(`/api/banks/${bankId}/bank-accounts/${bankAccountId}/bank-account-balances/${balanceId}`);
  }
}

