import React, { useState } from 'react';
import { FiX, FiShoppingCart } from 'react-icons/fi';
import { transactionAPI } from '../../services/api';
import toast from 'react-hot-toast';

const PurchaseTicket = ({ onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        user_id: '',
        theatre_seat: '',
        purchase_price: '',
        payment_method: 'credit_card'
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const paymentMethods = [
        { value: 'credit_card', label: 'Credit Card' },
        { value: 'debit_card', label: 'Debit Card' },
        { value: 'cash', label: 'Cash' },
        { value: 'digital_wallet', label: 'Digital Wallet' }
    ];

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.user_id || !formData.theatre_seat || !formData.purchase_price) {
            toast.error('Please fill in all required fields');
            return;
        }

        setIsSubmitting(true);
        try {
            await transactionAPI.purchaseTicket({
                user_id: formData.user_id,
                theatre_seat: formData.theatre_seat,
                purchase_price: parseFloat(formData.purchase_price),
                payment_method: formData.payment_method
            });

            toast.success('Ticket purchased successfully');
            onSuccess();
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Failed to purchase ticket');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>
                        <FiShoppingCart size={24} />
                        Purchase Ticket
                    </h2>
                    <button className="modal-close" onClick={onClose}>
                        <FiX size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="modal-form">
                    <div className="form-group">
                        <label className="form-label">User ID *</label>
                        <input
                            type="text"
                            name="user_id"
                            value={formData.user_id}
                            onChange={handleChange}
                            placeholder="Enter user ID"
                            className="form-input"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Theatre Seat *</label>
                        <input
                            type="text"
                            name="theatre_seat"
                            value={formData.theatre_seat}
                            onChange={handleChange}
                            placeholder="e.g., A1, B5, C10"
                            className="form-input"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Purchase Price *</label>
                        <input
                            type="number"
                            name="purchase_price"
                            value={formData.purchase_price}
                            onChange={handleChange}
                            placeholder="0.00"
                            step="0.01"
                            min="0"
                            className="form-input"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Payment Method</label>
                        <select
                            name="payment_method"
                            value={formData.payment_method}
                            onChange={handleChange}
                            className="form-input"
                        >
                            {paymentMethods.map(method => (
                                <option key={method.value} value={method.value}>
                                    {method.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="modal-actions">
                        <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={onClose}
                        >
                            Cancel
                        </button>

                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={isSubmitting}
                        >
                            <FiShoppingCart size={16} />
                            {isSubmitting ? 'Processing...' : 'Purchase Ticket'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default PurchaseTicket;
