import React from 'react';
import { FiAlertCircle, FiRefreshCw } from 'react-icons/fi';

const ErrorMessage = ({ message, error, onRetry }) => {
    // Safely extract error message
    const getErrorMessage = () => {
        if (message) return message;
        if (error?.message) return error.message;
        if (typeof error === 'string') return error;
        return 'An unexpected error occurred';
    };

    return (
        <div className="error-message">
            <FiAlertCircle size={48} className="error-icon" />
            <h3>Something went wrong</h3>
            <p>{getErrorMessage()}</p>
            {onRetry && (
                <button className="btn btn-primary" onClick={onRetry}>
                    <FiRefreshCw size={16} />
                    Try Again
                </button>
            )}
        </div>
    );
};

export default ErrorMessage;
