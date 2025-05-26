#!/bin/bash

echo "🔧 Setting up LocalStack resources..."

# Wait for LocalStack to be ready
echo "⏳ Waiting for LocalStack to be ready..."
while ! curl -s http://localhost:4566/_localstack/health | grep -q '"dynamodb": "available"'; do
    echo "Waiting for LocalStack..."
    sleep 2
done

echo "✅ LocalStack is ready!"

# Create DynamoDB table
echo "📊 Creating DynamoDB table..."
awslocal dynamodb create-table \
    --table-name ticket-booking \
    --attribute-definitions \
        AttributeName=Theatre-Seat,AttributeType=S \
    --key-schema \
        AttributeName=Theatre-Seat,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-1

# Wait for table to be active
echo "⏳ Waiting for table to be active..."
awslocal dynamodb wait table-exists --table-name ticket-booking --region us-east-1

echo "✅ DynamoDB table created successfully!"

# List tables to verify
echo "📋 Verifying table creation..."
awslocal dynamodb list-tables --region us-east-1

echo "🎉 LocalStack setup complete!"
