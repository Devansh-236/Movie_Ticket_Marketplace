import pytest
from unittest.mock import patch, MagicMock
import boto3
import os
from decimal import Decimal
import json

class TestUtilities:
    """Test cases for utility functions."""
    
    @patch('utils.database.boto3.resource')
    def test_get_table_default_name(self, mock_boto3_resource):
        """Test get_table with default table name."""
        from utils.database import get_table
        
        mock_dynamodb = MagicMock()
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Remove environment variable if it exists
        if 'DYNAMODB_TABLE' in os.environ:
            del os.environ['DYNAMODB_TABLE']
        
        result = get_table()
        
        mock_boto3_resource.assert_called_once_with('dynamodb')
        mock_dynamodb.Table.assert_called_once_with('ticket-booking')
        assert result == mock_table
    
    @patch('utils.database.boto3.resource')
    def test_get_table_custom_name(self, mock_boto3_resource):
        """Test get_table with custom table name from environment."""
        from utils.database import get_table
        
        mock_dynamodb = MagicMock()
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Set custom table name
        os.environ['DYNAMODB_TABLE'] = 'custom-table-name'
        
        result = get_table()
        
        mock_boto3_resource.assert_called_once_with('dynamodb')
        mock_dynamodb.Table.assert_called_once_with('custom-table-name')
        assert result == mock_table
        
        # Clean up
        del os.environ['DYNAMODB_TABLE']
    
    def test_custom_encoder_decimal(self):
        """Test CustomEncoder with Decimal values."""
        from utils.encoder import CustomEncoder
        
        data = {
            'price': Decimal('15.99'),
            'discount': Decimal('0.15'),
            'name': 'Test Movie'
        }
        
        result = json.dumps(data, cls=CustomEncoder)
        parsed = json.loads(result)
        
        assert parsed['price'] == 15.99
        assert parsed['discount'] == 0.15
        assert parsed['name'] == 'Test Movie'
    
    def test_custom_encoder_regular_types(self):
        """Test CustomEncoder with regular Python types."""
        from utils.encoder import CustomEncoder
        
        data = {
            'string': 'test',
            'integer': 42,
            'float': 3.14,
            'boolean': True,
            'list': [1, 2, 3],
            'dict': {'nested': 'value'}
        }
        
        result = json.dumps(data, cls=CustomEncoder)
        parsed = json.loads(result)
        
        assert parsed == data
    
    def test_custom_encoder_mixed_types(self):
        """Test CustomEncoder with mixed types including Decimal."""
        from utils.encoder import CustomEncoder
        
        data = {
            'ticket': {
                'seat': '1-A9',
                'price': Decimal('15.99'),
                'available': True,
                'metadata': {
                    'discount_rate': Decimal('0.1'),
                    'created_at': '2023-01-01'
                }
            },
            'prices': [Decimal('10.50'), Decimal('12.75'), Decimal('15.99')]
        }
        
        result = json.dumps(data, cls=CustomEncoder)
        parsed = json.loads(result)
        
        assert parsed['ticket']['price'] == 15.99
        assert parsed['ticket']['metadata']['discount_rate'] == 0.1
        assert parsed['prices'] == [10.50, 12.75, 15.99]
    
    def test_custom_encoder_zero_decimal(self):
        """Test CustomEncoder with zero Decimal value."""
        from utils.encoder import CustomEncoder
        
        data = {'zero_price': Decimal('0')}
        
        result = json.dumps(data, cls=CustomEncoder)
        parsed = json.loads(result)
        
        assert parsed['zero_price'] == 0.0
    
    def test_custom_encoder_negative_decimal(self):
        """Test CustomEncoder with negative Decimal value."""
        from utils.encoder import CustomEncoder
        
        data = {'refund': Decimal('-5.50')}
        
        result = json.dumps(data, cls=CustomEncoder)
        parsed = json.loads(result)
        
        assert parsed['refund'] == -5.50
    
    def test_custom_encoder_unsupported_type(self):
        """Test CustomEncoder with unsupported type falls back to default."""
        from utils.encoder import CustomEncoder
        
        # Create a custom object that's not JSON serializable
        class CustomObject:
            def __init__(self, value):
                self.value = value
        
        encoder = CustomEncoder()
        custom_obj = CustomObject("test")
        
        # Should raise TypeError for unsupported types
        with pytest.raises(TypeError):
            encoder.default(custom_obj)

class TestResponseUtils:
    """Test cases for response utility functions."""
    
    def test_create_response_default_headers(self):
        """Test create_response with default headers."""
        from utils.response import create_response
        
        body = {"message": "success"}
        response = create_response(200, body)
        
        assert response['statusCode'] == 200
        assert response['headers']['Content-Type'] == 'application/json'
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
        
        # Parse body to verify JSON encoding
        parsed_body = json.loads(response['body'])
        assert parsed_body == body
    
    def test_create_response_custom_headers(self):
        """Test create_response with custom headers."""
        from utils.response import create_response
        
        body = {"message": "success"}
        custom_headers = {"X-Custom-Header": "custom-value"}
        response = create_response(200, body, custom_headers)
        
        assert response['statusCode'] == 200
        assert response['headers']['X-Custom-Header'] == 'custom-value'
        assert response['headers']['Content-Type'] == 'application/json'  # Should still have defaults
    
    def test_success_response(self):
        """Test success_response helper."""
        from utils.response import success_response
        
        data = {"ticket": "created"}
        response = success_response(data)
        
        assert response['statusCode'] == 200
        parsed_body = json.loads(response['body'])
        assert parsed_body == data
    
    def test_success_response_custom_status(self):
        """Test success_response with custom status code."""
        from utils.response import success_response
        
        data = {"ticket": "created"}
        response = success_response(data, 201)
        
        assert response['statusCode'] == 201
        parsed_body = json.loads(response['body'])
        assert parsed_body == data
    
    def test_error_response(self):
        """Test error_response helper."""
        from utils.response import error_response
        
        message = "Ticket not found"
        response = error_response(message, 404)
        
        assert response['statusCode'] == 404
        parsed_body = json.loads(response['body'])
        assert parsed_body == {'error': message}
    
    def test_error_response_default_status(self):
        """Test error_response with default status code."""
        from utils.response import error_response
        
        message = "Bad request"
        response = error_response(message)
        
        assert response['statusCode'] == 400
        parsed_body = json.loads(response['body'])
        assert parsed_body == {'error': message}
    
    def test_response_with_decimal_values(self):
        """Test response functions with Decimal values."""
        from utils.response import success_response
        
        data = {"price": Decimal('15.99'), "discount": Decimal('2.50')}
        response = success_response(data)
        
        parsed_body = json.loads(response['body'])
        assert parsed_body['price'] == 15.99
        assert parsed_body['discount'] == 2.50
