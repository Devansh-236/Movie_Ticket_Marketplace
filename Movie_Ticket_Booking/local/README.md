# Movie Ticket Booking CRUD API - Serverless Framework with Event-Driven Architecture

This project implements a movie ticket booking CRUD API using the Serverless Framework, AWS Lambda, API Gateway, and DynamoDB with event-driven price change handling. It's designed to work alongside existing manual and CloudFormation-based implementations while using the same DynamoDB table.

## Architecture

- **AWS Lambda**: Serverless compute for handling API requests and events
- **API Gateway**: REST API endpoint management
- **DynamoDB**: NoSQL database for storing ticket bookings (uses existing `ticket-booking` table)
- **SNS**: Simple Notification Service for event publishing and handling
- **Serverless Framework**: Infrastructure as Code deployment

## Event-Driven Architecture

The system implements an event-driven architecture specifically for price changes:

1. **Price Update Trigger**: When a ticket price is updated via PATCH `/ticket`, an event is published
2. **Event Processing**: A dedicated Lambda function processes the price change event
3. **Metadata Update**: The event handler adds price change metadata to the same ticket
4. **Completion Event**: After processing, a completion event is published

### Event Flow

```
User Updates Price → PATCH Handler → Publishes "PriceChangeInitiated" Event
                                  ↓
Event Handler Processes → Updates Ticket Metadata → Publishes "PriceChangeProcessed" Event
```

## Project Structure

```
movie-booking-serverless-api/
├── serverless.yml              # Serverless Framework configuration with SNS
├── package.json               # Node.js dependencies and scripts
├── requirements.txt           # Python dependencies
├── handlers/                  # Lambda function handlers
│   ├── get_handler.py        # GET operations (retrieveMovies, retrieveTicket, retrieveAllTickets)
│   ├── post_handler.py       # POST operations (createTicket)
│   ├── patch_handler.py      # PATCH operations (updateTicket) with event publishing
│   ├── delete_handler.py     # DELETE operations (removeTicket)
│   └── event_handler.py      # Event processing for price changes
└── utils/                    # Utility modules
    ├── encoder.py           # Custom JSON encoder for DynamoDB
    └── response.py          # Standardized API response builder
```

## API Endpoints

| Method | Endpoint | Function | Description |
|--------|----------|----------|-------------|
| GET | `/movies` | `retrieveMovies` | Get all unique movies |
| GET | `/ticket?Theatre-Seat=<id>` | `retrieveTicket` | Get specific ticket by ID |
| GET | `/tickets` | `retrieveAllTickets` | Get all tickets |
| POST | `/ticket` | `createTicket` | Create new ticket |
| PATCH | `/ticket` | `updateTicket` | Update existing ticket (triggers events for price changes) |
| DELETE | `/ticket` | `removeTicket` | Delete ticket |

## Event Processing

### Price Change Events

When updating a ticket's price using the PATCH endpoint, the system:

1. **Publishes Initial Event**: `PriceChangeInitiated` event with:
   - Theatre seat ID
   - Movie name
   - Old and new price values
   - Timestamp

2. **Processes Event**: Event handler adds metadata:
   - `LastPriceChangeTimestamp`
   - `PreviousPrice`
   - `DiscountPercentage` (if price decreased)
   - `IsDiscounted` (boolean flag)

3. **Publishes Completion Event**: `PriceChangeProcessed` event indicating processing is complete

### Event Handler Function

The `priceChangeEventHandler` function:
- Listens to SNS topic for price change events
- Processes `PriceChangeInitiated` events
- Updates the ticket with additional metadata
- Publishes `PriceChangeProcessed` completion events
- Avoids infinite loops by only processing initial events

## Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **Node.js** (v16 or later)
3. **Python** (3.12)
4. **Serverless Framework CLI**

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Serverless Framework globally (if not installed)
npm install -g serverless
```

### 2. Configure AWS Credentials

```bash
# Configure AWS CLI if not already done
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Deploy the Stack

```bash
# Deploy to development stage
npm run deploy-dev

# Deploy to production stage
npm run deploy-prod

# Or use serverless directly
serverless deploy --stage dev
```

### 4. Test the Event-Driven Price Changes

After deployment, test the price change functionality:

```bash
# Create a ticket first
curl -X POST https://your-api-id.execute-api.region.amazonaws.com/dev/ticket \
  -H "Content-Type: application/json" \
  -d '{"Theatre-Seat": "1-A9", "Movie": "Avengers", "Price": 15.99}'

# Update the price (this will trigger events)
curl -X PATCH https://your-api-id.execute-api.region.amazonaws.com/dev/ticket \
  -H "Content-Type: application/json" \
  -d '{"Theatre-Seat": "1-A9", "updateKey": "Price", "updateValue": 12.99}'

# Check the updated ticket to see added metadata
curl "https://your-api-id.execute-api.region.amazonaws.com/dev/ticket?Theatre-Seat=1-A9"
```

## Environment Configuration

The application supports multiple stages with SNS topic isolation:

```bash
# Deploy to different stages (each gets its own SNS topic)
serverless deploy --stage dev
serverless deploy --stage prod --region us-west-2
```

## Function Names

This implementation includes all original functions plus:

- `priceChangeEventHandler` - Processes price change events from SNS

## Database Schema

The application uses the existing `ticket-booking` DynamoDB table with additional fields added by the event handler:

- **Primary Key**: `Theatre-Seat` (String)
- **Original Attributes**: `Movie`, `Price`, and other ticket-related fields
- **Event-Added Attributes**:
  - `LastPriceChangeTimestamp` - ISO timestamp of last price change
  - `PreviousPrice` - Previous price value before the change
  - `DiscountPercentage` - Calculated discount percentage (if applicable)
  - `IsDiscounted` - Boolean indicating if ticket is currently discounted

## Development Commands

```bash
# View logs for the event handler
serverless logs -f priceChangeEventHandler --tail

# View logs for patch handler
serverless logs -f updateTicket --tail

# Invoke event handler locally with test event
serverless invoke local -f priceChangeEventHandler -d '{
  "Records": [{
    "EventSource": "aws:sns",
    "Sns": {
      "Message": "{\"eventType\":\"PriceChangeInitiated\",\"theatreSeat\":\"1-A9\",\"movie\":\"Test Movie\",\"oldPrice\":15.99,\"newPrice\":12.99}"
    }
  }]
}'

# Remove the entire stack
serverless remove
```

## Error Handling

Enhanced error handling includes:
- Event publishing failure handling (operations continue even if events fail)
- SNS message parsing validation
- Event loop prevention (only processes initial price change events)
- Comprehensive logging for event processing

## Event Monitoring

Monitor events through:
- **CloudWatch Logs**: View Lambda function logs for event processing
- **SNS Metrics**: Monitor message publishing and delivery
- **DynamoDB Metrics**: Track read/write operations

## Security Considerations

Additional security measures:
- **SNS Permissions**: Functions have minimal required permissions for SNS operations
- **Event Validation**: All event messages are validated before processing
- **Event Loop Prevention**: Built-in safeguards against infinite event loops

## Cost Optimization

Event-driven architecture considerations:
- SNS pay-per-message pricing
- Lambda invocations for event processing
- Optimized event payloads to minimize costs

## Cleanup

To remove all resources including SNS topics:

```bash
serverless remove --stage dev
```

This will delete all Lambda functions, API Gateway, SNS topics, and associated IAM roles, but will preserve the existing DynamoDB table.

## Event Flow Example

1. **User updates price**: PATCH `/ticket` with price change
2. **System publishes event**: `PriceChangeInitiated` event to SNS
3. **Event handler processes**: Adds metadata to the same ticket
4. **System publishes completion**: `PriceChangeProcessed` event
5. **Logging**: All events are logged for monitoring and debugging