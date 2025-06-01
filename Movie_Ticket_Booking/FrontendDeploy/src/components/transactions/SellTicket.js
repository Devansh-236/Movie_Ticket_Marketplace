import React, { useState } from 'react';
import { FiX, FiDollarSign } from 'react-icons/fi';
import { transactionAPI } from '../../services/api';
import toast from 'react-hot-toast';

const SellTicket = ({ onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        user_id: '',
        theatre_seat: '',
        sale_price: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.user_id || !formData.theatre_seat || !formData.sale_price) {
            toast.error('Please fill in all required fields');
            return;
        }

        setIsSubmitting(true);
        try {
            await transactionAPI.sellTicket({
                user_id: formData.user_id,
                theatre_seat: formData.theatre_seat,
                sale_price: parseFloat(formData.sale_price)
            });

            toast.success('Ticket sold successfully');
            onSuccess();
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Failed to sell ticket');
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
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>
                        <FiDollarSign size={24} />
                        Sell Ticket
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
                        <label className="form-label">Sale Price *</label>
                        <input
                            type="number"
                            name="sale_price"
                            value={formData.sale_price}
                            onChange={handleChange}
                            placeholder="0.00"
                            step="0.01"
                            min="0"
                            className="form-input"
                            required
                        />
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
                            <FiDollarSign size={16} />
                            {isSubmitting ? 'Processing...' : 'Sell Ticket'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default SellTicket;
