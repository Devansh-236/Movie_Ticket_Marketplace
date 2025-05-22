import boto3
import json
from custom_encoder import CustomEncoder
import logging
logger=logging.getLogger()
logger.setLevel(logging.INFO)
dynamodbTableName="ticket-booking"
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getmethod='GET'
postmethod='POST'
patchmethod='PATCH'
deletemethod='DELETE'

movies='/movies'
ticket='/ticket'
tickets='/tickets'

def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event))
    httpMethod = event['httpMethod']
    path = event['path']
    if httpMethod == getmethod:
        if path == movies:
            response = getmovies()
        elif path == ticket:
            if event.get('queryStringParameters') and 'Theatre-Seat' in event['queryStringParameters']:
                response = getticket(event['queryStringParameters']['Theatre-Seat'])
            else:
                response = buildresponse(400, "Missing Theatre-Seat query parameter")
        elif path == tickets:
            response = gettickets()
    elif httpMethod == postmethod:
        if path == ticket:
            response = saveticket(json.loads(event['body']))
    elif httpMethod == patchmethod:
        if path == ticket:
            requestBody = json.loads(event['body'])
            response=modifyticket(requestBody['Theatre-Seat'],requestBody['updateKey'],requestBody['updateValue'])
    elif httpMethod == deletemethod:
        if path == ticket:
            requestBody = json.loads(event['body'])
            response = deleteticket(requestBody['Theatre-Seat'])
    else:
        response = buildresponse(400, "Invalid HTTP method or path")
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
    except :
        logger.exception("Error getting tickets")
        return buildresponse(500, "Internal server error")

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

def modifyticket(Theatre_Seat, updateKey, updateValue):
    try:
        response =table.update_item(
            Key={
                'Theatre-Seat': Theatre_Seat
            },
            UpdateExpression='set %s=:val' % updateKey,
            ExpressionAttributeValues={
                ':val': updateValue
            },
            ReturnValues='UPDATED_NEW'
        )
        body ={
            'Theatre-Seat': Theatre_Seat,
            'updateKey': updateKey,
            'updateValue': updateValue
        }
        return buildresponse(200, body)
    except :
        logger.exception("Error modifying ticket")

def deleteticket(Theatre_Seat):
    try:
        response = table.delete_item(
            Key={
                'Theatre-Seat': Theatre_Seat
            },
            ReturnValues='ALL_OLD'
        )
        body= {
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
