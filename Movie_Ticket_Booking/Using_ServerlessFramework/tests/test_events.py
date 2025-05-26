import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from decimal import Decimal
import json
from datetime import datetime

class TestEventHandler:
    """Test cases for event handling functionality."""
    
    @patch('handlers.events.sns')
    @patch('handlers.events.get_table')
    @pytest.mark.asyncio
    async def test_handle_price_change_event_success(self, mock_get_table, mock_sns):
        """Test successful price change event handling."""
        from handlers.events import handle_price_change_event
        
        mock_table = MagicMock()
        mock_table.update_item.return_value = {
            'Attributes': {
                'Theatre-Seat': '1-A9',
                'Movie': 'Avengers',
                'Price': Decimal('12.99'),
                'IsDiscounted': True,
                'DiscountPercentage': Decimal('18.63')
            }
        }
        mock_get_table.return_value = mock_table
        
        event_data = {
            'eventType': 'PriceChangeInitiated',
            'theatreSeat': '1-A9',
            'movie': 'Avengers',
            'oldPrice': 15.99,
            'newPrice': 12.99
        }
        
        result = await handle_price_change_event(event_data)
        
        assert result["message"] == "Price change event processed successfully"
        
        # Verify table update was called
        mock_table.update_item.assert_called_once()
        
        # Verify SNS publish was called
        mock_sns.publish.assert_called_once()
    
    @patch('handlers.events.sns')
    @patch('handlers.events.get_table')
    @pytest.mark.asyncio
    async def test_handle_price_increase_event(self, mock_get_table, mock_sns):
        """Test price change event with price increase (no discount)."""
        from handlers.events import handle_price_change_event
        
        mock_table = MagicMock()
        mock_table.update_item.return_value = {
            'Attributes': {
                'Theatre-Seat': '1-A9',
                'Movie': 'Avengers',
                'Price': Decimal('18.99'),
                'IsDiscounted': False,
                'DiscountPercentage': Decimal('0')
            }
        }
        mock_get_table.return_value = mock_table
        
        event_data = {
            'eventType': 'PriceChangeInitiated',
            'theatreSeat': '1-A9',
            'movie': 'Avengers',
            'oldPrice': 15.99,
            'newPrice': 18.99
        }
        
        result = await handle_price_change_event(event_data)
        
        assert result["message"] == "Price change event processed successfully"
        
        # Verify update was called with no discount
        call_args = mock_table.update_item.call_args
        update_values = call_args[1]['ExpressionAttributeValues']
        assert update_values[':IsDiscounted'] is False
        assert update_values[':DiscountPercentage'] == Decimal('0')
    
    @patch('handlers.events.sns')
    @patch('handlers.events.get_table')
    @pytest.mark.asyncio
    async def test_handle_non_price_change_event(self, mock_get_table, mock_sns):
        """Test handling of non-price change events."""
        from handlers.events import handle_price_change_event
        
        mock_table = MagicMock()
        mock_get_table.return_value = mock_table
        
        event_data = {
            'eventType': 'SomeOtherEvent',
            'theatreSeat': '1-A9',
            'movie': 'Avengers'
        }
        
        result = await handle_price_change_event(event_data)
        
        assert result["message"] == "Price change event processed successfully"
        
        # Verify no table updates were made
        mock_table.update_item.assert_not_called()
        mock_sns.publish.assert_not_called()
    
    @patch('handlers.events.sns')
    @patch('handlers.events.get_table')
    @pytest.mark.asyncio
    async def test_handle_price_change_event_with_none_old_price(self, mock_get_table, mock_sns):
        """Test price change event with None old price."""
        from handlers.events import handle_price_change_event
        
        mock_table = MagicMock()
        mock_table.update_item.return_value = {
            'Attributes': {
                'Theatre-Seat': '1-A9',
                'Movie': 'Avengers',
                'Price': Decimal('12.99'),
                'IsDiscounted': False,
                'DiscountPercentage': Decimal('0')
            }
        }
        mock_get_table.return_value = mock_table
        
        event_data = {
            'eventType': 'PriceChangeInitiated',
            'theatreSeat': '1-A9',
            'movie': 'Avengers',
            'oldPrice': None,
            'newPrice': 12.99
        }
        
        result = await handle_price_change_event(event_data)
        
        assert result["message"] == "Price change event processed successfully"
        
        # Verify update was called with no discount
        call_args = mock_table.update_item.call_args
        update_values = call_args[1]['ExpressionAttributeValues']
        assert update_values[':IsDiscounted'] is False
        assert update_values[':PreviousPrice'] is None
    
    @patch('handlers.events.sns')
    @patch('handlers.events.get_table')
    @pytest.mark.asyncio
    async def test_handle_price_change_event_sns_error(self, mock_get_table, mock_sns):
        """Test price change event with SNS publishing error."""
        from handlers.events import handle_price_change_event
        
        mock_table = MagicMock()
        mock_table.update_item.return_value = {
            'Attributes': {
                'Theatre-Seat': '1-A9',
                'Movie': 'Avengers',
                'Price': Decimal('12.99')
            }
        }
        mock_get_table.return_value = mock_table
        
        # Mock SNS publish to raise an error
        mock_sns.publish.side_effect = Exception("SNS error")
        
        event_data = {
            'eventType': 'PriceChangeInitiated',
            'theatreSeat': '1-A9',
            'movie': 'Avengers',
            'oldPrice': 15.99,
            'newPrice': 12.99
        }
        
        # Should still succeed even if SNS fails
        result = await handle_price_change_event(event_data)
        
        assert result["message"] == "Price change event processed successfully"
        
        # Verify table update was still called
        mock_table.update_item.assert_called_once()
    
    @patch('handlers.events.get_table')
    @pytest.mark.asyncio
    async def test_handle_price_change_event_dynamodb_error(self, mock_get_table):
        """Test price change event with DynamoDB error."""
        from handlers.events import handle_price_change_event
        from fastapi import HTTPException
        
        mock_table = MagicMock()
        mock_table.update_item.side_effect = Exception("DynamoDB error")
        mock_get_table.return_value = mock_table
        
        event_data = {
            'eventType': 'PriceChangeInitiated',
            'theatreSeat': '1-A9',
            'movie': 'Avengers',
            'oldPrice': 15.99,
            'newPrice': 12.99
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await handle_price_change_event(event_data)
        
        assert exc_info.value.status_code == 500
        assert "Failed to process price change event" in str(exc_info.value.detail)
    
    @patch('handlers.events.topic_arn', None)
    @patch('handlers.events.get_table')
    @pytest.mark.asyncio
    async def test_handle_price_change_event_no_topic_arn(self, mock_get_table):
        """Test price change event when topic ARN is not set."""
        from handlers.events import handle_price_change_event
        
        mock_table = MagicMock()
        mock_table.update_item.return_value = {
            'Attributes': {
                'Theatre-Seat': '1-A9',
                'Movie': 'Avengers',
                'Price': Decimal('12.99')
            }
        }
        mock_get_table.return_value = mock_table
        
        event_data = {
            'eventType': 'PriceChangeInitiated',
            'theatreSeat': '1-A9',
            'movie': 'Avengers',
            'oldPrice': 15.99,
            'newPrice': 12.99
        }
        
        result = await handle_price_change_event(event_data)
        
        assert result["message"] == "Price change event processed successfully"
        
        # Verify table update was called but no SNS publish
        mock_table.update_item.assert_called_once()
