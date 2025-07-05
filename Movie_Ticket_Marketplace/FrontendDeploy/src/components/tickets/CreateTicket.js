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

        // Enhanced validation
        if (!formData.theatreSeat?.trim()) {
            toast.error('Theatre Seat is required');
            return;
        }

        if (!formData.movie?.trim()) {
            toast.error('Movie name is required');
            return;
        }

        console.log('Form data before submission:', formData);

        setIsSubmitting(true);
        try {
            const requestData = {
                theatreSeat: formData.theatreSeat.trim(),
                movie: formData.movie.trim(),
                price: formData.price ? parseInt(formData.price, 10) : 0
            };

            console.log('Sending request data:', requestData);

            const response = await ticketAPI.createTicket(requestData);
            console.log('Create ticket response:', response);

            toast.success('Ticket created successfully');
            navigate('/tickets');
        } catch (error) {
            console.error('Create ticket error:', error);
            console.error('Error response:', error.response?.data);

            let errorMessage = 'Failed to create ticket';

            if (error.response?.data?.detail) {
                if (Array.isArray(error.response.data.detail)) {
                    const messages = error.response.data.detail
                        .map(err => {
                            if (typeof err === 'string') return err;
                            if (err.msg) return `${err.loc?.join('.')} - ${err.msg}`;
                            if (err.message) return err.message;
                            return 'Validation error';
                        })
                        .filter(msg => msg);

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

        if (name === 'price') {
            // Only allow digits
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

    // Test API function for debugging
    const testAPI = async () => {
        try {
            console.log('Testing API connection...');
            const response = await fetch(`${process.env.REACT_APP_API_URL}/tickets`);
            console.log('Test response status:', response.status);
            const data = await response.json();
            console.log('Test response data:', data);
            toast.success('API connection test successful');
        } catch (error) {
            console.error('API test failed:', error);
            toast.error('API connection test failed');
        }
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
                {/* Debug section - remove after fixing */}
                <div style={{ marginBottom: '1rem', padding: '1rem', background: '#f0f0f0', borderRadius: '4px' }}>
                    <p><strong>Debug Info:</strong></p>
                    <p>API URL: {process.env.REACT_APP_API_URL}</p>
                    <button type="button" onClick={testAPI} className="btn btn-secondary" style={{ marginBottom: '0.5rem' }}>
                        Test API Connection
                    </button>
                    <p>Form Data: {JSON.stringify(formData)}</p>
                </div>

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
                            Price (Whole numbers only)
                        </label>
                        <input
                            type="number"
                            id="price"
                            name="price"
                            value={formData.price}
                            onChange={handleChange}
                            placeholder="355"
                            step="1"
                            min="0"
                            className="form-input"
                        />
                        <small className="form-help">Enter price as whole numbers (e.g., 355, 207)</small>
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
