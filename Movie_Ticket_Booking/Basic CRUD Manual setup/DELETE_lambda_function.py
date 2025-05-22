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
        requestBody = json.loads(event['body'])
        response = deleteticket(requestBody['Theatre-Seat'])
    else:
        response = buildresponse(400, "Invalid path for DELETE method")
    
    return response

def deleteticket(Theatre_Seat):
    try:
        response = table.delete_item(
            Key={
                'Theatre-Seat': Theatre_Seat
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Theatre-Seat': Theatre_Seat,
            'Message': 'Ticket deleted successfully'
        }
        if 'Attributes' in response:
            return buildresponse(200, body)
        else:
            return buildresponse(404, "Ticket not found")
    except:
        logger.exception("Error deleting ticket")
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