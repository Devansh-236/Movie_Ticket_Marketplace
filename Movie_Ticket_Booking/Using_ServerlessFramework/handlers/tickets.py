from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
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

# Pydantic models
class TicketCreate(BaseModel):
    theatre_seat: str = Field(..., alias="Theatre-Seat")
    movie: str = Field(..., alias="Movie")
    price: Optional[float] = None
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class TicketUpdate(BaseModel):
    theatre_seat: str = Field(..., alias="Theatre-Seat")
    update_key: str = Field(..., alias="updateKey")
    update_value: Any = Field(..., alias="updateValue")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

class TicketDelete(BaseModel):
    theatre_seat: str = Field(..., alias="Theatre-Seat")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

# SNS setup
sns = boto3.client('sns')
topic_arn = os.environ.get('PRICE_CHANGE_TOPIC_ARN')

@router.get("/ticket")
async def get_ticket(theatre_seat: str = Query(..., alias="Theatre-Seat")):
    """Retrieve a specific ticket by Theatre-Seat ID"""
    logger.info(f"Retrieving ticket: {theatre_seat}")
    
    try:
        table = get_table()
        response = table.get_item(Key={'Theatre-Seat': theatre_seat})
        
        if 'Item' in response:
            return response['Item']
        else:
            raise HTTPException(status_code=404, detail="Ticket not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve ticket")

@router.get("/tickets")
async def get_all_tickets():
    """Retrieve all tickets"""
    logger.info("Retrieving all tickets")
    
    try:
        table = get_table()
        response = table.scan()
        items = response.get('Items', [])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        return {"tickets": items}
        
    except Exception as e:
        logger.error(f"Error retrieving all tickets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tickets")

@router.post("/ticket", status_code=201)
async def create_ticket(ticket: TicketCreate):
    """Create a new ticket booking"""
    logger.info(f"Creating ticket: {ticket.theatre_seat}")
    
    try:
        table = get_table()
        
        # Convert to dict and handle field mapping
        ticket_data = {
            'Theatre-Seat': ticket.theatre_seat,
            'Movie': ticket.movie
        }
        
        if ticket.price is not None:
            ticket_data['Price'] = Decimal(str(ticket.price))
        
        # Save ticket to DynamoDB
        table.put_item(Item=ticket_data)
        
        response_body = {
            'message': 'Ticket created successfully',
            'Theatre-Seat': ticket.theatre_seat,
            'Movie': ticket.movie
        }
        
        logger.info(f"Successfully created ticket: {ticket.theatre_seat}")
        return response_body
        
    except Exception as e:
        logger.error(f"Error creating ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create ticket")

@router.patch("/ticket")
async def update_ticket(ticket_update: TicketUpdate):
    """Update an existing ticket"""
    logger.info(f"Updating ticket: {ticket_update.theatre_seat}")
    
    try:
        table = get_table()
        
        # Prevent updating the primary key
        if ticket_update.update_key == 'Theatre-Seat':
            raise HTTPException(status_code=400, detail="Cannot update primary key Theatre-Seat")
        
        # Get the current item to check for price changes
        current_item_response = table.get_item(Key={'Theatre-Seat': ticket_update.theatre_seat})
        current_item = current_item_response.get('Item')
        
        if not current_item:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Check if this is a price change
        is_price_change = ticket_update.update_key.lower() == 'price'
        
        if is_price_change:
            old_price = current_item.get('Price')
            new_price = Decimal(str(ticket_update.update_value))
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
            update_expression = f"SET #{ticket_update.update_key} = :val"
            expression_attribute_names = {f"#{ticket_update.update_key}": ticket_update.update_key}
            expression_attribute_values = {":val": ticket_update.update_value}
        
        response = table.update_item(
            Key={'Theatre-Seat': ticket_update.theatre_seat},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        
        updated_item = response.get('Attributes', {})
        
        # Publish price change event if applicable
        if is_price_change and topic_arn:
            old_price = current_item.get('Price')
            new_price = ticket_update.update_value
            
            event_message = {
                'eventType': 'PriceChangeInitiated',
                'theatreSeat': ticket_update.theatre_seat,
                'movie': updated_item.get('Movie'),
                'oldPrice': float(old_price) if isinstance(old_price, Decimal) else old_price,
                'newPrice': float(new_price) if isinstance(new_price, Decimal) else new_price,
                'timestamp': datetime.utcnow().isoformat(),
                'updatedItem': updated_item
            }
            
            try:
                sns.publish(
                    TopicArn=topic_arn,
                    Message=json.dumps(event_message, cls=CustomEncoder),
                    Subject=f'Price Change Event for {ticket_update.theatre_seat}'
                )
                logger.info(f"Published price change event for {ticket_update.theatre_seat}")
            except Exception as sns_error:
                logger.error(f"Failed to publish price change event: {str(sns_error)}")
        
        response_body = {
            'message': 'Ticket updated successfully',
            'Theatre-Seat': ticket_update.theatre_seat,
            'updateKey': ticket_update.update_key,
            'updateValue': ticket_update.update_value,
            'updatedItem': updated_item,
            'priceChangeEventPublished': is_price_change and topic_arn is not None
        }
        
        logger.info(f"Successfully updated ticket: {ticket_update.theatre_seat}")
        return response_body
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update ticket")

@router.delete("/ticket")
async def delete_ticket(ticket_delete: TicketDelete):
    """Delete a ticket booking"""
    logger.info(f"Deleting ticket: {ticket_delete.theatre_seat}")
    
    try:
        table = get_table()
        
        response = table.delete_item(
            Key={'Theatre-Seat': ticket_delete.theatre_seat},
            ReturnValues='ALL_OLD'
        )
        
        if 'Attributes' in response:
            response_body = {
                'message': 'Ticket deleted successfully',
                'Theatre-Seat': ticket_delete.theatre_seat,
                'deletedItem': response['Attributes']
            }
            logger.info(f"Successfully deleted ticket: {ticket_delete.theatre_seat}")
            return response_body
        else:
            raise HTTPException(status_code=404, detail="Ticket not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete ticket")
