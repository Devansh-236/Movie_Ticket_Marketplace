import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiSave, FiUser, FiMail, FiDollarSign } from 'react-icons/fi';
import { userAPI } from '../../services/api';
import toast from 'react-hot-toast';

const CreateUser = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        user_id: '',
        email: '',
        name: '',
        initial_balance: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.user_id || !formData.email || !formData.name) {
            toast.error('Please fill in all required fields');
            return;
        }

        setIsSubmitting(true);
        try {
            await userAPI.createUser({
                user_id: formData.user_id,
                email: formData.email,
                name: formData.name,
                initial_balance: formData.initial_balance ? parseFloat(formData.initial_balance) : 0.0
            });

            toast.success('User created successfully');
            navigate('/users');
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Failed to create user');
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
                    onClick={() => navigate('/users')}
                >
                    <FiArrowLeft size={16} />
                    Back to Users
                </button>

                <div className="page-title-section">
                    <h1 className="page-title">Create New User</h1>
                    <p className="page-subtitle">Add a new user with payroll tracking</p>
                </div>
            </div>

            <div className="form-container">
                <form onSubmit={handleSubmit} className="form">
                    <div className="form-group">
                        <label htmlFor="user_id" className="form-label">
                            <FiUser size={16} />
                            User ID *
                        </label>
                        <input
                            type="text"
                            id="user_id"
                            name="user_id"
                            value={formData.user_id}
                            onChange={handleChange}
                            placeholder="Enter unique user ID"
                            className="form-input"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email" className="form-label">
                            <FiMail size={16} />
                            Email *
                        </label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="user@example.com"
                            className="form-input"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="name" className="form-label">
                            <FiUser size={16} />
                            Full Name *
                        </label>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            placeholder="Enter full name"
                            className="form-input"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="initial_balance" className="form-label">
                            <FiDollarSign size={16} />
                            Initial Balance (Optional)
                        </label>
                        <input
                            type="number"
                            id="initial_balance"
                            name="initial_balance"
                            value={formData.initial_balance}
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
                            onClick={() => navigate('/users')}
                        >
                            Cancel
                        </button>

                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={isSubmitting}
                        >
                            <FiSave size={16} />
                            {isSubmitting ? 'Creating...' : 'Create User'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateUser;
