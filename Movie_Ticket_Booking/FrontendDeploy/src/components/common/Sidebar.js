import React from 'react';
import { NavLink } from 'react-router-dom';
import {
    FiHome,
    FiFilm,
    FiUsers,
    FiCreditCard,
    FiPlus
} from 'react-icons/fi';
import { MdLocalMovies } from 'react-icons/md';
import { FaTrophy } from 'react-icons/fa';


const Sidebar = () => {
    const menuItems = [
        { path: '/', icon: FiHome, label: 'Dashboard' },
        { path: '/tickets', icon: MdLocalMovies, label: 'Tickets' }, // Changed icon
        { path: '/tickets/create', icon: FiPlus, label: 'Create Ticket' },
        { path: '/movies', icon: FiFilm, label: 'Movies' },
        { path: '/users', icon: FiUsers, label: 'Users' },
        { path: '/users/create', icon: FiPlus, label: 'Create User' },
        { path: '/users/leaderboard', icon: FaTrophy, label: 'Leaderboard' }, // Changed icon
        { path: '/transactions', icon: FiCreditCard, label: 'Transactions' },
    ];

    return (
        <aside className="sidebar">
            <nav className="sidebar-nav">
                {menuItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            `sidebar-link ${isActive ? 'active' : ''}`
                        }
                    >
                        <item.icon size={20} />
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </nav>
        </aside>
    );
};

export default Sidebar;
