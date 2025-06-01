import React from 'react';
import { FiFilm, FiClock, FiStar } from 'react-icons/fi';
import { useApi } from '../../hooks/useApi';
import { movieAPI } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

const MovieList = () => {
    const { data: moviesData, loading, error, refetch } = useApi(movieAPI.getAllMovies);

    const movies = moviesData?.movies || [];

    if (loading) return <LoadingSpinner text="Loading movies..." />;
    if (error) return <ErrorMessage message={error.message} onRetry={refetch} />;

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
                    {movies.map((movie, index) => (
                        <div key={index} className="movie-card">
                            <div className="movie-header">
                                <FiFilm size={24} className="movie-icon" />
                                <h3 className="movie-title">{movie.title || movie.name || 'Unknown Movie'}</h3>
                            </div>

                            <div className="movie-details">
                                {movie.genre && (
                                    <div className="movie-detail">
                                        <span className="detail-label">Genre:</span>
                                        <span className="detail-value">{movie.genre}</span>
                                    </div>
                                )}

                                {movie.duration && (
                                    <div className="movie-detail">
                                        <FiClock size={16} />
                                        <span className="detail-value">{movie.duration} min</span>
                                    </div>
                                )}

                                {movie.rating && (
                                    <div className="movie-detail">
                                        <FiStar size={16} />
                                        <span className="detail-value">{movie.rating}/10</span>
                                    </div>
                                )}

                                {movie.available_seats && (
                                    <div className="movie-detail">
                                        <span className="detail-label">Available Seats:</span>
                                        <span className="detail-value">{movie.available_seats}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
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
