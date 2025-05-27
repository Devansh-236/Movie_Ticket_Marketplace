import boto3
import logging
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.users_table = boto3.resource('dynamodb').Table('users-payroll')

    async def create_user(self, user_id: str, email: str, name: str, initial_balance: float = 0.0) -> Dict:
        """Create a new user with payroll tracking"""
        
        timestamp = datetime.utcnow().isoformat()
        
        user_data = {
            'userId': user_id,
            'email': email,
            'name': name,
            'currentBalance': Decimal(str(initial_balance)),
            'totalPurchases': Decimal('0'),
            'totalSales': Decimal('0'),
            'totalTransactions': 0,
            'createdAt': timestamp,
            'lastUpdated': timestamp,
            'status': 'ACTIVE'
        }
        
        try:
            # Check if user already exists
            existing_user = self.users_table.get_item(Key={'userId': user_id})
            if 'Item' in existing_user:
                raise Exception("User already exists")
            
            self.users_table.put_item(Item=user_data)
            return user_data
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    async def get_user_payroll(self, user_id: str) -> Optional[Dict]:
        """Get user's current payroll status"""
        
        try:
            response = self.users_table.get_item(Key={'userId': user_id})
            return response.get('Item')
            
        except Exception as e:
            logger.error(f"Error retrieving user payroll: {str(e)}")
            raise

    async def update_user_balance(self, user_id: str, amount: float, transaction_id: str) -> Dict:
        """Update user's balance and transaction counters"""
        
        timestamp = datetime.utcnow().isoformat()
        amount_decimal = Decimal(str(amount))
        
        try:
            # Ensure user exists
            user = await self.get_user_payroll(user_id)
            if not user:
                # Create user if doesn't exist
                await self.create_user(user_id, f"{user_id}@example.com", f"User {user_id}")
            
            if amount > 0:
                # Positive amount (sale/income)
                update_expression = 'SET currentBalance = currentBalance + :amount, totalSales = totalSales + :amount, totalTransactions = totalTransactions + :one, lastUpdated = :timestamp, lastTransactionId = :transaction_id'
            else:
                # Negative amount (purchase/expense)
                update_expression = 'SET currentBalance = currentBalance + :amount, totalPurchases = totalPurchases + :abs_amount, totalTransactions = totalTransactions + :one, lastUpdated = :timestamp, lastTransactionId = :transaction_id'
            
            expression_attribute_values = {
                ':amount': amount_decimal,
                ':one': 1,
                ':timestamp': timestamp,
                ':transaction_id': transaction_id
            }
            
            if amount < 0:
                expression_attribute_values[':abs_amount'] = abs(amount_decimal)
            
            response = self.users_table.update_item(
                Key={'userId': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            return response['Attributes']
            
        except Exception as e:
            logger.error(f"Error updating user balance: {str(e)}")
            raise

    async def get_user_summary(self, user_id: str) -> Optional[Dict]:
        """Get comprehensive user summary"""
        
        try:
            # Get payroll data
            payroll = await self.get_user_payroll(user_id)
            if not payroll:
                return None
            
            # ✅ LOCAL IMPORT - Import TransactionService only when needed to avoid circular import
            from services.transaction_service import TransactionService
            transaction_service = TransactionService()
            recent_transactions = await transaction_service.get_user_transactions(user_id, limit=10)
            
            # Calculate additional metrics
            current_balance = float(payroll.get('currentBalance', 0))
            total_purchases = float(payroll.get('totalPurchases', 0))
            total_sales = float(payroll.get('totalSales', 0))
            
            net_profit_loss = total_sales - total_purchases
            
            summary = {
                'user_info': {
                    'userId': payroll.get('userId'),
                    'email': payroll.get('email'),
                    'name': payroll.get('name'),
                    'status': payroll.get('status'),
                    'member_since': payroll.get('createdAt')
                },
                'financial_summary': {
                    'current_balance': current_balance,
                    'total_purchases': total_purchases,
                    'total_sales': total_sales,
                    'net_profit_loss': net_profit_loss,
                    'total_transactions': payroll.get('totalTransactions', 0),
                    'is_net_positive': net_profit_loss > 0
                },
                'recent_transactions': recent_transactions[:5]  # Last 5 transactions
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error retrieving user summary: {str(e)}")
            raise

    async def get_payroll_leaderboard(self, limit: int = 10, order: str = "desc") -> List[Dict]:
        """Get leaderboard of users by net payroll"""
        
        try:
            response = self.users_table.scan()
            users = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.users_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                users.extend(response.get('Items', []))
            
            # Calculate net profit/loss for each user
            for user in users:
                total_sales = float(user.get('totalSales', 0))
                total_purchases = float(user.get('totalPurchases', 0))
                user['netProfitLoss'] = total_sales - total_purchases
                user['currentBalance'] = float(user.get('currentBalance', 0))
            
            # Sort by net profit/loss
            reverse_order = order.lower() == "desc"
            sorted_users = sorted(users, key=lambda x: x['netProfitLoss'], reverse=reverse_order)
            
            # Return top users with relevant info
            leaderboard = []
            for i, user in enumerate(sorted_users[:limit]):
                leaderboard.append({
                    'rank': i + 1,
                    'userId': user.get('userId'),
                    'name': user.get('name'),
                    'currentBalance': user['currentBalance'],
                    'netProfitLoss': user['netProfitLoss'],
                    'totalTransactions': user.get('totalTransactions', 0),
                    'totalSales': float(user.get('totalSales', 0)),
                    'totalPurchases': float(user.get('totalPurchases', 0)),
                    'isNetPositive': user['netProfitLoss'] > 0
                })
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error retrieving payroll leaderboard: {str(e)}")
            raise
