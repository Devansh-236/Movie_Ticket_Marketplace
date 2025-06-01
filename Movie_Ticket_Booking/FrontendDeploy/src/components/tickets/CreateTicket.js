import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiSave } from 'react-icons/fi';
import { ticketAPI } from '../../services/api';
import toast from 'react-hot-toast';

const CreateTicket = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        theatreSeat: '',
        movie: '',
        price: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.theatreSeat || !formData.movie) {
            toast.error('Please fill in all required fields');
            return;
        }

        setIsSubmitting(true);
        try {
            await ticketAPI.createTicket({
                theatreSeat: formData.theatreSeat,
                movie: formData.movie,
                price: formData.price ? parseFloat(formData.price) : undefined
            });

            toast.success('Ticket created successfully');
            navigate('/tickets');
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Failed to create ticket');
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
        <div className="page-container">
            <div className="page-header">
                <button
                    className="btn btn-secondary"
                    onClick={() => navigate('/tickets')}
                >
                    <FiArrowLeft size={16} />
                    Back to Tickets
                </button>

                <div className="page-title-section">
                    <h1 className="page-title">Create New Ticket</h1>
                    <p className="page-subtitle">Add a new movie ticket to the system</p>
                </div>
            </div>

            <div className="form-container">
                <form onSubmit={handleSubmit} className="form">
                    <div className="form-group">
                        <label htmlFor="theatreSeat" className="form-label">
                            Theatre Seat *
                        </label>
                        <input
                            type="text"
                            id="theatreSeat"
                            name="theatreSeat"
                            value={formData.theatreSeat}
                            onChange={handleChange}
                            placeholder="e.g., A1, B5, C10"
                            className="form-input"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="movie" className="form-label">
                            Movie *
                        </label>
                        <input
                            type="text"
                            id="movie"
                            name="movie"
                            value={formData.movie}
                            onChange={handleChange}
                            placeholder="Enter movie name"
                            className="form-input"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="price" className="form-label">
                            Price (Optional)
                        </label>
                        <input
                            type="number"
                            id="price"
                            name="price"
                            value={formData.price}
                            onChange={handleChange}
                            placeholder="0.00"
                            step="0.01"
                            min="0"
                            className="form-input"
                        />
                    </div>

                    <div className="form-actions">
                        <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={() => navigate('/tickets')}
                        >
                            Cancel
                        </button>

                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={isSubmitting}
                        >
                            <FiSave size={16} />
                            {isSubmitting ? 'Creating...' : 'Create Ticket'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateTicket;
