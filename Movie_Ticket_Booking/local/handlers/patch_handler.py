import boto3
import json
import os
import logging
from decimal import Decimal
from datetime import datetime

from utils.encoder import CustomEncoder
from utils.response import build_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'ticket-booking')
table = dynamodb.Table(table_name)

# SNS setup
sns = boto3.client('sns')
topic_arn = os.environ.get('PRICE_CHANGE_TOPIC_ARN')


def update_ticket(event, context):
    """Update an existing ticket"""
    logger.info(f"Updating ticket with event: {json.dumps(event)}")
    
    try:
        # Parse request body
        if not event.get('body'):
            return build_response(400, {'error': 'Request body is required'})

        request_data = json.loads(event['body'])

        # Validate required fields
        theatre_seat = request_data.get('Theatre-Seat')
        update_key = request_data.get('updateKey')
        update_value = request_data.get('updateValue')

        if not theatre_seat:
            return build_response(400, {'error': 'Theatre-Seat is required'})

        if not update_key:
            return build_response(400, {'error': 'updateKey is required'})

        if update_value is None:
            return build_response(400, {'error': 'updateValue is required'})

        # Prevent updating the primary key
        if update_key == 'Theatre-Seat':
            return build_response(400, {'error': 'Cannot update primary key Theatre-Seat'})
        
        # Get the current item to check for price changes
        current_item_response = table.get_item(Key={'Theatre-Seat': theatre_seat})
        current_item = current_item_response.get('Item')
        
        if not current_item:
            return build_response(404, {'error': 'Ticket not found'})
        
        # If updating the price, also update PreviousPrice and LastPriceChangeTimestamp
        is_price_change = update_key.lower() == 'price'
        if is_price_change:
            old_price = current_item.get('Price')
            new_price = update_value
            timestamp = datetime.utcnow().isoformat()

            update_expression = "SET #Price = :newPrice, #PreviousPrice = :oldPrice, #LastPriceChangeTimestamp = :timestamp"
            expression_attribute_names = {
                "#Price": "Price",
                "#PreviousPrice": "PreviousPrice",
                "#LastPriceChangeTimestamp": "LastPriceChangeTimestamp"
            }
            expression_attribute_values = {
                ":newPrice": new_price,
                ":oldPrice": old_price,
                ":timestamp": timestamp
            }
        else:
            update_expression = f"SET #{update_key} = :val"
            expression_attribute_names = {f"#{update_key}": update_key}
            expression_attribute_values = {":val": update_value}

        response = table.update_item(
            Key={'Theatre-Seat': theatre_seat},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        
        updated_item = response.get('Attributes', {})

        # Check if this is a price change and publish event
        is_price_change = update_key.lower() == 'price'
        if is_price_change and topic_arn:
            old_price = current_item.get('Price')
            new_price = update_value

            # Publish price change event
            event_message = {
                'eventType': 'PriceChangeInitiated',
                'theatreSeat': theatre_seat,
                'movie': updated_item.get('Movie'),
                'oldPrice': float(old_price) if isinstance(old_price, Decimal) else old_price,
                'newPrice': float(new_price) if isinstance(new_price, Decimal) else new_price,
                'timestamp': context.aws_request_id,
                'updatedItem': updated_item
            }

            try:
                sns.publish(
                    TopicArn=topic_arn,
                    Message=json.dumps(event_message, cls=CustomEncoder),
                    Subject=f'Price Change Event for {theatre_seat}'
                )
                logger.info(f"Published price change event for {theatre_seat}")
            except Exception as sns_error:
                logger.error(f"Failed to publish price change event: {str(sns_error)}")
                # Continue processing even if event publishing fails

        response_body = {
            'message': 'Ticket updated successfully',
            'Theatre-Seat': theatre_seat,
            'updateKey': update_key,
            'updateValue': update_value,
            'updatedItem': updated_item,
            'priceChangeEventPublished': is_price_change and topic_arn is not None
        }
        
        logger.info(f"Successfully updated ticket: {theatre_seat}")
        return build_response(200, response_body)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return build_response(400, {'error': 'Invalid JSON format'})

    except Exception as e:
        logger.error(f"Error updating ticket: {str(e)}")
        # Check if it's a conditional check failed error (item doesn't exist)
        if 'ConditionalCheckFailedException' in str(e):
            return build_response(404, {'error': 'Ticket not found'})
        return build_response(500, {'error': 'Failed to update ticket'})