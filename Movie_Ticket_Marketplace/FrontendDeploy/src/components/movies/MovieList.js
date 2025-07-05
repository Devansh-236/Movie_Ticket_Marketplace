import React from 'react';
import { FiFilm } from 'react-icons/fi';
import { useApi } from '../../hooks/useApi';
import { movieAPI } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

const MovieList = () => {
    const { data: moviesData, loading, error, refetch } = useApi(movieAPI.getAllMovies, []);

    // Handle if movies is an array of strings or objects
    const movies = moviesData?.movies || moviesData || [];

    if (loading) return <LoadingSpinner text="Loading movies..." />;
    if (error) return <ErrorMessage error={error} onRetry={refetch} />;

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="page-title-section">
                    <h1 className="page-title">Movies</h1>
                    <p className="page-subtitle">Available movies in the system</p>
                </div>
            </div>

            {movies.length > 0 ? (
                <div className="movies-grid">
                    {movies.map((movie, index) => {
                        // Handle both string and object formats
                        const movieTitle = typeof movie === 'string' ? movie :
                            movie.Movie || movie.title || movie.name || `Movie ${index + 1}`;

                        return (
                            <div key={movieTitle || index} className="movie-card">
                                <div className="movie-header">
                                    <FiFilm size={24} className="movie-icon" />
                                    <h3 className="movie-title">{movieTitle}</h3>
                                </div>

                                <div className="movie-details">
                                    {typeof movie === 'object' && (
                                        <>
                                            {movie.Genre && (
                                                <div className="movie-detail">
                                                    <span className="detail-label">Genre:</span>
                                                    <span className="detail-value">{movie.Genre}</span>
                                                </div>
                                            )}

                                            {movie.ticket_count && (
                                                <div className="movie-detail">
                                                    <span className="detail-label">Total Tickets:</span>
                                                    <span className="detail-value">{movie.ticket_count}</span>
                                                </div>
                                            )}
                                        </>
                                    )}

                                    {typeof movie === 'string' && (
                                        <div className="movie-detail">
                                            <span className="detail-label">Type:</span>
                                            <span className="detail-value">Available Movie</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div className="empty-state">
                    <FiFilm size={48} />
                    <h3>No movies available</h3>
                    <p>No movies found in the system</p>
                </div>
            )}
        </div>
    );
};

export default MovieList;
