#!/bin/bash

# Agentic Honey-Pot Deployment Helper Script

echo "=================================="
echo "Agentic Honey-Pot Deployment Helper"
echo "=================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python installation
echo "🔍 Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION found"
else
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check pip installation
echo "🔍 Checking pip installation..."
if command_exists pip3 || command_exists pip; then
    echo "✅ pip found"
else
    echo "❌ pip not found. Please install pip."
    exit 1
fi

echo ""
echo "Choose deployment option:"
echo "1) Local Development"
echo "2) Docker Deployment"
echo "3) Heroku Deployment"
echo "4) Render Deployment"
echo "5) Test API"
echo "6) Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "📦 Setting up local development environment..."
        
        # Install dependencies
        echo "Installing dependencies..."
        pip3 install -r requirements.txt
        
        # Create .env file if not exists
        if [ ! -f .env ]; then
            echo "Creating .env file..."
            cp .env.example .env
            echo "⚠️  Please edit .env file and set your API_SECRET_KEY"
        fi
        
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "To start the server, run:"
        echo "  python3 honeypot_api.py"
        echo ""
        echo "Or with uvicorn:"
        echo "  uvicorn honeypot_api:app --reload --host 0.0.0.0 --port 8000"
        ;;
        
    2)
        echo ""
        echo "🐳 Docker Deployment..."
        
        if ! command_exists docker; then
            echo "❌ Docker not found. Please install Docker."
            exit 1
        fi
        
        echo "Building Docker image..."
        docker build -t honeypot-api .
        
        read -p "Enter your API_SECRET_KEY: " api_key
        
        echo "Starting container..."
        docker run -d -p 8000:8000 -e API_SECRET_KEY="$api_key" --name honeypot-api honeypot-api
        
        echo ""
        echo "✅ Docker container started!"
        echo "API running at: http://localhost:8000"
        echo ""
        echo "To view logs: docker logs honeypot-api"
        echo "To stop: docker stop honeypot-api"
        echo "To remove: docker rm honeypot-api"
        ;;
        
    3)
        echo ""
        echo "🚀 Heroku Deployment..."
        
        if ! command_exists heroku; then
            echo "❌ Heroku CLI not found."
            echo "Install from: https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi
        
        read -p "Enter your app name: " app_name
        read -p "Enter your API_SECRET_KEY: " api_key
        
        echo "Creating Heroku app..."
        heroku create "$app_name"
        
        echo "Setting environment variables..."
        heroku config:set API_SECRET_KEY="$api_key" -a "$app_name"
        
        echo "Deploying to Heroku..."
        git push heroku main
        
        echo ""
        echo "✅ Deployment complete!"
        echo "Your API: https://$app_name.herokuapp.com/detect"
        ;;
        
    4)
        echo ""
        echo "🎨 Render Deployment Instructions..."
        echo ""
        echo "1. Go to https://render.com and sign in"
        echo "2. Click 'New' → 'Web Service'"
        echo "3. Connect your GitHub repository"
        echo "4. Configure:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: uvicorn honeypot_api:app --host 0.0.0.0 --port \$PORT"
        echo "5. Add environment variable:"
        echo "   - Key: API_SECRET_KEY"
        echo "   - Value: your-secret-key"
        echo "6. Click 'Create Web Service'"
        echo ""
        echo "Your API will be at: https://your-app-name.onrender.com/detect"
        ;;
        
    5)
        echo ""
        echo "🧪 Testing API..."
        
        read -p "Enter API URL (default: http://localhost:8000): " api_url
        api_url=${api_url:-http://localhost:8000}
        
        read -p "Enter API Key: " api_key
        
        echo ""
        echo "Testing health endpoint..."
        curl -s "$api_url/health" | python3 -m json.tool
        
        echo ""
        echo "Testing scam detection..."
        curl -s -X POST "$api_url/detect" \
          -H "Content-Type: application/json" \
          -H "x-api-key: $api_key" \
          -d '{
            "sessionId": "test-001",
            "message": {
              "sender": "scammer",
              "text": "Your bank account will be blocked. Verify immediately.",
              "timestamp": 1770005528731
            },
            "conversationHistory": [],
            "metadata": {
              "channel": "SMS",
              "language": "English",
              "locale": "IN"
            }
          }' | python3 -m json.tool
        
        echo ""
        echo "✅ Test complete!"
        ;;
        
    6)
        echo "Goodbye!"
        exit 0
        ;;
        
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "=================================="
echo "Deployment helper finished!"
echo "=================================="