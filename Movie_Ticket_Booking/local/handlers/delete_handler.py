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

def remove_ticket(event, context):
    """Delete a ticket booking"""
    logger.info(f"Deleting ticket with event: {json.dumps(event)}")
    
    try:
        # Parse request body
        if not event.get('body'):
            return build_response(400, {'error': 'Request body is required'})
        
        request_data = json.loads(event['body'])
        
        # Validate required field
        theatre_seat = request_data.get('Theatre-Seat')
        
        if not theatre_seat:
            return build_response(400, {'error': 'Theatre-Seat is required'})
        
        # Delete item from DynamoDB
        response = table.delete_item(
            Key={'Theatre-Seat': theatre_seat},
            ReturnValues='ALL_OLD'
        )
        
        # Check if item was actually deleted
        if 'Attributes' in response:
            response_body = {
                'message': 'Ticket deleted successfully',
                'Theatre-Seat': theatre_seat,
                'deletedItem': response['Attributes']
            }
            logger.info(f"Successfully deleted ticket: {theatre_seat}")
            return build_response(200, response_body)
        else:
            logger.warning(f"Ticket not found for deletion: {theatre_seat}")
            return build_response(404, {'error': 'Ticket not found'})
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return build_response(400, {'error': 'Invalid JSON format'})
        
    except Exception as e:
        logger.error(f"Error deleting ticket: {str(e)}")
        return build_response(500, {'error': 'Failed to delete ticket'})