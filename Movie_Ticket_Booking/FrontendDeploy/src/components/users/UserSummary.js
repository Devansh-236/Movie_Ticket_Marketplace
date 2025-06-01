import React from 'react';
import { FiUser, FiDollarSign, FiTrendingUp, FiTrendingDown, FiCreditCard } from 'react-icons/fi';

const UserSummary = ({ userSummary }) => {
    if (!userSummary) {
        return (
            <div className="user-summary-placeholder">
                <p>No user data available</p>
            </div>
        );
    }

    const { user_info, financial_summary, recent_transactions } = userSummary;

    return (
        <div className="user-summary">
            {/* User Information Card */}
            <div className="user-info-card">
                <div className="card-header">
                    <FiUser size={24} />
                    <h2>User Information</h2>
                </div>

                <div className="user-details">
                    <div className="detail-item">
                        <span className="detail-label">User ID:</span>
                        <span className="detail-value">{user_info.userId}</span>
                    </div>

                    <div className="detail-item">
                        <span className="detail-label">Name:</span>
                        <span className="detail-value">{user_info.name}</span>
                    </div>

                    <div className="detail-item">
                        <span className="detail-label">Email:</span>
                        <span className="detail-value">{user_info.email}</span>
                    </div>

                    <div className="detail-item">
                        <span className="detail-label">Status:</span>
                        <span className={`status-badge ${user_info.status.toLowerCase()}`}>
                            {user_info.status}
                        </span>
                    </div>

                    <div className="detail-item">
                        <span className="detail-label">Member Since:</span>
                        <span className="detail-value">
                            {new Date(user_info.member_since).toLocaleDateString()}
                        </span>
                    </div>
                </div>
            </div>

            {/* Financial Summary */}
            <div className="financial-summary">
                <div className="card-header">
                    <FiDollarSign size={24} />
                    <h2>Financial Summary</h2>
                </div>

                <div className="summary-cards">
                    <div className="summary-card">
                        <div className="card-icon balance">
                            <FiDollarSign size={24} />
                        </div>
                        <div className="card-content">
                            <h3>Current Balance</h3>
                            <p className="amount balance">${financial_summary.current_balance.toFixed(2)}</p>
                        </div>
                    </div>

                    <div className="summary-card">
                        <div className="card-icon purchases">
                            <FiTrendingDown size={24} />
                        </div>
                        <div className="card-content">
                            <h3>Total Purchases</h3>
                            <p className="amount negative">${financial_summary.total_purchases.toFixed(2)}</p>
                        </div>
                    </div>

                    <div className="summary-card">
                        <div className="card-icon sales">
                            <FiTrendingUp size={24} />
                        </div>
                        <div className="card-content">
                            <h3>Total Sales</h3>
                            <p className="amount positive">${financial_summary.total_sales.toFixed(2)}</p>
                        </div>
                    </div>

                    <div className="summary-card">
                        <div className={`card-icon ${financial_summary.is_net_positive ? 'profit' : 'loss'}`}>
                            {financial_summary.is_net_positive ?
                                <FiTrendingUp size={24} /> :
                                <FiTrendingDown size={24} />
                            }
                        </div>
                        <div className="card-content">
                            <h3>Net P&L</h3>
                            <p className={`amount ${financial_summary.is_net_positive ? 'positive' : 'negative'}`}>
                                ${financial_summary.net_profit_loss.toFixed(2)}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Recent Transactions */}
            {recent_transactions && recent_transactions.length > 0 && (
                <div className="recent-transactions">
                    <div className="card-header">
                        <FiCreditCard size={24} />
                        <h3>Recent Transactions</h3>
                    </div>

                    <div className="transactions-list">
                        {recent_transactions.map((transaction, index) => (
                            <div key={index} className="transaction-item">
                                <div className="transaction-info">
                                    <div className="transaction-main">
                                        <span className={`transaction-type ${transaction.transactionType.toLowerCase()}`}>
                                            {transaction.transactionType}
                                        </span>
                                        <span className="transaction-description">
                                            {transaction.description}
                                        </span>
                                    </div>

                                    {transaction.movie && (
                                        <div className="transaction-details">
                                            <span className="detail-text">Movie: {transaction.movie}</span>
                                            {transaction.theatreSeat && (
                                                <span className="detail-text">Seat: {transaction.theatreSeat}</span>
                                            )}
                                        </div>
                                    )}

                                    {transaction.timestamp && (
                                        <div className="transaction-date">
                                            {new Date(transaction.timestamp).toLocaleDateString('en-US', {
                                                year: 'numeric',
                                                month: 'short',
                                                day: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit'
                                            })}
                                        </div>
                                    )}
                                </div>

                                <div className="transaction-amount">
                                    <span className={`amount ${transaction.transactionType === 'SALE' ? 'positive' : 'negative'}`}>
                                        {transaction.transactionType === 'SALE' ? '+' : '-'}
                                        ${Math.abs(transaction.amount).toFixed(2)}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Performance Metrics */}
            <div className="performance-metrics">
                <div className="card-header">
                    <FiTrendingUp size={24} />
                    <h3>Performance Metrics</h3>
                </div>

                <div className="metrics-grid">
                    <div className="metric-item">
                        <span className="metric-label">Transaction Count</span>
                        <span className="metric-value">
                            {(recent_transactions?.length || 0)}
                        </span>
                    </div>

                    <div className="metric-item">
                        <span className="metric-label">Average Transaction</span>
                        <span className="metric-value">
                            ${recent_transactions?.length > 0 ?
                                (recent_transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0) / recent_transactions.length).toFixed(2) :
                                '0.00'
                            }
                        </span>
                    </div>

                    <div className="metric-item">
                        <span className="metric-label">Profit Margin</span>
                        <span className={`metric-value ${financial_summary.is_net_positive ? 'positive' : 'negative'}`}>
                            {financial_summary.total_purchases > 0 ?
                                ((financial_summary.net_profit_loss / financial_summary.total_purchases) * 100).toFixed(1) :
                                '0.0'
                            }%
                        </span>
                    </div>

                    <div className="metric-item">
                        <span className="metric-label">Account Status</span>
                        <span className={`metric-value ${financial_summary.current_balance >= 0 ? 'positive' : 'negative'}`}>
                            {financial_summary.current_balance >= 0 ? 'Positive' : 'Negative'}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserSummary;
