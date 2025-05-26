import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
import json
from datetime import datetime

class TestTicketRoutes:
    """Test cases for ticket-related routes."""
    
    @patch('handlers.tickets.get_table')
    def test_get_ticket_success(self, mock_get_table, client):
        """Test successful ticket retrieval."""
        mock_table = MagicMock()
        mock_table.get_item.return_value = {
            'Item': {
                'Theatre-Seat': '1-A9',
                'Movie': 'Avengers',
                'Price': Decimal('15.99')
            }
        }
        mock_get_table.return_value = mock_table
        
        response = client.get("/api/ticket?Theatre-Seat=1-A9")
        assert response.status_code == 200
        
        data = response.json()
        assert data['Theatre-Seat'] == '1-A9'
        assert data['Movie'] == 'Avengers'
        assert float(data['Price']) == 15.99
    
    @patch('handlers.tickets.get_table')
    def test_get_ticket_not_found(self, mock_get_table, client):
        """Test ticket retrieval when ticket doesn't exist."""
        mock_table = MagicMock()
        mock_table.get_item.return_value = {}
        mock_get_table.return_value = mock_table
        
        response = client.get("/api/ticket?Theatre-Seat=nonexistent")
        assert response.status_code == 404
        assert "Ticket not found" in response.json()["detail"]
    
    @patch('handlers.tickets.get_table')
    def test_get_ticket_dynamodb_error(self, mock_get_table, client):
        """Test ticket retrieval with DynamoDB error."""
        mock_table = MagicMock()
        mock_table.get_item.side_effect = Exception("DynamoDB error")
        mock_get_table.return_value = mock_table
        
        response = client.get("/api/ticket?Theatre-Seat=1-A9")
        assert response.status_code == 500
        assert "Failed to retrieve ticket" in response.json()["detail"]
    
    @patch('handlers.tickets.get_table')
    def test_get_all_tickets_success(self, mock_get_table, client):
        """Test successful retrieval of all tickets."""
        mock_table = MagicMock()
        mock_table.scan.return_value = {
            'Items': [
                {'Theatre-Seat': '1-A9', 'Movie': 'Avengers', 'Price': Decimal('15.99')},
                {'Theatre-Seat': '1-B5', 'Movie': 'Spider-Man', 'Price': Decimal('12.50')}
            ]
        }
        mock_get_table.return_value = mock_table
        
        response = client.get("/api/tickets")
        assert response.status_code == 200
        
        data = response.json()
        assert "tickets" in data
        assert len(data["tickets"]) == 2
    
    @patch('handlers.tickets.get_table')
    def test_get_all_tickets_with_pagination(self, mock_get_table, client):
        """Test ticket retrieval with pagination."""
        mock_table = MagicMock()
        mock_table.scan.side_effect = [
            {
                'Items': [{'Theatre-Seat': '1-A9', 'Movie': 'Avengers'}],
                'LastEvaluatedKey': {'Theatre-Seat': '1-A9'}
            },
            {
                'Items': [{'Theatre-Seat': '1-B5', 'Movie': 'Spider-Man'}]
            }
        ]
        mock_get_table.return_value = mock_table
        
        response = client.get("/api/tickets")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["tickets"]) == 2
        assert mock_table.scan.call_count == 2
    
    @patch('handlers.tickets.get_table')
    def test_create_ticket_success(self, mock_get_table, client):
        """Test successful ticket creation."""
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        
        ticket_data = {
            "Theatre-Seat": "1-A9",
            "Movie": "Avengers",
            "price": 15.99
        }
        
        response = client.post("/api/ticket", json=ticket_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["message"] == "Ticket created successfully"
        assert data["Theatre-Seat"] == "1-A9"
        assert data["Movie"] == "Avengers"
        
        # Verify put_item was called
        mock_table.put_item.assert_called_once()
    
    @patch('handlers.tickets.get_table')
    def test_create_ticket_without_price(self, mock_get_table, client):
        """Test ticket creation without price."""
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        
        ticket_data = {
            "Theatre-Seat": "1-A9",
            "Movie": "Avengers"
        }
        
        response = client.post("/api/ticket", json=ticket_data)
        assert response.status_code == 201
        
        # Verify put_item was called with correct data
        call_args = mock_table.put_item.call_args
        item = call_args[1]['Item']
        assert 'Price' not in item
    
    @patch('handlers.tickets.get_table')
    def test_create_ticket_dynamodb_error(self, mock_get_table, client):
        """Test ticket creation with DynamoDB error."""
        mock_table = MagicMock()
        mock_table.put_item.side_effect = Exception("DynamoDB error")
        mock_get_table.return_value = mock_table
        
        ticket_data = {
            "Theatre-Seat": "1-A9",
            "Movie": "Avengers"
        }
        
        response = client.post("/api/ticket", json=ticket_data)
        assert response.status_code == 500
        assert "Failed to create ticket" in response.json()["detail"]
    
    @patch('handlers.tickets.sns')
    @patch('handlers.tickets.get_table')
    def test_update_ticket_success(self, mock_get_table, mock_sns, client):
        """Test successful ticket update."""
        mock_table = MagicMock()
        mock_table.get_item.return_value = {
            'Item': {'Theatre-Seat': '1-A9', 'Movie': 'Avengers', 'Price': Decimal('15.99')}
        }
        mock_table.update_item.return_value = {
            'Attributes': {'Theatre-Seat': '1-A9', 'Movie': 'Updated Movie'}
        }
        mock_get_table.return_value = mock_table
        
        update_data = {
            "Theatre-Seat": "1-A9",
            "updateKey": "Movie",
            "updateValue": "Updated Movie"
        }
        
        response = client.patch("/api/ticket", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Ticket updated successfully"
        assert data["updateKey"] == "Movie"
        assert data["updateValue"] == "Updated Movie"
    
    @patch('handlers.tickets.sns')
    @patch('handlers.tickets.get_table')
    def test_update_ticket_price_with_sns(self, mock_get_table, mock_sns, client):
        """Test ticket price update with SNS event publishing."""
        mock_table = MagicMock()
        mock_table.get_item.return_value = {
            'Item': {'Theatre-Seat': '1-A9', 'Movie': 'Avengers', 'Price': Decimal('15.99')}
        }
        mock_table.update_item.return_value = {
            'Attributes': {
                'Theatre-Seat': '1-A9', 
                'Movie': 'Avengers', 
                'Price': Decimal('12.99')
            }
        }
        mock_get_table.return_value = mock_table
        
        update_data = {
            "Theatre-Seat": "1-A9",
            "updateKey": "price",
            "updateValue": 12.99
        }
        
        response = client.patch("/api/ticket", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["priceChangeEventPublished"] is True
        
        # Verify SNS publish was called
        mock_sns.publish.assert_called_once()
    
    @patch('handlers.tickets.get_table')
    def test_update_ticket_primary_key_error(self, mock_get_table, client):
        """Test updating primary key returns error."""
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        
        update_data = {
            "Theatre-Seat": "1-A9",
            "updateKey": "Theatre-Seat",
            "updateValue": "new-seat"
        }
        
        response = client.patch("/api/ticket", json=update_data)
        assert response.status_code == 400
        assert "Cannot update primary key" in response.json()["detail"]
    
    @patch('handlers.tickets.get_table')
    def test_update_ticket_not_found(self, mock_get_table, client):
        """Test updating non-existent ticket."""
        mock_table = MagicMock()
        mock_table.get_item.return_value = {}
        mock_get_table.return_value = mock_table
        
        update_data = {
            "Theatre-Seat": "nonexistent",
            "updateKey": "Movie",
            "updateValue": "New Movie"
        }
        
        response = client.patch("/api/ticket", json=update_data)
        assert response.status_code == 404
        assert "Ticket not found" in response.json()["detail"]
    
    @patch('handlers.tickets.get_table')
    def test_delete_ticket_success(self, mock_get_table, client):
        """Test successful ticket deletion."""
        mock_table = MagicMock()
        mock_table.delete_item.return_value = {
            'Attributes': {'Theatre-Seat': '1-A9', 'Movie': 'Avengers'}
        }
        mock_get_table.return_value = mock_table
        
        delete_data = {"Theatre-Seat": "1-A9"}
        
        response = client.request("DELETE", "/api/ticket", json=delete_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Ticket deleted successfully"
        assert data["Theatre-Seat"] == "1-A9"
    
    @patch('handlers.tickets.get_table')
    def test_delete_ticket_not_found(self, mock_get_table, client):
        """Test deleting non-existent ticket."""
        mock_table = MagicMock()
        mock_table.delete_item.return_value = {}
        mock_get_table.return_value = mock_table
        
        delete_data = {"Theatre-Seat": "nonexistent"}
        
        response = client.request("DELETE", "/api/ticket", json=delete_data)
        assert response.status_code == 404
        assert "Ticket not found" in response.json()["detail"]
    
    @patch('handlers.tickets.get_table')
    def test_delete_ticket_dynamodb_error(self, mock_get_table, client):
        """Test ticket deletion with DynamoDB error."""
        mock_table = MagicMock()
        mock_table.delete_item.side_effect = Exception("DynamoDB error")
        mock_get_table.return_value = mock_table
        
        delete_data = {"Theatre-Seat": "1-A9"}
        
        response = client.request("DELETE", "/api/ticket", json=delete_data)
        assert response.status_code == 500
        assert "Failed to delete ticket" in response.json()["detail"]
