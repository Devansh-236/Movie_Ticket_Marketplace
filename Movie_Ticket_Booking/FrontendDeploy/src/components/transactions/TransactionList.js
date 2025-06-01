import React, { useState } from 'react';
import { FiSearch, FiShoppingCart, FiDollarSign, FiCreditCard } from 'react-icons/fi';
import { transactionAPI } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import PurchaseTicket from './PurchaseTicket';
import SellTicket from './SellTicket';
import toast from 'react-hot-toast';

const TransactionList = () => {
    const [userId, setUserId] = useState('');
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showPurchaseModal, setShowPurchaseModal] = useState(false);
    const [showSellModal, setShowSellModal] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();

        if (!userId.trim()) {
            toast.error('Please enter a user ID');
            return;
        }

        setLoading(true);
        try {
            const response = await transactionAPI.getUserTransactions(userId);
            setTransactions(response.data.transactions || []);
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Failed to fetch transactions');
            setTransactions([]);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getTransactionIcon = (type) => {
        switch (type) {
            case 'PURCHASE': return <FiShoppingCart size={20} />;
            case 'SALE': return <FiDollarSign size={20} />;
            default: return <FiCreditCard size={20} />;
        }
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="page-title-section">
                    <h1 className="page-title">Transactions</h1>
                    <p className="page-subtitle">View and manage user transactions</p>
                </div>

                <div className="header-actions">
                    <button
                        className="btn btn-primary"
                        onClick={() => setShowPurchaseModal(true)}
                    >
                        <FiShoppingCart size={16} />
                        Purchase Ticket
                    </button>

                    <button
                        className="btn btn-secondary"
                        onClick={() => setShowSellModal(true)}
                    >
                        <FiDollarSign size={16} />
                        Sell Ticket
                    </button>
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
                            placeholder="Enter User ID to view transactions..."
                            className="search-input"
                        />
                        <button type="submit" className="btn btn-primary" disabled={loading}>
                            {loading ? 'Searching...' : 'Search'}
                        </button>
                    </div>
                </form>
            </div>

            {loading && <LoadingSpinner text="Loading transactions..." />}

            {transactions.length > 0 && (
                <div className="transactions-container">
                    <div className="transactions-header">
                        <h2>Transactions for User: {userId}</h2>
                        <span className="transaction-count">{transactions.length} transactions</span>
                    </div>

                    <div className="transactions-list">
                        {transactions.map((transaction) => (
                            <div key={transaction.transactionId} className="transaction-card">
                                <div className="transaction-icon">
                                    {getTransactionIcon(transaction.transactionType)}
                                </div>

                                <div className="transaction-details">
                                    <div className="transaction-main">
                                        <h3 className="transaction-title">{transaction.description}</h3>
                                        <span className={`transaction-type ${transaction.transactionType.toLowerCase()}`}>
                                            {transaction.transactionType}
                                        </span>
                                    </div>

                                    <div className="transaction-info">
                                        <div className="info-item">
                                            <span className="info-label">Movie:</span>
                                            <span className="info-value">{transaction.movie}</span>
                                        </div>

                                        <div className="info-item">
                                            <span className="info-label">Seat:</span>
                                            <span className="info-value">{transaction.theatreSeat}</span>
                                        </div>

                                        <div className="info-item">
                                            <span className="info-label">Date:</span>
                                            <span className="info-value">{formatDate(transaction.timestamp)}</span>
                                        </div>

                                        <div className="info-item">
                                            <span className="info-label">Status:</span>
                                            <span className={`status-badge ${transaction.status.toLowerCase()}`}>
                                                {transaction.status}
                                            </span>
                                        </div>
                                    </div>
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

            {showPurchaseModal && (
                <PurchaseTicket
                    onClose={() => setShowPurchaseModal(false)}
                    onSuccess={() => {
                        setShowPurchaseModal(false);
                        if (userId) handleSearch({ preventDefault: () => { } });
                    }}
                />
            )}

            {showSellModal && (
                <SellTicket
                    onClose={() => setShowSellModal(false)}
                    onSuccess={() => {
                        setShowSellModal(false);
                        if (userId) handleSearch({ preventDefault: () => { } });
                    }}
                />
            )}
        </div>
    );
};

export default TransactionList;
