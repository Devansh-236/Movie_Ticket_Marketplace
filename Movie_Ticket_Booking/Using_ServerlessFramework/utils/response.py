import json
from utils.encoder import CustomEncoder

def build_response(status_code, body=None):
    """Build a standardized API Gateway response"""
    
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,PATCH,DELETE,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        }
    }
    
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    
    return response