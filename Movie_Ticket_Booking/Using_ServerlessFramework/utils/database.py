import boto3
import os

def get_table():
    """Get DynamoDB table instance"""
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get('DYNAMODB_TABLE', 'ticket-booking')
    return dynamodb.Table(table_name)
