import logging
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime
from services.dynamodb_service import DynamoDBService

logger = logging.getLogger(__name__)

class EventService:
    def __init__(self):
        self.dynamodb_service = DynamoDBService()

    async def process_price_change_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process price change events (simulates SQS message processing)"""
        try:
            event_type = event_data.get('eventType')
            theatre_seat = event_data.get('theatreSeat')
            old_price = event_data.get('oldPrice')
            new_price = event_data.get('newPrice')
            
            logger.info(f"Processing {event_type} event for seat {theatre_seat}")
            
            if event_type == 'PriceChangeInitiated':
                return await self._handle_price_change_initiated(event_data)
            else:
                logger.warning(f"Unknown event type: {event_type}")
                return {
                    'status': 'ignored',
                    'message': f'Unknown event type: {event_type}',
                    'eventData': event_data
                }
                
        except Exception as e:
            logger.error(f"Error processing price change event: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'eventData': event_data
            }

    async def _handle_price_change_initiated(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle price change initiated events"""
        try:
            theatre_seat = event_data.get('theatreSeat')
            old_price = event_data.get('oldPrice', 0)
            new_price = event_data.get('newPrice')
            
            # Calculate discount information
            discount_info = self._calculate_discount_info(old_price, new_price)
            
            # Update the ticket with discount information
            update_result = await self._update_ticket_with_discount_info(
                theatre_seat, 
                discount_info
            )
            
            # Log the price change
            logger.info(
                f"Price change processed for {theatre_seat}: "
                f"${old_price} -> ${new_price} "
                f"(Discount: {discount_info['discount_percentage']}%)"
            )
            
            return {
                'status': 'processed',
                'message': 'Price change event processed successfully',
                'theatreSeat': theatre_seat,
                'priceChange': {
                    'oldPrice': old_price,
                    'newPrice': new_price,
                    'discountPercentage': discount_info['discount_percentage'],
                    'isDiscounted': discount_info['is_discounted']
                },
                'updateResult': update_result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling price change initiated event: {e}")
            raise

    def _calculate_discount_info(self, old_price: float, new_price: float) -> Dict[str, Any]:
        """Calculate discount information based on price change"""
        try:
            old_price = float(old_price) if old_price else 0
            new_price = float(new_price)
            
            if old_price == 0:
                # No previous price, no discount
                return {
                    'discount_percentage': Decimal('0'),
                    'is_discounted': False
                }
            
            # Calculate discount percentage
            if new_price < old_price:
                discount_amount = old_price - new_price
                discount_percentage = (discount_amount / old_price) * 100
                is_discounted = True
            else:
                discount_percentage = 0
                is_discounted = False
            
            return {
                'discount_percentage': Decimal(str(round(discount_percentage, 2))),
                'is_discounted': is_discounted
            }
            
        except Exception as e:
            logger.error(f"Error calculating discount info: {e}")
            return {
                'discount_percentage': Decimal('0'),
                'is_discounted': False
            }

    async def _update_ticket_with_discount_info(
        self, 
        theatre_seat: str, 
        discount_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update ticket with discount information"""
        try:
            # Get current ticket
            current_ticket = self.dynamodb_service.get_ticket(theatre_seat)
            if not current_ticket:
                raise ValueError(f"Ticket not found: {theatre_seat}")
            
            # Update discount percentage
            self.dynamodb_service.update_ticket(
                theatre_seat, 
                'DiscountPercentage', 
                discount_info['discount_percentage']
            )
            
            # Update is_discounted flag
            self.dynamodb_service.update_ticket(
                theatre_seat, 
                'IsDiscounted', 
                discount_info['is_discounted']
            )
            
            return {
                'status': 'updated',
                'updatedFields': ['DiscountPercentage', 'IsDiscounted'],
                'discountPercentage': float(discount_info['discount_percentage']),
                'isDiscounted': discount_info['is_discounted']
            }
            
        except Exception as e:
            logger.error(f"Error updating ticket with discount info: {e}")
            raise

    async def simulate_sqs_message_processing(self, message_body: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate SQS message processing for testing purposes"""
        try:
            logger.info("Simulating SQS message processing...")
            
            # Extract SNS message from SQS message format
            if 'Message' in message_body:
                import json
                sns_message = json.loads(message_body['Message'])
                return await self.process_price_change_event(sns_message)
            else:
                # Direct event processing
                return await self.process_price_change_event(message_body)
                
        except Exception as e:
            logger.error(f"Error simulating SQS message processing: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'messageBody': message_body
            }

    def get_event_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about event processing"""
        try:
            # Get all tickets to calculate stats
            all_tickets = self.dynamodb_service.get_all_tickets()
            
            total_tickets = len(all_tickets)
            discounted_tickets = sum(1 for ticket in all_tickets if ticket.get('IsDiscounted', False))
            
            # Calculate average discount
            total_discount = sum(
                float(ticket.get('DiscountPercentage', 0)) 
                for ticket in all_tickets 
                if ticket.get('IsDiscounted', False)
            )
            
            avg_discount = total_discount / discounted_tickets if discounted_tickets > 0 else 0
            
            return {
                'totalTickets': total_tickets,
                'discountedTickets': discounted_tickets,
                'nonDiscountedTickets': total_tickets - discounted_tickets,
                'averageDiscountPercentage': round(avg_discount, 2),
                'discountedTicketPercentage': round(
                    (discounted_tickets / total_tickets * 100) if total_tickets > 0 else 0, 2
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting event processing stats: {e}")
            return {
                'error': str(e),
                'totalTickets': 0,
                'discountedTickets': 0,
                'nonDiscountedTickets': 0,
                'averageDiscountPercentage': 0,
                'discountedTicketPercentage': 0
            }
