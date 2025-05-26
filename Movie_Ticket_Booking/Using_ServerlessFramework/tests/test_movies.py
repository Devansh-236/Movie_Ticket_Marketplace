import pytest
from unittest.mock import patch, MagicMock
from moto import mock_dynamodb
import boto3

class TestMovieRoutes:
    """Test cases for movie-related routes."""
    
    @patch('handlers.movies.get_table')
    def test_get_movies_success(self, mock_get_table, client):
        """Test successful retrieval of unique movies."""
        # Mock table response
        mock_table = MagicMock()
        mock_table.scan.return_value = {
            'Items': [
                {'Movie': 'Avengers', 'Theatre-Seat': '1-A9'},
                {'Movie': 'Spider-Man', 'Theatre-Seat': '1-B5'},
                {'Movie': 'Avengers', 'Theatre-Seat': '2-C3'},
                {'Movie': 'Batman', 'Theatre-Seat': '3-D1'}
            ]
        }
        mock_get_table.return_value = mock_table
        
        response = client.get("/api/movies")
        assert response.status_code == 200
        
        data = response.json()
        assert "movies" in data
        movies = data["movies"]
        assert len(movies) == 3  # Unique movies
        assert "Avengers" in movies
        assert "Spider-Man" in movies
        assert "Batman" in movies
    
    @patch('handlers.movies.get_table')
    def test_get_movies_with_pagination(self, mock_get_table, client):
        """Test movie retrieval with DynamoDB pagination."""
        mock_table = MagicMock()
        
        # First scan call with pagination
        mock_table.scan.side_effect = [
            {
                'Items': [
                    {'Movie': 'Avengers', 'Theatre-Seat': '1-A9'},
                    {'Movie': 'Spider-Man', 'Theatre-Seat': '1-B5'}
                ],
                'LastEvaluatedKey': {'Theatre-Seat': '1-B5'}
            },
            {
                'Items': [
                    {'Movie': 'Batman', 'Theatre-Seat': '2-C3'}
                ]
            }
        ]
        mock_get_table.return_value = mock_table
        
        response = client.get("/api/movies")
        assert response.status_code == 200
        
        data = response.json()
        movies = data["movies"]
        assert len(movies) == 3
        
        # Verify pagination was handled
        assert mock_table.scan.call_count == 2
    
    @patch('handlers.movies.get_table')
    def test_get_movies_empty_result(self, mock_get_table, client):
        """Test movie retrieval when no tickets exist."""
        mock_table = MagicMock()
        mock_table.scan.return_value = {'Items': []}
        mock_get_table.return_value = mock_table
        
        response = client.get("/api/movies")
        assert response.status_code == 200
        
        data = response.json()
        assert data["movies"] == []
    
    @patch('handlers.movies.get_table')
    def test_get_movies_dynamodb_error(self, mock_get_table, client):
        """Test movie retrieval when DynamoDB raises an error."""
        mock_table = MagicMock()
        mock_table.scan.side_effect = Exception("DynamoDB error")
        mock_get_table.return_value = mock_table
        
        response = client.get("/api/movies")
        assert response.status_code == 500
        
        data = response.json()
        assert "Failed to retrieve movies" in data["detail"]
    
    @patch('handlers.movies.get_table')
    def test_get_movies_items_without_movie_field(self, mock_get_table, client):
        """Test movie retrieval with items missing Movie field."""
        mock_table = MagicMock()
        mock_table.scan.return_value = {
            'Items': [
                {'Movie': 'Avengers', 'Theatre-Seat': '1-A9'},
                {'Theatre-Seat': '1-B5'},  # Missing Movie field
                {'Movie': 'Spider-Man', 'Theatre-Seat': '2-C3'},
                {'Movie': None, 'Theatre-Seat': '3-D1'}  # None Movie field
            ]
        }
        mock_get_table.return_value = mock_table
        
        response = client.get("/api/movies")
        assert response.status_code == 200
        
        data = response.json()
        movies = data["movies"]
        # Should only include valid movie names
        assert "Avengers" in movies
        assert "Spider-Man" in movies
        assert None not in movies
        assert len([m for m in movies if m]) == 2
