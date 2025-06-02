import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-api-gateway-url.amazonaws.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', {
      method: config.method,
      url: config.url,
      data: config.data
    });
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Error:', error.response?.data);
    return Promise.reject(error);
  }
);

// Ticket API calls - FIXED with correct snake_case field names
export const ticketAPI = {
  getAllTickets: () => api.get('/tickets'),
  getTicket: (theatreSeat) => api.get(`/ticket?Theatre-Seat=${theatreSeat}`),
  createTicket: (ticketData) => {
    const payload = {
      theatre_seat: ticketData.theatreSeat?.trim() || '',  // Changed to snake_case
      movie: ticketData.movie?.trim() || '',               // This was already correct
      price: ticketData.price ? parseInt(ticketData.price, 10) : 0
    };
    
    console.log('Creating ticket with correct payload:', payload);
    return api.post('/ticket', payload);
  },
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
  purchaseTicket: (purchaseData) => api.post('/purchase-ticket', {
    ...purchaseData,
    purchase_price: parseInt(purchaseData.purchase_price, 10)
  }),
  sellTicket: (saleData) => api.post('/sell-ticket', {
    ...saleData,
    sale_price: parseInt(saleData.sale_price, 10)
  }),
  getUserTransactions: (userId, limit = 50) => 
    api.get(`/user-transactions/${userId}?limit=${limit}`),
  getTransactionDetails: (transactionId) => 
    api.get(`/transaction/${transactionId}`)
};

export default api;
