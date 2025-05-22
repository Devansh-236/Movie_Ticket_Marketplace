import boto3
import json
import os
import logging
from utils.encoder import CustomEncoder
from utils.response import build_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'ticket-booking')
table = dynamodb.Table(table_name)

def update_ticket(event, context):
    """Update an existing ticket"""
    logger.info(f"Updating ticket with event: {json.dumps(event)}")
    
    try:
        # Parse request body
        if not event.get('body'):
            return build_response(400, {'error': 'Request body is required'})
        
        request_data = json.loads(event['body'])
        
        # Validate required fields
        theatre_seat = request_data.get('Theatre-Seat')
        update_key = request_data.get('updateKey')
        update_value = request_data.get('updateValue')
        
        if not theatre_seat:
            return build_response(400, {'error': 'Theatre-Seat is required'})
        
        if not update_key:
            return build_response(400, {'error': 'updateKey is required'})
        
        if update_value is None:
            return build_response(400, {'error': 'updateValue is required'})
        
        # Prevent updating the primary key
        if update_key == 'Theatre-Seat':
            return build_response(400, {'error': 'Cannot update primary key Theatre-Seat'})
        
        # Update item in DynamoDB
        response = table.update_item(
            Key={'Theatre-Seat': theatre_seat},
            UpdateExpression=f'SET #{update_key} = :val',
            ExpressionAttributeNames={f'#{update_key}': update_key},
            ExpressionAttributeValues={':val': update_value},
            ReturnValues='ALL_NEW'
        )
        
        response_body = {
            'message': 'Ticket updated successfully',
            'Theatre-Seat': theatre_seat,
            'updateKey': update_key,
            'updateValue': update_value,
            'updatedItem': response.get('Attributes', {})
        }
        
        logger.info(f"Successfully updated ticket: {theatre_seat}")
        return build_response(200, response_body)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return build_response(400, {'error': 'Invalid JSON format'})
        
    except Exception as e:
        logger.error(f"Error updating ticket: {str(e)}")
        # Check if it's a conditional check failed error (item doesn't exist)
        if 'ConditionalCheckFailedException' in str(e):
            return build_response(404, {'error': 'Ticket not found'})
        return build_response(500, {'error': 'Failed to update ticket'})