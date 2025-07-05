import React, { useState } from 'react';
import { FiX, FiDollarSign } from 'react-icons/fi';
import { transactionAPI } from '../../services/api';
import toast from 'react-hot-toast';

const SellTicket = ({ onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        user_id: '',
        theatre_seat: '',
        sale_price: '',
        buyer_id: ''  // Added missing field
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Updated validation to include buyer_id
        if (!formData.user_id || !formData.theatre_seat || !formData.sale_price || !formData.buyer_id) {
            toast.error('Please fill in all required fields');
            return;
        }

        setIsSubmitting(true);
        try {
            await transactionAPI.sellTicket({
                user_id: formData.user_id,
                theatre_seat: formData.theatre_seat,
                sale_price: parseInt(formData.sale_price, 10),
                buyer_id: formData.buyer_id  // Added missing field
            });

            toast.success('Ticket sold successfully');
            onSuccess();
        } catch (error) {
            console.error('Sell ticket error:', error);

            let errorMessage = 'Failed to sell ticket';

            if (error.response?.data?.detail) {
                if (Array.isArray(error.response.data.detail)) {
                    const messages = error.response.data.detail
                        .map(err => {
                            if (typeof err === 'string') return err;
                            if (err.msg && err.loc) return `${err.loc.join('.')} - ${err.msg}`;
                            if (err.msg) return err.msg;
                            if (err.message) return err.message;
                            return 'Validation error';
                        })
                        .filter(msg => msg && msg.trim() !== '');

                    errorMessage = messages.length > 0 ? messages.join(', ') : 'Validation failed';
                } else if (typeof error.response.data.detail === 'string') {
                    errorMessage = error.response.data.detail;
                }
            } else if (error.response?.data?.message) {
                errorMessage = error.response.data.message;
            } else if (error.message) {
                errorMessage = error.message;
            }

            toast.error(errorMessage);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;

        if (name === 'sale_price') {
            const integerValue = value.replace(/[^\d]/g, '');
            setFormData(prev => ({
                ...prev,
                [name]: integerValue
            }));
        } else {
            setFormData(prev => ({
                ...prev,
                [name]: value
            }));
        }
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
                        <label className="form-label">Seller User ID *</label>
                        <input
                            type="text"
                            name="user_id"
                            value={formData.user_id}
                            onChange={handleChange}
                            placeholder="Enter seller user ID"
                            className="form-input"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Buyer User ID *</label>
                        <input
                            type="text"
                            name="buyer_id"
                            value={formData.buyer_id}
                            onChange={handleChange}
                            placeholder="Enter buyer user ID"
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
                            placeholder="355"
                            step="1"
                            min="0"
                            className="form-input"
                            required
                        />
                        <small className="form-help">Enter as whole number (e.g., 355)</small>
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
