export const API_ENDPOINTS = {
    TICKETS: '/tickets',
    TICKET: '/ticket',
    MOVIES: '/movies',
    USERS: '/users',
    PURCHASE_TICKET: '/purchase-ticket',
    SELL_TICKET: '/sell-ticket',
    USER_TRANSACTIONS: '/user-transactions',
    TRANSACTION: '/transaction'
};

export const TRANSACTION_TYPES = {
    PURCHASE: 'PURCHASE',
    SALE: 'SALE'
};

export const PAYMENT_METHODS = [
    { value: 'credit_card', label: 'Credit Card' },
    { value: 'debit_card', label: 'Debit Card' },
    { value: 'cash', label: 'Cash' },
    { value: 'digital_wallet', label: 'Digital Wallet' }
];

export const TICKET_STATUS = {
    AVAILABLE: 'available',
    SOLD: 'sold'
};
