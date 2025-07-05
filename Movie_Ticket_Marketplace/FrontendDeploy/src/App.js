import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Header from './components/common/Header';
import Sidebar from './components/common/Sidebar';
import TicketList from './components/tickets/TicketList';
import CreateTicket from './components/tickets/CreateTicket';
import UserProfile from './components/users/UserProfile';
import CreateUser from './components/users/CreateUser';
import Leaderboard from './components/users/Leaderboard';
import TransactionList from './components/transactions/TransactionList';
import MovieList from './components/movies/MovieList';
import { useTheme } from './context/ThemeContext';
import './App.css';

function App() {
  const { isDarkMode } = useTheme();

  return (
    <div className={`app ${isDarkMode ? 'dark' : 'light'}`}>
      <Router>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: isDarkMode ? '#1e1e2e' : '#ffffff',
              color: isDarkMode ? '#cdd6f4' : '#11111b',
              border: `1px solid ${isDarkMode ? '#313244' : '#e6e6e6'}`,
            },
          }}
        />
        <Header />
        <div className="app-container">
          <Sidebar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<TicketList />} />
              <Route path="/tickets" element={<TicketList />} />
              <Route path="/tickets/create" element={<CreateTicket />} />
              <Route path="/movies" element={<MovieList />} />
              <Route path="/users" element={<UserProfile />} />
              <Route path="/users/create" element={<CreateUser />} />
              <Route path="/users/leaderboard" element={<Leaderboard />} />
              <Route path="/transactions" element={<TransactionList />} />
            </Routes>
          </main>
        </div>
      </Router>
    </div>
  );
}

export default App;
