from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import logging
from datetime import datetime

from services.transaction_service import TransactionService
from utils.encoder import CustomEncoder

router = APIRouter()
logger = logging.getLogger(__name__)

class TicketPurchaseRequest(BaseModel):
    user_id: str
    theatre_seat: str
    purchase_price: float
    payment_method: str = "credit_card"

class TicketSaleRequest(BaseModel):
    user_id: str
    theatre_seat: str
    sale_price: float
    buyer_id: str

class TicketTransferRequest(BaseModel):
    seller_id: str
    buyer_id: str
    theatre_seat: str
    transfer_price: float

@router.post("/purchase-ticket", status_code=201)
async def purchase_ticket(request: TicketPurchaseRequest):
    """Purchase a ticket and record transaction"""
    logger.info(f"Processing ticket purchase for user {request.user_id}")
    
    try:
        transaction_service = TransactionService()
        result = await transaction_service.process_ticket_purchase(
            user_id=request.user_id,
            theatre_seat=request.theatre_seat,
            purchase_price=request.purchase_price,
            payment_method=request.payment_method
        )
        
        return {
            "message": "Ticket purchased successfully",
            "transaction_id": result["transaction_id"],
            "user_balance": result["user_balance"],
            "ticket_details": result["ticket_details"]
        }
        
    except Exception as e:
        logger.error(f"Error processing ticket purchase: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sell-ticket", status_code=201)
async def sell_ticket(request: TicketSaleRequest):
    """Sell a ticket to another user and record transaction"""
    logger.info(f"Processing ticket sale from {request.user_id} to {request.buyer_id}")
    
    try:
        transaction_service = TransactionService()
        result = await transaction_service.process_ticket_sale(
            seller_id=request.user_id,
            buyer_id=request.buyer_id,
            theatre_seat=request.theatre_seat,
            sale_price=request.sale_price
        )
        
        return {
            "message": "Ticket sold successfully",
            "seller_transaction_id": result["seller_transaction_id"],
            "buyer_transaction_id": result["buyer_transaction_id"],
            "seller_balance": result["seller_balance"],
            "buyer_balance": result["buyer_balance"]
        }
        
    except Exception as e:
        logger.error(f"Error processing ticket sale: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-transactions/{user_id}")
async def get_user_transactions(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get transaction history for a user"""
    logger.info(f"Retrieving transactions for user {user_id}")
    
    try:
        transaction_service = TransactionService()
        transactions = await transaction_service.get_user_transactions(
            user_id=user_id,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "user_id": user_id,
            "transactions": transactions,
            "total_transactions": len(transactions)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transaction/{transaction_id}")
async def get_transaction_details(transaction_id: str):
    """Get details of a specific transaction"""
    logger.info(f"Retrieving transaction details for {transaction_id}")
    
    try:
        transaction_service = TransactionService()
        transaction = await transaction_service.get_transaction_by_id(transaction_id)
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
