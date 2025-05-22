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
        response = modifyticket(requestBody['Theatre-Seat'], requestBody['updateKey'], requestBody['updateValue'])
    else:
        response = buildresponse(400, "Invalid path for PATCH method")
    
    return response

def modifyticket(Theatre_Seat, updateKey, updateValue):
    try:
        response = table.update_item(
            Key={
                'Theatre-Seat': Theatre_Seat
            },
            UpdateExpression='set %s=:val' % updateKey,
            ExpressionAttributeValues={
                ':val': updateValue
            },
            ReturnValues='UPDATED_NEW'
        )
        body = {
            'Theatre-Seat': Theatre_Seat,
            'updateKey': updateKey,
            'updateValue': updateValue
        }
        return buildresponse(200, body)
    except:
        logger.exception("Error modifying ticket")
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