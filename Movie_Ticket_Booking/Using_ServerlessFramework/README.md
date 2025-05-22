# Movie Ticket Booking CRUD API - Serverless Framework

This project implements a movie ticket booking CRUD API using the Serverless Framework, AWS Lambda, API Gateway, and DynamoDB. It's designed to work alongside existing manual and CloudFormation-based implementations while using the same DynamoDB table.

## Architecture

- **AWS Lambda**: Serverless compute for handling API requests
- **API Gateway**: REST API endpoint management
- **DynamoDB**: NoSQL database for storing ticket bookings (uses existing `ticket-booking` table)
- **Serverless Framework**: Infrastructure as Code deployment

## Project Structure

```
movie-booking-serverless-api/
├── serverless.yml              # Serverless Framework configuration
├── package.json               # Node.js dependencies and scripts
├── requirements.txt           # Python dependencies
├── handlers/                  # Lambda function handlers
│   ├── get_handler.py        # GET operations (retrieveMovies, retrieveTicket, retrieveAllTickets)
│   ├── post_handler.py       # POST operations (createTicket)
│   ├── patch_handler.py      # PATCH operations (updateTicket)
│   └── delete_handler.py     # DELETE operations (removeTicket)
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
| PATCH | `/ticket` | `updateTicket` | Update existing ticket |
| DELETE | `/ticket` | `removeTicket` | Delete ticket |

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

### 4. Test the API

After deployment, you'll receive an API Gateway URL. Test the endpoints:

```bash
# Get all movies
curl https://your-api-id.execute-api.region.amazonaws.com/dev/movies

# Create a ticket
curl -X POST https://your-api-id.execute-api.region.amazonaws.com/dev/ticket \
  -H "Content-Type: application/json" \
  -d '{"Theatre-Seat": "1-A9", "Movie": "Avengers", "Price": 15.99}'

# Get specific ticket
curl "https://your-api-id.execute-api.region.amazonaws.com/dev/ticket?Theatre-Seat=1-A9"

# Update ticket
curl -X PATCH https://your-api-id.execute-api.region.amazonaws.com/dev/ticket \
  -H "Content-Type: application/json" \
  -d '{"Theatre-Seat": "1-A9", "updateKey": "Price", "updateValue": 18.99}'

# Delete ticket
curl -X DELETE https://your-api-id.execute-api.region.amazonaws.com/dev/ticket \
  -H "Content-Type: application/json" \
  -d '{"Theatre-Seat": "1-A9"}'
```

## Environment Configuration

The application supports multiple stages (dev, prod, etc.):

```bash
# Deploy to different stages
serverless deploy --stage dev
serverless deploy --stage prod --region us-west-2
```

## Function Names

This implementation uses different function names from the original CloudFormation setup:

- `retrieveMovies` (instead of `GetMoviesFunction`)
- `retrieveTicket` (instead of `GetTicket`)
- `retrieveAllTickets` (instead of `GetTickets`)
- `createTicket` (instead of `PostTicketFunction`)
- `updateTicket` (instead of `PatchTicketFunction`)
- `removeTicket` (instead of `DeleteTicketFunction`)

## Database Schema

The application uses the existing `ticket-booking` DynamoDB table with:

- **Primary Key**: `Theatre-Seat` (String)
- **Attributes**: `Movie`, `Price`, and any other ticket-related fields

## Development Commands

```bash
# View logs for a specific function
serverless logs -f createTicket --tail

# Invoke function locally
serverless invoke local -f createTicket -d '{"body": "{\"Theatre-Seat\":\"1-A9\",\"Movie\":\"Test Movie\"}"}'

# Remove the entire stack
serverless remove
```

## Error Handling

The application includes comprehensive error handling:

- Input validation for required fields
- JSON parsing error handling
- DynamoDB operation error handling
- Standardized error responses with appropriate HTTP status codes

## CORS Configuration

CORS is enabled for all endpoints to allow cross-origin requests from web applications.

## Security Considerations

1. **IAM Roles**: Functions have minimal required permissions for DynamoDB operations
2. **Input Validation**: All inputs are validated before processing
3. **Error Messages**: Generic error messages to avoid information disclosure

## Monitoring and Logging

- CloudWatch logs are automatically created for each function
- Structured logging with appropriate log levels
- Request/response logging for debugging

## Cost Optimization

- Pay-per-request billing for DynamoDB
- Lambda functions with appropriate timeout settings
- Efficient DynamoDB queries to minimize read/write units

## Cleanup

To remove all resources:

```bash
serverless remove --stage dev
```

This will delete all Lambda functions, API Gateway, and associated IAM roles, but will preserve the existing DynamoDB table.