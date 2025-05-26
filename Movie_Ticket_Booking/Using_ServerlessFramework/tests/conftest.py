import pytest
import boto3
import os
from moto import mock_dynamodb, mock_sns, mock_sqs
from fastapi.testclient import TestClient
from decimal import Decimal
import json
from unittest.mock import patch, MagicMock

# Set test environment variables
os.environ['DYNAMODB_TABLE'] = 'test-ticket-booking'
os.environ['PRICE_CHANGE_TOPIC_ARN'] = 'arn:aws:sns:us-east-1:123456789012:test-price-change-topic'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'

@pytest.fixture(scope="session")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def mock_dynamodb_table():
    """Create a mock DynamoDB table for testing."""
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Create table
        table = dynamodb.create_table(
            TableName='test-ticket-booking',
            KeySchema=[
                {
                    'AttributeName': 'Theatre-Seat',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'Theatre-Seat',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        
        yield table

@pytest.fixture
def mock_sns_topic():
    """Create a mock SNS topic for testing."""
    with mock_sns():
        sns = boto3.client('sns', region_name='us-east-1')
        
        # Create topic
        response = sns.create_topic(Name='test-price-change-topic')
        topic_arn = response['TopicArn']
        
        yield topic_arn

@pytest.fixture
def mock_sqs_queue():
    """Create a mock SQS queue for testing."""
    with mock_sqs():
        sqs = boto3.client('sqs', region_name='us-east-1')
        
        # Create queue
        response = sqs.create_queue(QueueName='test-price-change-queue')
        queue_url = response['QueueUrl']
        
        yield queue_url

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from app import app
    return TestClient(app)

@pytest.fixture
def sample_ticket_data():
    """Sample ticket data for testing."""
    return {
        'Theatre-Seat': '1-A9',
        'Movie': 'Avengers',
        'Price': Decimal('15.99')
    }

@pytest.fixture
def sample_tickets_data():
    """Sample multiple tickets data for testing."""
    return [
        {
            'Theatre-Seat': '1-A9',
            'Movie': 'Avengers',
            'Price': Decimal('15.99')
        },
        {
            'Theatre-Seat': '1-B5',
            'Movie': 'Spider-Man',
            'Price': Decimal('12.50')
        },
        {
            'Theatre-Seat': '2-C3',
            'Movie': 'Avengers',
            'Price': Decimal('18.00')
        }
    ]

@pytest.fixture
def mock_table_with_data(mock_dynamodb_table, sample_tickets_data):
    """Mock DynamoDB table with sample data."""
    for ticket in sample_tickets_data:
        mock_dynamodb_table.put_item(Item=ticket)
    return mock_dynamodb_table
