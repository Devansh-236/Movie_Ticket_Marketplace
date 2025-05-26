import boto3
import os
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.environ.get('AWS_ENDPOINT_URL', 'http://localhost:4566'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'test'),
            region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        )
        self.table_name = os.environ.get('DYNAMODB_TABLE', 'ticket-booking')
        self.table = self.dynamodb.Table(self.table_name)

    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ticket booking"""
        try:
            # Convert any float values to Decimal for DynamoDB
            processed_data = self._process_item_for_dynamodb(ticket_data)
            
            self.table.put_item(Item=processed_data)
            logger.info(f"Successfully created ticket: {ticket_data.get('Theatre-Seat')}")
            
            return {
                'message': 'Ticket created successfully',
                'Theatre-Seat': ticket_data.get('Theatre-Seat'),
                'Movie': ticket_data.get('Movie')
            }
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            raise

    def get_ticket(self, theatre_seat: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific ticket by Theatre-Seat ID"""
        try:
            response = self.table.get_item(Key={'Theatre-Seat': theatre_seat})
            
            if 'Item' in response:
                return self._process_item_from_dynamodb(response['Item'])
            return None
        except Exception as e:
            logger.error(f"Error retrieving ticket: {e}")
            raise

    def get_all_tickets(self) -> List[Dict[str, Any]]:
        """Retrieve all tickets"""
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            
            return [self._process_item_from_dynamodb(item) for item in items]
        except Exception as e:
            logger.error(f"Error retrieving all tickets: {e}")
            raise

    def get_movies(self) -> List[str]:
        """Retrieve all unique movies from tickets"""
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            
            # Extract unique movie names
            unique_movies = list({item.get('Movie') for item in items if item.get('Movie')})
            return unique_movies
        except Exception as e:
            logger.error(f"Error retrieving movies: {e}")
            raise

    def update_ticket(self, theatre_seat: str, update_key: str, update_value: Any) -> Dict[str, Any]:
        """Update an existing ticket"""
        try:
            # Get current item first
            current_item_response = self.table.get_item(Key={'Theatre-Seat': theatre_seat})
            current_item = current_item_response.get('Item')
            
            if not current_item:
                raise ValueError("Ticket not found")

            # Prevent updating the primary key
            if update_key == 'Theatre-Seat':
                raise ValueError("Cannot update primary key Theatre-Seat")

            # Process update value for DynamoDB
            processed_value = self._convert_to_decimal_if_number(update_value)

            # Build update expression
            update_expression = f"SET #{update_key} = :val"
            expression_attribute_names = {f"#{update_key}": update_key}
            expression_attribute_values = {":val": processed_value}

            # If updating price, also update metadata
            if update_key.lower() == 'price':
                from datetime import datetime
                old_price = current_item.get('Price')
                timestamp = datetime.utcnow().isoformat()
                
                update_expression = "SET #Price = :newPrice, #PreviousPrice = :oldPrice, #LastPriceChangeTimestamp = :timestamp"
                expression_attribute_names = {
                    "#Price": "Price",
                    "#PreviousPrice": "PreviousPrice",
                    "#LastPriceChangeTimestamp": "LastPriceChangeTimestamp"
                }
                expression_attribute_values = {
                    ":newPrice": processed_value,
                    ":oldPrice": old_price,
                    ":timestamp": timestamp
                }

            response = self.table.update_item(
                Key={'Theatre-Seat': theatre_seat},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )

            updated_item = self._process_item_from_dynamodb(response.get('Attributes', {}))
            
            return {
                'message': 'Ticket updated successfully',
                'Theatre-Seat': theatre_seat,
                'updateKey': update_key,
                'updateValue': update_value,
                'updatedItem': updated_item,
                'current_item': current_item
            }
        except Exception as e:
            logger.error(f"Error updating ticket: {e}")
            raise

    def delete_ticket(self, theatre_seat: str) -> Dict[str, Any]:
        """Delete a ticket booking"""
        try:
            response = self.table.delete_item(
                Key={'Theatre-Seat': theatre_seat},
                ReturnValues='ALL_OLD'
            )
            
            if 'Attributes' in response:
                deleted_item = self._process_item_from_dynamodb(response['Attributes'])
                return {
                    'message': 'Ticket deleted successfully',
                    'Theatre-Seat': theatre_seat,
                    'deletedItem': deleted_item
                }
            else:
                raise ValueError("Ticket not found")
        except Exception as e:
            logger.error(f"Error deleting ticket: {e}")
            raise

    def _process_item_for_dynamodb(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert item for DynamoDB storage"""
        processed = {}
        for key, value in item.items():
            if isinstance(value, float):
                processed[key] = Decimal(str(value))
            else:
                processed[key] = value
        return processed

    def _process_item_from_dynamodb(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert item from DynamoDB format"""
        processed = {}
        for key, value in item.items():
            if isinstance(value, Decimal):
                processed[key] = float(value)
            else:
                processed[key] = value
        return processed

    def _convert_to_decimal_if_number(self, value: Any) -> Any:
        """Convert numeric values to Decimal for DynamoDB"""
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        return value
