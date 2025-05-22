import boto3
import json
from custom_encoder import CustomEncoder
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = "ticket-booking"
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event))
    path = event['path']
    
    if path == '/movies':
        response = getmovies()
    elif path == '/ticket':
        if event.get('queryStringParameters') and 'Theatre-Seat' in event['queryStringParameters']:
            response = getticket(event['queryStringParameters']['Theatre-Seat'])
        else:
            response = buildresponse(400, "Missing Theatre-Seat query parameter")
    elif path == '/tickets':
        response = gettickets()
    else:
        response = buildresponse(400, "Invalid path for GET method")
    
    return response

def getmovies():
    try:
        response = table.scan()
        items = response.get('Items', [])
        # Extract unique movie names
        unique_movies = list({item.get('Movie') for item in items if 'Movie' in item})
        body = {
            'movies': unique_movies
        }
        return buildresponse(200, body)
    except Exception as e:
        logger.error("Error getting movies: " + str(e))
        return buildresponse(500, "Internal server error")

def getticket(ticketId):
    try:
        response = table.get_item(
            Key={
                'Theatre-Seat': ticketId
            }
        )
        if 'Item' in response:
            return buildresponse(200, response['Item'])
        else:
            return buildresponse(404, "Ticket not found")
    except Exception as e:
        logger.error("Error getting ticket: " + str(e))
        return buildresponse(500, "Internal server error")

def gettickets():
    try:
        response = table.scan()
        items = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        body = {
            'tickets': items
        }
        return buildresponse(200, body)
    except:
        logger.exception("Error getting tickets")
        return buildresponse(500, "Internal server error")

def buildresponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    
    return response