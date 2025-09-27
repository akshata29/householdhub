"use client";

import * as React from "react";
import { 
  ChevronRight,
  Wallet,
  PiggyBank,
  CircleDollarSign,
  Clock,
} from "lucide-react";
import { formatCurrency, formatPercentage } from "@/lib/utils";
import { Account } from "@/lib/schemas";

interface AccountsListProps {
  title?: string;
  accounts: Account[];
  loading?: boolean;
  error?: string;
  onAccountClick?: (account: Account) => void;
  className?: string;
}

function getAccountIcon(type: Account['type']) {
  switch (type) {
    case 'checking':
      return Wallet;
    case 'savings':
      return PiggyBank;
    case 'money-market':
      return CircleDollarSign;
    case 'cd':
      return Clock;
    default:
      return Wallet;
  }
}

function getAccountTypeLabel(type: Account['type']) {
  switch (type) {
    case 'checking':
      return 'Checking';
    case 'savings':
      return 'Savings';
    case 'money-market':
      return 'Money Market';
    case 'cd':
      return 'Certificate of Deposit';
    case 'investment':
      return 'Investment';
    case 'retirement':
      return 'Retirement';
    default:
      return type;
  }
}

export function AccountsList({
  title = "Cash Accounts",
  accounts,
  loading = false,
  error,
  onAccountClick,
  className,
}: AccountsListProps) {
  if (loading) {
    return (
      <div className="loading-state">Loading accounts...</div>
    );
  }

  if (error) {
    return (
      <div className="empty-state">
        <h3>Failed to load accounts</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!accounts.length) {
    return (
      <div className="empty-state">
        <h3>No accounts</h3>
        <p>No accounts to display</p>
      </div>
    );
  }

  return (
    <div className="accounts-container">
      {accounts.map((account) => {
        const Icon = getAccountIcon(account.type);
        
        return (
          <div
            key={account.id}
            className="account-item"
            onClick={() => onAccountClick?.(account)}
            style={{ cursor: onAccountClick ? 'pointer' : 'default' }}
          >
            <div className="account-icon">
              <Icon size={20} color="#0f766e" />
            </div>
            
            <div className="account-info">
              <h4>{account.name}</h4>
              <p>{getAccountTypeLabel(account.type)}</p>
              {account.institution && (
                <p style={{ fontSize: '11px', color: '#94a3b8' }}>
                  {account.institution}
                </p>
              )}
            </div>
            
            <div className="account-balance">
              <div className="amount font-tabular">
                {formatCurrency(account.balance)}
              </div>
              {account.apy && (
                <div style={{ fontSize: '11px', color: '#64748b' }}>
                  {formatPercentage(account.apy / 100)} APY
                </div>
              )}
            </div>
            
            {onAccountClick && (
              <ChevronRight size={16} color="#94a3b8" />
            )}
          </div>
        );
      })}
    </div>
  );
}