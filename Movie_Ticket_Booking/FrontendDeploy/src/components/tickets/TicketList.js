import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FiPlus, FiSearch, FiFilter } from 'react-icons/fi';
import { useApi } from '../../hooks/useApi';
import { ticketAPI } from '../../services/api';
import TicketCard from './TicketCard';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

const TicketList = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');

    const { data: ticketsData, loading, error, refetch } = useApi(ticketAPI.getAllTickets);

    const tickets = ticketsData?.tickets || [];

    const filteredTickets = tickets.filter(ticket => {
        const matchesSearch = ticket.Movie?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            ticket['Theatre-Seat']?.toLowerCase().includes(searchTerm.toLowerCase());

        const matchesFilter = filterStatus === 'all' ||
            (filterStatus === 'available' && ticket.status !== 'sold') ||
            (filterStatus === 'sold' && ticket.status === 'sold');

        return matchesSearch && matchesFilter;
    });

    if (loading) return <LoadingSpinner text="Loading tickets..." />;
    if (error) return <ErrorMessage message={error.message} onRetry={refetch} />;

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="page-title-section">
                    <h1 className="page-title">Tickets</h1>
                    <p className="page-subtitle">Manage movie tickets and bookings</p>
                </div>

                <Link to="/tickets/create" className="btn btn-primary">
                    <FiPlus size={16} />
                    Create Ticket
                </Link>
            </div>

            <div className="filters-section">
                <div className="search-box">
                    <FiSearch size={20} />
                    <input
                        type="text"
                        placeholder="Search tickets by movie or seat..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <div className="filter-dropdown">
                    <FiFilter size={16} />
                    <select
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                    >
                        <option value="all">All Tickets</option>
                        <option value="available">Available</option>
                        <option value="sold">Sold</option>
                    </select>
                </div>
            </div>

            <div className="tickets-grid">
                {filteredTickets.length > 0 ? (
                    filteredTickets.map((ticket) => (
                        <TicketCard
                            key={ticket['Theatre-Seat']}
                            ticket={ticket}
                            onUpdate={refetch}
                        />
                    ))
                ) : (
                    <div className="empty-state">
                        <p>No tickets found</p>
                        <Link to="/tickets/create" className="btn btn-secondary">
                            Create your first ticket
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TicketList;
