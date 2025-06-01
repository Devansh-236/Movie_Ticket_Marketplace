import axios from 'axios';

// Replace with your actual API Gateway URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-api-gateway-url.amazonaws.com/dev';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for debugging
api.interceptors.request.use(
    (config) => {
        console.log('API Request:', config);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

// Ticket API calls
export const ticketAPI = {
    getAllTickets: () => api.get('/tickets'),
    getTicket: (theatreSeat) => api.get(`/ticket?Theatre-Seat=${theatreSeat}`),
    createTicket: (ticketData) => api.post('/ticket', {
        'Theatre-Seat': ticketData.theatreSeat,
        'Movie': ticketData.movie,
        'Price': ticketData.price
    }),
    updateTicket: (ticketData) => api.patch('/ticket', {
        'Theatre-Seat': ticketData.theatreSeat,
        'updateKey': ticketData.updateKey,
        'updateValue': ticketData.updateValue
    }),
    deleteTicket: (theatreSeat) => api.delete('/ticket', {
        data: { 'Theatre-Seat': theatreSeat }
    })
};

// Movie API calls
export const movieAPI = {
    getAllMovies: () => api.get('/movies')
};

// User API calls
export const userAPI = {
    createUser: (userData) => api.post('/users', userData),
    getUserPayroll: (userId) => api.get(`/users/${userId}/payroll`),
    getUserSummary: (userId) => api.get(`/users/${userId}/summary`),
    getLeaderboard: (limit = 10, order = 'desc') =>
        api.get(`/users/leaderboard?limit=${limit}&order=${order}`)
};

// Transaction API calls
export const transactionAPI = {
    purchaseTicket: (purchaseData) => api.post('/purchase-ticket', purchaseData),
    sellTicket: (saleData) => api.post('/sell-ticket', saleData),
    getUserTransactions: (userId, limit = 50) =>
        api.get(`/user-transactions/${userId}?limit=${limit}`),
    getTransactionDetails: (transactionId) =>
        api.get(`/transaction/${transactionId}`)
};

export default api;
