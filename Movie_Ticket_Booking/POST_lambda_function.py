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
    
    if path == '/ticket':
        response = saveticket(json.loads(event['body']))
    else:
        response = buildresponse(400, "Invalid path for POST method")
    
    return response

def saveticket(ticket):
    try:
        table.put_item(
            Item=ticket
        )
        body = {
            'Theatre-Seat': ticket['Theatre-Seat'],
            'Movie': ticket['Movie'],
        }
        return buildresponse(200, "Ticket saved successfully")
    except Exception as e:
        logger.error("Error saving ticket: " + str(e))
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