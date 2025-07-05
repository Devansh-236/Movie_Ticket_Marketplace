from fastapi import APIRouter, HTTPException
import boto3
import os
import logging
from utils.database import get_table
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/movies", response_model=dict)
async def get_movies():
    """Retrieve all unique movies from tickets"""
    logger.info("Retrieving all unique movies")
    
    try:
        table = get_table()
        response = table.scan()
        items = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        # Extract unique movie names
        unique_movies = list({item.get('Movie') for item in items if item.get('Movie')})
        
        return {"movies": unique_movies}
        
    except Exception as e:
        logger.error(f"Error retrieving movies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve movies")
