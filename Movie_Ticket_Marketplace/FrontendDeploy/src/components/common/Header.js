import React from 'react';
import { FiMoon, FiSun, FiUser, FiBell } from 'react-icons/fi';
import { useTheme } from '../../context/ThemeContext';

const Header = () => {
  const { isDarkMode, toggleDarkMode } = useTheme();

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="header-title">Movie Booking System</h1>
          <span className="header-subtitle">Transaction Tracking & Payroll</span>
        </div>
        
        <div className="header-right">
          <button className="header-btn" onClick={toggleDarkMode}>
            {isDarkMode ? <FiSun size={20} /> : <FiMoon size={20} />}
          </button>
          
          <button className="header-btn">
            <FiBell size={20} />
          </button>
          
          <div className="user-avatar">
            <FiUser size={20} />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
