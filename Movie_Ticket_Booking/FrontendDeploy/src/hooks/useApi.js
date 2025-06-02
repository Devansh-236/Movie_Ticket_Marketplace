import { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';

export const useApi = (apiFunction, dependencies = []) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const memoizedApiFunction = useCallback(apiFunction, dependencies);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await memoizedApiFunction();
                setData(response.data);
            } catch (err) {
                console.error('API Error:', err);

                // Set error as string, never as object
                let errorMessage = 'An error occurred';

                if (err.response?.data?.detail) {
                    if (Array.isArray(err.response.data.detail)) {
                        errorMessage = err.response.data.detail
                            .map(e => e.msg || e.message || 'Validation error')
                            .join(', ');
                    } else if (typeof err.response.data.detail === 'string') {
                        errorMessage = err.response.data.detail;
                    } else {
                        errorMessage = 'Validation error occurred';
                    }
                } else if (err.response?.data?.message) {
                    errorMessage = err.response.data.message;
                } else if (err.message) {
                    errorMessage = err.message;
                }

                // Always set error as string, never object
                setError(new Error(errorMessage));
                toast.error(errorMessage);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [memoizedApiFunction]);

    const refetch = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await memoizedApiFunction();
            setData(response.data);
        } catch (err) {
            console.error('API Refetch Error:', err);

            let errorMessage = 'An error occurred';

            if (err.response?.data?.detail) {
                if (Array.isArray(err.response.data.detail)) {
                    errorMessage = err.response.data.detail
                        .map(e => e.msg || e.message || 'Validation error')
                        .join(', ');
                } else if (typeof err.response.data.detail === 'string') {
                    errorMessage = err.response.data.detail;
                } else {
                    errorMessage = 'Validation error occurred';
                }
            } else if (err.response?.data?.message) {
                errorMessage = err.response.data.message;
            } else if (err.message) {
                errorMessage = err.message;
            }

            setError(new Error(errorMessage));
            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    }, [memoizedApiFunction]);

    return { data, loading, error, refetch };
};
