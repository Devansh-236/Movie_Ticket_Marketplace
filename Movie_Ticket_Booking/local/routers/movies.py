from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
import logging

from services.dynamodb_service import DynamoDBService

router = APIRouter()
logger = logging.getLogger(__name__)

def get_dynamodb_service(request: Request) -> DynamoDBService:
    return request.app.state.dynamodb_service

@router.get("/movies")
async def get_movies(
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service)
):
    """Retrieve all unique movies from tickets"""
    try:
        movies = dynamodb_service.get_movies()
        return {"movies": movies}
    except Exception as e:
        logger.error(f"Error retrieving movies: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve movies")
