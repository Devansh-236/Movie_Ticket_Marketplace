import React, { useState } from 'react';
import { FiTrendingUp, FiTrendingDown, FiUsers } from 'react-icons/fi';
import { FaTrophy } from 'react-icons/fa';
import { useApi } from '../../hooks/useApi';
import { userAPI } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

const Leaderboard = () => {
    const [limit, setLimit] = useState(10);
    const [order, setOrder] = useState('desc');

    const { data: leaderboardData, loading, error, refetch } = useApi(
        () => userAPI.getLeaderboard(limit, order),
        [limit, order] // Dependencies on limit and order
    );

    const leaderboard = leaderboardData?.leaderboard || [];

    const getRankIcon = (rank) => {
        switch (rank) {
            case 1: return '🥇';
            case 2: return '🥈';
            case 3: return '🥉';
            default: return rank;
        }
    };

    if (loading) return <LoadingSpinner text="Loading leaderboard..." />;
    if (error) return <ErrorMessage message={error.message} onRetry={refetch} />;

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="page-title-section">
                    <h1 className="page-title">
                        <FaTrophy size={28} />
                        Payroll Leaderboard
                    </h1>

                    <p className="page-subtitle">Top performers by net profit/loss</p>
                </div>
            </div>

            <div className="leaderboard-controls">
                <div className="control-group">
                    <label>Show:</label>
                    <select
                        value={limit}
                        onChange={(e) => setLimit(Number(e.target.value))}
                        className="control-select"
                    >
                        <option value={5}>Top 5</option>
                        <option value={10}>Top 10</option>
                        <option value={25}>Top 25</option>
                        <option value={50}>Top 50</option>
                    </select>
                </div>

                <div className="control-group">
                    <label>Order:</label>
                    <select
                        value={order}
                        onChange={(e) => setOrder(e.target.value)}
                        className="control-select"
                    >
                        <option value="desc">Highest to Lowest</option>
                        <option value="asc">Lowest to Highest</option>
                    </select>
                </div>
            </div>

            {leaderboard.length > 0 ? (
                <div className="leaderboard-list">
                    {leaderboard.map((user) => (
                        <div key={user.userId} className={`leaderboard-item rank-${user.rank}`}>
                            <div className="rank-section">
                                <span className="rank-number">{getRankIcon(user.rank)}</span>
                            </div>

                            <div className="user-section">
                                <div className="user-info">
                                    <h3 className="user-name">{user.name}</h3>
                                    <p className="user-id">{user.userId}</p>
                                </div>
                            </div>

                            <div className="stats-section">
                                <div className="stat-item">
                                    <span className="stat-label">Current Balance</span>
                                    <span className="stat-value balance">
                                        ${user.currentBalance.toFixed(2)}
                                    </span>
                                </div>

                                <div className="stat-item">
                                    <span className="stat-label">Net P&L</span>
                                    <span className={`stat-value ${user.isNetPositive ? 'positive' : 'negative'}`}>
                                        {user.isNetPositive ? <FiTrendingUp size={16} /> : <FiTrendingDown size={16} />}
                                        ${user.netProfitLoss.toFixed(2)}
                                    </span>
                                </div>

                                <div className="stat-item">
                                    <span className="stat-label">Total Sales</span>
                                    <span className="stat-value sales">
                                        ${user.totalSales.toFixed(2)}
                                    </span>
                                </div>

                                <div className="stat-item">
                                    <span className="stat-label">Total Purchases</span>
                                    <span className="stat-value purchases">
                                        ${user.totalPurchases.toFixed(2)}
                                    </span>
                                </div>

                                <div className="stat-item">
                                    <span className="stat-label">Transactions</span>
                                    <span className="stat-value transactions">
                                        {user.totalTransactions}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    <FiUsers size={48} />
                    <h3>No users found</h3>
                    <p>Create some users to see the leaderboard</p>
                </div>
            )}
        </div>
    );
};

export default Leaderboard;
