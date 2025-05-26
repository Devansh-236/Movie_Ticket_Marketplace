#!/bin/bash

echo "🚀 Setting up Movie Booking Serverless API with LocalStack..."

# Check if Python 3.11 is installed
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 is required but not installed."
    echo "Please install Python 3.11 and try again."
    exit 1
fi

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3.11 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Install AWS CLI Local (awslocal)
echo "🔧 Installing AWS CLI Local..."
pip install awscli-local

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p volume
mkdir -p .localstack

# Make scripts executable
chmod +x localstack-setup.sh

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start LocalStack: npm run localstack-start"
echo "3. Setup LocalStack resources: npm run localstack-setup"
echo "4. Deploy the application: npm run deploy-local"
