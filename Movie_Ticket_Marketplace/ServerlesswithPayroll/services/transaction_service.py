import boto3
import uuid
import logging
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional

from utils.database import get_table
# ✅ REMOVED: from services.user_service import UserService - This was causing circular import

logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self):
        self.transactions_table = boto3.resource('dynamodb').Table('user-transactions')
        self.tickets_table = get_table()
        # ✅ REMOVED: self.user_service = UserService() - Initialize when needed instead

    async def process_ticket_purchase(self, user_id: str, theatre_seat: str, purchase_price: float, payment_method: str) -> Dict:
        """Process a ticket purchase and update user payroll"""
        
        # Check if ticket exists and is available
        ticket_response = self.tickets_table.get_item(Key={'Theatre-Seat': theatre_seat})
        if 'Item' not in ticket_response:
            raise Exception("Ticket not found")
            
        ticket = ticket_response['Item']
        if ticket.get('status') == 'sold':
            raise Exception("Ticket already sold")
        
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # Create transaction record
            transaction_data = {
                'transactionId': transaction_id,
                'userId': user_id,
                'transactionType': 'PURCHASE',
                'theatreSeat': theatre_seat,
                'movie': ticket.get('Movie'),
                'amount': Decimal(str(purchase_price)),
                'paymentMethod': payment_method,
                'timestamp': timestamp,
                'status': 'COMPLETED',
                'description': f"Purchased ticket for {ticket.get('Movie')} - Seat {theatre_seat}"
            }
            
            # Save transaction
            self.transactions_table.put_item(Item=transaction_data)
            
            # Update ticket status and owner
            self.tickets_table.update_item(
                Key={'Theatre-Seat': theatre_seat},
                UpdateExpression='SET #status = :status, #owner = :owner, #purchasePrice = :price, #purchaseTimestamp = :timestamp',
                ExpressionAttributeNames={
                    '#status': 'status',
                    '#owner': 'owner',
                    '#purchasePrice': 'purchasePrice',
                    '#purchaseTimestamp': 'purchaseTimestamp'
                },
                ExpressionAttributeValues={
                    ':status': 'sold',
                    ':owner': user_id,
                    ':price': Decimal(str(purchase_price)),
                    ':timestamp': timestamp
                }
            )
            
            # ✅ LOCAL IMPORT - Import UserService only when needed to avoid circular import
            from services.user_service import UserService
            user_service = UserService()
            updated_payroll = await user_service.update_user_balance(user_id, -purchase_price, transaction_id)
            
            return {
                'transaction_id': transaction_id,
                'user_balance': updated_payroll['currentBalance'],
                'ticket_details': ticket
            }
            
        except Exception as e:
            logger.error(f"Error processing ticket purchase: {str(e)}")
            raise

    async def process_ticket_sale(self, seller_id: str, buyer_id: str, theatre_seat: str, sale_price: float) -> Dict:
        """Process a ticket sale between two users"""
        
        # Verify seller owns the ticket
        ticket_response = self.tickets_table.get_item(Key={'Theatre-Seat': theatre_seat})
        if 'Item' not in ticket_response:
            raise Exception("Ticket not found")
            
        ticket = ticket_response['Item']
        if ticket.get('owner') != seller_id:
            raise Exception("Seller does not own this ticket")
        
        seller_transaction_id = str(uuid.uuid4())
        buyer_transaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # Create seller transaction (positive - income)
            seller_transaction = {
                'transactionId': seller_transaction_id,
                'userId': seller_id,
                'transactionType': 'SALE',
                'theatreSeat': theatre_seat,
                'movie': ticket.get('Movie'),
                'amount': Decimal(str(sale_price)),
                'buyerId': buyer_id,
                'timestamp': timestamp,
                'status': 'COMPLETED',
                'description': f"Sold ticket for {ticket.get('Movie')} - Seat {theatre_seat} to {buyer_id}"
            }
            
            # Create buyer transaction (negative - expense)
            buyer_transaction = {
                'transactionId': buyer_transaction_id,
                'userId': buyer_id,
                'transactionType': 'PURCHASE',
                'theatreSeat': theatre_seat,
                'movie': ticket.get('Movie'),
                'amount': Decimal(str(sale_price)),
                'sellerId': seller_id,
                'timestamp': timestamp,
                'status': 'COMPLETED',
                'description': f"Purchased ticket for {ticket.get('Movie')} - Seat {theatre_seat} from {seller_id}"
            }
            
            # Save both transactions
            self.transactions_table.put_item(Item=seller_transaction)
            self.transactions_table.put_item(Item=buyer_transaction)
            
            # Update ticket ownership
            original_purchase_price = ticket.get('purchasePrice', Decimal('0'))
            self.tickets_table.update_item(
                Key={'Theatre-Seat': theatre_seat},
                UpdateExpression='SET #owner = :new_owner, #salePrice = :sale_price, #saleTimestamp = :timestamp, #previousOwner = :previous_owner, #originalPurchasePrice = :original_price',
                ExpressionAttributeNames={
                    '#owner': 'owner',
                    '#salePrice': 'salePrice',
                    '#saleTimestamp': 'saleTimestamp',
                    '#previousOwner': 'previousOwner',
                    '#originalPurchasePrice': 'originalPurchasePrice'
                },
                ExpressionAttributeValues={
                    ':new_owner': buyer_id,
                    ':sale_price': Decimal(str(sale_price)),
                    ':timestamp': timestamp,
                    ':previous_owner': seller_id,
                    ':original_price': original_purchase_price
                }
            )
            
            # ✅ LOCAL IMPORT - Import UserService only when needed to avoid circular import
            from services.user_service import UserService
            user_service = UserService()
            seller_payroll = await user_service.update_user_balance(seller_id, sale_price, seller_transaction_id)
            buyer_payroll = await user_service.update_user_balance(buyer_id, -sale_price, buyer_transaction_id)
            
            return {
                'seller_transaction_id': seller_transaction_id,
                'buyer_transaction_id': buyer_transaction_id,
                'seller_balance': seller_payroll['currentBalance'],
                'buyer_balance': buyer_payroll['currentBalance']
            }
            
        except Exception as e:
            logger.error(f"Error processing ticket sale: {str(e)}")
            raise

    async def get_user_transactions(self, user_id: str, limit: int = 50, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Get transaction history for a user"""
        
        try:
            query_params = {
                'IndexName': 'UserTransactionsIndex',
                'KeyConditionExpression': 'userId = :user_id',
                'ExpressionAttributeValues': {':user_id': user_id},
                'ScanIndexForward': False,  # Most recent first
                'Limit': limit
            }
            
            if start_date and end_date:
                query_params['KeyConditionExpression'] += ' AND #timestamp BETWEEN :start_date AND :end_date'
                query_params['ExpressionAttributeNames'] = {'#timestamp': 'timestamp'}
                query_params['ExpressionAttributeValues'].update({
                    ':start_date': start_date,
                    ':end_date': end_date
                })
            
            response = self.transactions_table.query(**query_params)
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Error retrieving user transactions: {str(e)}")
            raise

    async def get_transaction_by_id(self, transaction_id: str) -> Optional[Dict]:
        """Get a specific transaction by ID"""
        
        try:
            response = self.transactions_table.get_item(Key={'transactionId': transaction_id})
            return response.get('Item')
            
        except Exception as e:
            logger.error(f"Error retrieving transaction: {str(e)}")
            raise
