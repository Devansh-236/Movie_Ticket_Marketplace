import React, { useState } from 'react';
import { FiSearch, FiUser, FiDollarSign, FiTrendingUp, FiTrendingDown } from 'react-icons/fi';
import { userAPI } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import toast from 'react-hot-toast';

const UserProfile = () => {
    const [userId, setUserId] = useState('');
    const [userSummary, setUserSummary] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();

        if (!userId.trim()) {
            toast.error('Please enter a user ID');
            return;
        }

        setLoading(true);
        try {
            const response = await userAPI.getUserSummary(userId);
            setUserSummary(response.data);
        } catch (error) {
            toast.error(error.response?.data?.detail || 'User not found');
            setUserSummary(null);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="page-title-section">
                    <h1 className="page-title">User Profile</h1>
                    <p className="page-subtitle">Search and view user information</p>
                </div>
            </div>

            <div className="search-section">
                <form onSubmit={handleSearch} className="search-form">
                    <div className="search-input-group">
                        <FiSearch size={20} />
                        <input
                            type="text"
                            value={userId}
                            onChange={(e) => setUserId(e.target.value)}
                            placeholder="Enter User ID to search..."
                            className="search-input"
                        />
                        <button type="submit" className="btn btn-primary" disabled={loading}>
                            {loading ? 'Searching...' : 'Search'}
                        </button>
                    </div>
                </form>
            </div>

            {loading && <LoadingSpinner text="Loading user data..." />}

            {userSummary && (
                <div className="user-summary">
                    <div className="user-info-card">
                        <div className="card-header">
                            <FiUser size={24} />
                            <h2>User Information</h2>
                        </div>

                        <div className="user-details">
                            <div className="detail-item">
                                <span className="detail-label">User ID:</span>
                                <span className="detail-value">{userSummary.user_info.userId}</span>
                            </div>

                            <div className="detail-item">
                                <span className="detail-label">Name:</span>
                                <span className="detail-value">{userSummary.user_info.name}</span>
                            </div>

                            <div className="detail-item">
                                <span className="detail-label">Email:</span>
                                <span className="detail-value">{userSummary.user_info.email}</span>
                            </div>

                            <div className="detail-item">
                                <span className="detail-label">Status:</span>
                                <span className={`status-badge ${userSummary.user_info.status.toLowerCase()}`}>
                                    {userSummary.user_info.status}
                                </span>
                            </div>

                            <div className="detail-item">
                                <span className="detail-label">Member Since:</span>
                                <span className="detail-value">
                                    {new Date(userSummary.user_info.member_since).toLocaleDateString()}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="financial-summary">
                        <div className="summary-cards">
                            <div className="summary-card">
                                <div className="card-icon balance">
                                    <FiDollarSign size={24} />
                                </div>
                                <div className="card-content">
                                    <h3>Current Balance</h3>
                                    <p className="amount">${userSummary.financial_summary.current_balance.toFixed(2)}</p>
                                </div>
                            </div>

                            <div className="summary-card">
                                <div className="card-icon purchases">
                                    <FiTrendingDown size={24} />
                                </div>
                                <div className="card-content">
                                    <h3>Total Purchases</h3>
                                    <p className="amount negative">${userSummary.financial_summary.total_purchases.toFixed(2)}</p>
                                </div>
                            </div>

                            <div className="summary-card">
                                <div className="card-icon sales">
                                    <FiTrendingUp size={24} />
                                </div>
                                <div className="card-content">
                                    <h3>Total Sales</h3>
                                    <p className="amount positive">${userSummary.financial_summary.total_sales.toFixed(2)}</p>
                                </div>
                            </div>

                            <div className="summary-card">
                                <div className={`card-icon ${userSummary.financial_summary.is_net_positive ? 'profit' : 'loss'}`}>
                                    {userSummary.financial_summary.is_net_positive ?
                                        <FiTrendingUp size={24} /> :
                                        <FiTrendingDown size={24} />
                                    }
                                </div>
                                <div className="card-content">
                                    <h3>Net P&L</h3>
                                    <p className={`amount ${userSummary.financial_summary.is_net_positive ? 'positive' : 'negative'}`}>
                                        ${userSummary.financial_summary.net_profit_loss.toFixed(2)}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {userSummary.recent_transactions && userSummary.recent_transactions.length > 0 && (
                        <div className="recent-transactions">
                            <h3>Recent Transactions</h3>
                            <div className="transactions-list">
                                {userSummary.recent_transactions.map((transaction, index) => (
                                    <div key={index} className="transaction-item">
                                        <div className="transaction-info">
                                            <span className="transaction-type">{transaction.transactionType}</span>
                                            <span className="transaction-description">{transaction.description}</span>
                                        </div>
                                        <div className="transaction-amount">
                                            <span className={transaction.transactionType === 'SALE' ? 'positive' : 'negative'}>
                                                ${Math.abs(transaction.amount).toFixed(2)}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default UserProfile;
