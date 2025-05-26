import boto3
import json
import os
import logging
from utils.encoder import CustomEncoder
from utils.response import build_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB setup
dynamodb_endpoint = os.environ.get('AWS_ENDPOINT_URL')
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID', 'test')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY', 'test')

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=os.environ.get('AWS_ENDPOINT_URL'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'test'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'test'),
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
)

table_name = os.environ.get('DYNAMODB_TABLE', 'ticket-booking')
table = dynamodb.Table(table_name)

def create_ticket(event, context):
    """Create a new ticket booking"""
    logger.info(f"Creating ticket with event: {json.dumps(event)}")
    
    try:
        # Parse request body
        if not event.get('body'):
            return build_response(400, {'error': 'Request body is required'})
        
        ticket_data = json.loads(event['body'])
        
        # Validate required fields
        if not ticket_data.get('Theatre-Seat'):
            return build_response(400, {'error': 'Theatre-Seat is required'})
        
        if not ticket_data.get('Movie'):
            return build_response(400, {'error': 'Movie is required'})
        
        # Save ticket to DynamoDB
        table.put_item(Item=ticket_data)
        
        response_body = {
            'message': 'Ticket created successfully',
            'Theatre-Seat': ticket_data['Theatre-Seat'],
            'Movie': ticket_data['Movie']
        }
        
        logger.info(f"Successfully created ticket: {ticket_data['Theatre-Seat']}")
        return build_response(201, response_body)
        
    except Exception as e:
        logger.error(f"Error creating ticket: {e}", exc_info=True)
        return build_response(500, {'error': f'Failed to create ticket: {str(e)}'})