import json
from decimal import Decimal

class CustomEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal types."""
    
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
