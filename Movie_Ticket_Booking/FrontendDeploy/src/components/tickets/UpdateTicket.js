import React, { useState } from 'react';
import { FiX, FiSave } from 'react-icons/fi';
import { ticketAPI } from '../../services/api';
import toast from 'react-hot-toast';

const UpdateTicket = ({ ticket, onClose, onUpdate }) => {
    const [updateKey, setUpdateKey] = useState('Price');
    const [updateValue, setUpdateValue] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const updateOptions = [
        { value: 'Price', label: 'Price' },
        { value: 'Movie', label: 'Movie' },
        { value: 'status', label: 'Status' }
    ];

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!updateValue.trim()) {
            toast.error('Please enter a value');
            return;
        }

        setIsSubmitting(true);
        try {
            let processedValue = updateValue;

            // Convert to number for price
            if (updateKey === 'Price') {
                processedValue = parseFloat(updateValue);
                if (isNaN(processedValue)) {
                    toast.error('Price must be a valid number');
                    return;
                }
            }

            await ticketAPI.updateTicket({
                theatreSeat: ticket['Theatre-Seat'],
                updateKey,
                updateValue: processedValue
            });

            toast.success('Ticket updated successfully');
            onUpdate();
            onClose();
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Failed to update ticket');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Update Ticket</h2>
                    <button className="modal-close" onClick={onClose}>
                        <FiX size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="modal-form">
                    <div className="form-group">
                        <label className="form-label">Ticket Seat</label>
                        <input
                            type="text"
                            value={ticket['Theatre-Seat']}
                            disabled
                            className="form-input disabled"
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Update Field</label>
                        <select
                            value={updateKey}
                            onChange={(e) => setUpdateKey(e.target.value)}
                            className="form-input"
                        >
                            {updateOptions.map(option => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label className="form-label">New Value</label>
                        <input
                            type={updateKey === 'Price' ? 'number' : 'text'}
                            value={updateValue}
                            onChange={(e) => setUpdateValue(e.target.value)}
                            placeholder={`Enter new ${updateKey.toLowerCase()}`}
                            step={updateKey === 'Price' ? '0.01' : undefined}
                            min={updateKey === 'Price' ? '0' : undefined}
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
                            <FiSave size={16} />
                            {isSubmitting ? 'Updating...' : 'Update'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default UpdateTicket;
