from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import logging

from services.user_service import UserService

router = APIRouter()
logger = logging.getLogger(__name__)

class UserCreate(BaseModel):
    user_id: str
    email: str
    name: str
    initial_balance: Optional[float] = 0.0

@router.post("/users", status_code=201)
async def create_user(user: UserCreate):
    """Create a new user with payroll tracking"""
    logger.info(f"Creating user: {user.user_id}")
    
    try:
        user_service = UserService()
        result = await user_service.create_user(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            initial_balance=user.initial_balance
        )
        
        return {
            "message": "User created successfully",
            "user_id": user.user_id,
            "payroll": result
        }
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/payroll")
async def get_user_payroll(user_id: str):
    """Get user's current payroll status"""
    logger.info(f"Retrieving payroll for user: {user_id}")
    
    try:
        user_service = UserService()
        payroll = await user_service.get_user_payroll(user_id)
        
        if not payroll:
            raise HTTPException(status_code=404, detail="User not found")
            
        return payroll
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user payroll: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/summary")
async def get_user_summary(user_id: str):
    """Get comprehensive user summary including payroll and recent transactions"""
    logger.info(f"Retrieving summary for user: {user_id}")
    
    try:
        user_service = UserService()
        summary = await user_service.get_user_summary(user_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="User not found")
            
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/leaderboard")
async def get_payroll_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    order: str = Query("desc", regex="^(asc|desc)$")
):
    """Get leaderboard of users by net payroll"""
    logger.info("Retrieving payroll leaderboard")
    
    try:
        user_service = UserService()
        leaderboard = await user_service.get_payroll_leaderboard(limit, order)
        
        return {
            "leaderboard": leaderboard,
            "total_users": len(leaderboard)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
