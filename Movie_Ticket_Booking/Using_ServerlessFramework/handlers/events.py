from fastapi import APIRouter, HTTPException
import boto3
import json
import os
import logging
from decimal import Decimal
from datetime import datetime
from utils.database import get_table
from utils.encoder import CustomEncoder

router = APIRouter()
logger = logging.getLogger(__name__)

# SNS setup
sns = boto3.client('sns')
topic_arn = os.environ.get('PRICE_CHANGE_TOPIC_ARN')

async def handle_price_change_event(event_data: dict):
    """Handle price change events"""
    logger.info(f"Processing price change event: {json.dumps(event_data)}")
    
    try:
        table = get_table()
        
        # Extract event details
        event_type = event_data.get('eventType')
        theatre_seat = event_data.get('theatreSeat')
        movie = event_data.get('movie')
        old_price = event_data.get('oldPrice')
        new_price = event_data.get('newPrice')
        
        # Only process initial price change events
        if event_type == 'PriceChangeInitiated':
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
                
                # Publish completion event
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
        
        return {"message": "Price change event processed successfully"}
        
    except Exception as e:
        logger.error(f"Error processing price change event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process price change event")
