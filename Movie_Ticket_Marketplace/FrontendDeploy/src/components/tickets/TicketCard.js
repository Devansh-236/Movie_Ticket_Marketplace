import React, { useState } from 'react';
import { FiEdit2, FiTrash2, FiDollarSign, FiMapPin, FiFilm } from 'react-icons/fi';
import { ticketAPI } from '../../services/api';
import toast from 'react-hot-toast';
import UpdateTicket from './UpdateTicket';

const TicketCard = ({ ticket, onUpdate }) => {
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this ticket?')) return;
    
    setIsDeleting(true);
    try {
      await ticketAPI.deleteTicket(ticket['Theatre-Seat']);
      toast.success('Ticket deleted successfully');
      onUpdate();
    } catch (error) {
      toast.error('Failed to delete ticket');
    } finally {
      setIsDeleting(false);
    }
  };

  const isAvailable = ticket.status !== 'sold';
  const price = ticket.Price || 0;

  return (
    <>
      <div className={`ticket-card ${!isAvailable ? 'sold' : ''}`}>
        <div className="ticket-header">
          <div className="ticket-status">
            <span className={`status-badge ${isAvailable ? 'available' : 'sold'}`}>
              {isAvailable ? 'Available' : 'Sold'}
            </span>
          </div>
          
          <div className="ticket-actions">
            <button 
              className="action-btn edit"
              onClick={() => setShowUpdateModal(true)}
              title="Edit ticket"
            >
              <FiEdit2 size={16} />
            </button>
            
            <button 
              className="action-btn delete"
              onClick={handleDelete}
              disabled={isDeleting}
              title="Delete ticket"
            >
              <FiTrash2 size={16} />
            </button>
          </div>
        </div>

        <div className="ticket-content">
          <div className="ticket-info">
            <div className="info-item">
              <FiFilm className="info-icon" />
              <span className="info-label">Movie:</span>
              <span className="info-value">{ticket.Movie}</span>
            </div>
            
            <div className="info-item">
              <FiMapPin className="info-icon" />
              <span className="info-label">Seat:</span>
              <span className="info-value">{ticket['Theatre-Seat']}</span>
            </div>
            
            <div className="info-item">
              <FiDollarSign className="info-icon" />
              <span className="info-label">Price:</span>
              <span className="info-value">${price.toFixed(2)}</span>
            </div>
          </div>

          {ticket.owner && (
            <div className="ticket-owner">
              <span className="owner-label">Owner:</span>
              <span className="owner-value">{ticket.owner}</span>
            </div>
          )}

          {ticket.DiscountPercentage > 0 && (
            <div className="discount-badge">
              {ticket.DiscountPercentage}% OFF
            </div>
          )}
        </div>
      </div>

      {showUpdateModal && (
        <UpdateTicket
          ticket={ticket}
          onClose={() => setShowUpdateModal(false)}
          onUpdate={onUpdate}
        />
      )}
    </>
  );
};

export default TicketCard;
