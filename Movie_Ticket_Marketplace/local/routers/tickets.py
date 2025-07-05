from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any
import logging

from models.ticket import TicketCreate, TicketUpdate, TicketDelete, TicketResponse
from services.dynamodb_service import DynamoDBService
from services.sns_service import SNSService

router = APIRouter()
logger = logging.getLogger(__name__)

def get_dynamodb_service(request: Request) -> DynamoDBService:
    return request.app.state.dynamodb_service

@router.post("/ticket", response_model=Dict[str, Any], status_code=201)
async def create_ticket(
    ticket: TicketCreate,
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Create a new ticket booking"""
    try:
        ticket_data = ticket.model_dump(by_alias=True, exclude_none=True)
        
        # Validate required fields
        if not ticket_data.get('Theatre-Seat'):
            raise HTTPException(status_code=400, detail="Theatre-Seat is required")
        if not ticket_data.get('Movie'):
            raise HTTPException(status_code=400, detail="Movie is required")
        
        result = dynamodb_service.create_ticket(ticket_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        raise HTTPException(status_code=500, detail="Failed to create ticket")

@router.get("/ticket")
async def get_ticket(
    theatre_seat: str,
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Retrieve a specific ticket by Theatre-Seat ID"""
    try:
        if not theatre_seat:
            raise HTTPException(status_code=400, detail="Theatre-Seat query parameter is required")
        
        ticket = dynamodb_service.get_ticket(theatre_seat)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving ticket: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve ticket")

@router.get("/tickets")
async def get_all_tickets(
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Retrieve all tickets"""
    try:
        tickets = dynamodb_service.get_all_tickets()
        return {"tickets": tickets}
    except Exception as e:
        logger.error(f"Error retrieving all tickets: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tickets")

@router.patch("/ticket")
async def update_ticket(
    ticket_update: TicketUpdate,
    request: Request,
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Update an existing ticket"""
    try:
        update_data = ticket_update.model_dump(by_alias=True)
        theatre_seat = update_data.get('Theatre-Seat')
        update_key = update_data.get('updateKey')
        update_value = update_data.get('updateValue')
        
        # Validate required fields
        if not theatre_seat:
            raise HTTPException(status_code=400, detail="Theatre-Seat is required")
        if not update_key:
            raise HTTPException(status_code=400, detail="updateKey is required")
        if update_value is None:
            raise HTTPException(status_code=400, detail="updateValue is required")
        
        result = dynamodb_service.update_ticket(theatre_seat, update_key, update_value)
        
        # Handle price change events
        is_price_change = update_key.lower() == 'price'
        if is_price_change:
            sns_service = SNSService()
            current_item = result.get('current_item', {})
            updated_item = result.get('updatedItem', {})
            
            event_data = {
                'eventType': 'PriceChangeInitiated',
                'theatreSeat': theatre_seat,
                'movie': updated_item.get('Movie'),
                'oldPrice': float(current_item.get('Price', 0)),
                'newPrice': float(update_value),
                'timestamp': 'fastapi-request',
                'updatedItem': updated_item
            }
            
            event_published = sns_service.publish_price_change_event(event_data)
            result['priceChangeEventPublished'] = event_published
        
        return result
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating ticket: {e}")
        raise HTTPException(status_code=500, detail="Failed to update ticket")

@router.delete("/ticket")
async def delete_ticket(
    ticket_delete: TicketDelete,
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Delete a ticket booking"""
    try:
        delete_data = ticket_delete.model_dump(by_alias=True)
        theatre_seat = delete_data.get('Theatre-Seat')
        
        if not theatre_seat:
            raise HTTPException(status_code=400, detail="Theatre-Seat is required")
        
        result = dynamodb_service.delete_ticket(theatre_seat)
        return result
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting ticket: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete ticket")
