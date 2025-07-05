from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from models.ticket import PriceChangeEvent
from services.event_service import EventService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/events/price-change")
async def handle_price_change_event(event: PriceChangeEvent):
    """Handle price change events (simulates SQS processing)"""
    try:
        event_service = EventService()
        result = await event_service.process_price_change_event(event.model_dump(by_alias=True))
        return result
    except Exception as e:
        logger.error(f"Error processing price change event: {e}")
        raise HTTPException(status_code=500, detail="Failed to process price change event")

@router.post("/events/simulate-sqs")
async def simulate_sqs_processing(message_body: Dict[str, Any]):
    """Simulate SQS message processing for testing"""
    try:
        event_service = EventService()
        result = await event_service.simulate_sqs_message_processing(message_body)
        return result
    except Exception as e:
        logger.error(f"Error simulating SQS processing: {e}")
        raise HTTPException(status_code=500, detail="Failed to simulate SQS processing")

@router.get("/events/stats")
async def get_event_processing_stats():
    """Get event processing statistics"""
    try:
        event_service = EventService()
        stats = event_service.get_event_processing_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting event processing stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get event processing stats")
