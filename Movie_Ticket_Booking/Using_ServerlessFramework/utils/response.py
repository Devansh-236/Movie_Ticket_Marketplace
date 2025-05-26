from typing import Any, Dict, Optional
import json
from utils.encoder import CustomEncoder

def create_response(
    status_code: int,
    body: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create a standardized API response."""
    
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PATCH,DELETE'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body, cls=CustomEncoder)
    }

def success_response(data: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    """Create a success response."""
    return create_response(status_code, data)

def error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
    """Create an error response."""
    return create_response(status_code, {'error': message})
