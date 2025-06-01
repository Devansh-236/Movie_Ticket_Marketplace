import React from 'react';
import { FiAlertCircle, FiRefreshCw } from 'react-icons/fi';

const ErrorMessage = ({ message, onRetry }) => {
    return (
        <div className="error-message">
            <FiAlertCircle size={48} className="error-icon" />
            <h3>Something went wrong</h3>
            <p>{message || 'An unexpected error occurred'}</p>
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
