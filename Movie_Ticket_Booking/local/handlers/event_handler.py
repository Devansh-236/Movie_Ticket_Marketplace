import boto3
import json
import os
import logging
from decimal import Decimal
from datetime import datetime
from utils.encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'ticket-booking')
table = dynamodb.Table(table_name)

# SNS setup
sns = boto3.client('sns')
topic_arn = os.environ.get('PRICE_CHANGE_TOPIC_ARN')

# SQS setup
sqs = boto3.client('sqs')
queue_url = os.environ.get('SQS_QUEUE_URL')

async def handle_price_change_event(event, context):
    """Handle price change events from SQS queue"""
    logger.info(f"Received SQS event: {json.dumps(event)}")
    try:
        # Parse SQS messages
        for record in event.get('Records', []):
            if record.get('eventSource') == 'aws:sqs':
                # SQS message body contains the SNS message
                sqs_body = json.loads(record['body'])
                # Extract the actual SNS message
                if 'Message' in sqs_body:
                    # This is an SNS message delivered via SQS
                    message = json.loads(sqs_body['Message'])
                else:
                    # Direct SQS message (fallback)
                    message = sqs_body
                # Process the message
                await process_price_change_message(message)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Price change event processed successfully'})
        }
    except Exception as e:
        logger.error(f"Error processing SQS price change event: {str(e)}")
        # Re-raise the exception to trigger SQS retry mechanism
        raise e

async def process_price_change_message(message):
    """Process individual price change message"""
    try:
        # Extract event details
        event_type = message.get('eventType')
        theatre_seat = message.get('theatreSeat')
        movie = message.get('movie')
        old_price = message.get('oldPrice')
        new_price = message.get('newPrice')
        timestamp = message.get('timestamp')
        
        logger.info(f"Processing {event_type} for {theatre_seat}: {old_price} -> {new_price}")
        
        # Only process initial price change events to avoid infinite loops
        if event_type == 'PriceChangeInitiated':
            # Perform additional business logic update
            additional_updates = {}
            additional_updates['LastPriceChangeTimestamp'] = datetime.utcnow().isoformat()
            additional_updates['PreviousPrice'] = Decimal(str(old_price)) if old_price else None

            # Calculate discount if price decreased
            if old_price and new_price < old_price:
                discount_percentage = round(((old_price - new_price) / old_price) * 100, 2)
                additional_updates['DiscountPercentage'] = Decimal(str(discount_percentage))
                additional_updates['IsDiscounted'] = True
            else:
                additional_updates['DiscountPercentage'] = Decimal('0')
                additional_updates['IsDiscounted'] = False

            # Update the ticket with additional metadata
            update_expression_parts = []
            expression_attribute_names = {}
            expression_attribute_values = {}

            for key, value in additional_updates.items():
                update_expression_parts.append(f'#{key} = :{key}')
                expression_attribute_names[f'#{key}'] = key
                expression_attribute_values[f':{key}'] = value

            if update_expression_parts:
                update_expression = 'SET ' + ', '.join(update_expression_parts)
                response = table.update_item(
                    Key={'Theatre-Seat': theatre_seat},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
                    ReturnValues='ALL_NEW'
                )
                updated_item = response.get('Attributes', {})
                logger.info(f"Added price change metadata for {theatre_seat}")

                # Publish another event indicating the processing is complete
                completion_event = {
                    'eventType': 'PriceChangeProcessed',
                    'theatreSeat': theatre_seat,
                    'movie': movie,
                    'finalPrice': new_price,
                    'priceChangeTimestamp': additional_updates['LastPriceChangeTimestamp'],
                    'isDiscounted': additional_updates['IsDiscounted'],
                    'discountPercentage': float(additional_updates['DiscountPercentage']),
                    'processedAt': datetime.utcnow().isoformat(),
                    'updatedItem': updated_item
                }

                if topic_arn:
                    try:
                        sns.publish(
                            TopicArn=topic_arn,
                            Message=json.dumps(completion_event, cls=CustomEncoder),
                            Subject=f'Price Change Processed for {theatre_seat}'
                        )
                        logger.info(f"Published price change completion event for {theatre_seat}")
                    except Exception as sns_error:
                        logger.error(f"Failed to publish completion event: {str(sns_error)}")

        elif event_type == 'PriceChangeProcessed':
            logger.info(f"Price change processing completed for {theatre_seat}")
            # This is the final event in the chain - just log it

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Price change event processed successfully'})
        }

    except Exception as e:
        logger.error(f"Error processing price change event: {str(e)}")
        # Re-raise the exception to trigger SNS retry mechanism
        raise e