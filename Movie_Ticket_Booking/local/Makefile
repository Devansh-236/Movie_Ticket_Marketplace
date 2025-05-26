.PHONY: help setup start stop deploy test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Setup the development environment
	./setup.sh

start: ## Start LocalStack
	docker-compose up -d
	@echo "Waiting for LocalStack to start..."
	@sleep 10
	./localstack-setup.sh

stop: ## Stop LocalStack
	docker-compose down

deploy: ## Deploy to LocalStack
	source venv/bin/activate && serverless deploy --stage local

remove: ## Remove deployment from LocalStack
	source venv/bin/activate && serverless remove --stage local

test: ## Test the API endpoints
	@echo "Testing API endpoints..."
	@echo "Creating a ticket..."
	curl -X POST http://localhost:4566/restapis/*/local/_user_request_/ticket \
		-H "Content-Type: application/json" \
		-d '{"Theatre-Seat": "1-A7", "Movie": "Test Movie", "Price": 159}'
	@echo ""
	@echo "Getting all tickets..."
	curl http://localhost:4566/restapis/*/local/_user_request_/tickets

clean: ## Clean up all resources
	make stop
	docker system prune -f
	rm -rf volume/
	rm -rf .serverless/
	rm -rf node_modules/
	rm -rf venv/

logs: ## Show LocalStack logs
	docker-compose logs -f localstack

status: ## Check LocalStack status
	curl -s http://localhost:4566/_localstack/health | python3 -m json.tool
