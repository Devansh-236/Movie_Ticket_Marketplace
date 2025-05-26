import boto3
import json
import os
import logging
from typing import Dict, Any
from utils.encoder import CustomEncoder

logger = logging.getLogger(__name__)

class SNSService:
    def __init__(self):
        self.sns = boto3.client(
            'sns',
            endpoint_url=os.environ.get('AWS_ENDPOINT_URL', 'http://localhost:4566'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'test'),
            region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        )
        self.topic_arn = os.environ.get('PRICE_CHANGE_TOPIC_ARN')

    def publish_price_change_event(self, event_data: Dict[str, Any]) -> bool:
        """Publish price change event to SNS topic"""
        try:
            if not self.topic_arn:
                logger.warning("PRICE_CHANGE_TOPIC_ARN not configured")
                return False

            self.sns.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(event_data, cls=CustomEncoder),
                Subject=f'Price Change Event for {event_data.get("theatreSeat")}'
            )
            
            logger.info(f"Published price change event for {event_data.get('theatreSeat')}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish price change event: {e}")
            return False
