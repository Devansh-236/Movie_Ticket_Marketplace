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

def get_movies(event, context):
    """Retrieve all unique movies from tickets"""
    logger.info("Retrieving all unique movies")
    
    try:
        response = table.scan()
        items = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        # Extract unique movie names
        unique_movies = list({item.get('Movie') for item in items if item.get('Movie')})
        
        return build_response(200, {'movies': unique_movies})
        
    except Exception as e:
        logger.error(f"Error retrieving movies: {str(e)}")
        return build_response(500, {'error': 'Failed to retrieve movies'})

def get_ticket(event, context):
    """Retrieve a specific ticket by Theatre-Seat ID"""
    logger.info(f"Retrieving ticket with event: {json.dumps(event)}")
    
    try:
        # Get Theatre-Seat from query parameters
        query_params = event.get('queryStringParameters') or {}
        theatre_seat = query_params.get('Theatre-Seat')
        
        if not theatre_seat:
            return build_response(400, {'error': 'Theatre-Seat query parameter is required'})
        
        response = table.get_item(
            Key={'Theatre-Seat': theatre_seat}
        )
        
        if 'Item' in response:
            return build_response(200, response['Item'])
        else:
            return build_response(404, {'error': 'Ticket not found'})
            
    except Exception as e:
        logger.error(f"Error retrieving ticket: {str(e)}")
        return build_response(500, {'error': 'Failed to retrieve ticket'})

def get_all_tickets(event, context):
    """Retrieve all tickets"""
    logger.info("Retrieving all tickets")
    
    try:
        response = table.scan()
        items = response.get('Items', [])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        return build_response(200, {'tickets': items})
        
    except Exception as e:
        logger.error(f"Error retrieving all tickets: {str(e)}")
        return build_response(500, {'error': 'Failed to retrieve tickets'})