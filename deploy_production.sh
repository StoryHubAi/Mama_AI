#!/bin/bash

# MAMA-AI Production Deployment Script
# Run this script to prepare and deploy to production

echo "🚀 MAMA-AI Production Deployment Preparation"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: app.py not found. Please run this script from the MAMA-AI directory.${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Pre-deployment checklist:${NC}"

# Check for required files
echo -e "Checking required files..."
files=("app.py" "requirements.txt" "Procfile" ".env.production" "runtime.txt")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ✅ $file"
    else
        echo -e "  ❌ $file ${RED}(missing)${NC}"
    fi
done

# Check Python version
echo -e "\nChecking Python version..."
python_version=$(python --version 2>&1)
echo -e "  📍 $python_version"

# Check dependencies
echo -e "\nChecking dependencies..."
if pip freeze > /dev/null 2>&1; then
    echo -e "  ✅ Dependencies accessible"
else
    echo -e "  ❌ ${RED}Dependencies check failed${NC}"
fi

# Environment check
echo -e "\n${YELLOW}⚙️  Environment Configuration:${NC}"
if [ -f ".env" ]; then
    echo -e "  📄 .env file exists"
    
    # Check for placeholder values
    if grep -q "your_.*_here" .env; then
        echo -e "  ⚠️  ${YELLOW}Warning: Found placeholder values in .env${NC}"
        echo -e "    Please update API keys before deployment"
    fi
    
    # Check for production settings
    if grep -q "FLASK_ENV=production" .env; then
        echo -e "  ✅ Production environment configured"
    else
        echo -e "  ⚠️  ${YELLOW}Consider setting FLASK_ENV=production${NC}"
    fi
else
    echo -e "  ⚠️  ${YELLOW}.env file not found. Copy from .env.production${NC}"
fi

# Test local application
echo -e "\n${BLUE}🧪 Testing local application:${NC}"
echo -e "Starting quick health check..."

# Start app in background for testing
python app.py &
APP_PID=$!
sleep 5

# Test health endpoint
if curl -s http://localhost:5000/health > /dev/null; then
    echo -e "  ✅ Application starts successfully"
    
    # Run production tests
    echo -e "  🔬 Running production tests..."
    python production_test.py --quick --url http://localhost:5000
else
    echo -e "  ❌ ${RED}Application failed to start${NC}"
fi

# Cleanup
kill $APP_PID 2>/dev/null
wait $APP_PID 2>/dev/null

# Git status
echo -e "\n${BLUE}📂 Git Status:${NC}"
if git status > /dev/null 2>&1; then
    uncommitted=$(git status --porcelain | wc -l)
    if [ $uncommitted -eq 0 ]; then
        echo -e "  ✅ All changes committed"
    else
        echo -e "  ⚠️  ${YELLOW}$uncommitted uncommitted changes${NC}"
        echo -e "    Run: git add . && git commit -m 'Production ready'"
    fi
    
    current_branch=$(git branch --show-current)
    echo -e "  📍 Current branch: $current_branch"
else
    echo -e "  ❌ ${RED}Not a git repository${NC}"
fi

# Heroku deployment steps
echo -e "\n${GREEN}🌐 Heroku Deployment Steps:${NC}"
echo -e "1. Ensure you have Heroku CLI installed"
echo -e "2. Login to Heroku: ${BLUE}heroku login${NC}"
echo -e "3. Create app: ${BLUE}heroku create mama-ai-health-assistant${NC}"
echo -e "4. Add PostgreSQL: ${BLUE}heroku addons:create heroku-postgresql:mini${NC}"
echo -e "5. Set environment variables:"
echo -e "   ${BLUE}heroku config:set FLASK_ENV=production${NC}"
echo -e "   ${BLUE}heroku config:set SECRET_KEY=your-secure-key${NC}"
echo -e "   ${BLUE}heroku config:set AFRICASTALKING_USERNAME=your-username${NC}"
echo -e "   ${BLUE}heroku config:set AFRICASTALKING_API_KEY=your-api-key${NC}"
echo -e "   ${BLUE}heroku config:set OPENAI_API_KEY=your-openai-key${NC}"
echo -e "6. Deploy: ${BLUE}git push heroku main${NC}"
echo -e "7. Check logs: ${BLUE}heroku logs --tail${NC}"

# Security reminders
echo -e "\n${YELLOW}🔒 Security Checklist:${NC}"
echo -e "  📋 Update all API keys to production values"
echo -e "  📋 Set strong SECRET_KEY (minimum 32 characters)"
echo -e "  📋 Never commit real API keys to git"
echo -e "  📋 Use PostgreSQL for production database"
echo -e "  📋 Enable HTTPS in production"

# Post-deployment tasks
echo -e "\n${BLUE}📋 Post-Deployment Tasks:${NC}"
echo -e "  📋 Configure Africa's Talking webhooks"
echo -e "  📋 Test SMS functionality"
echo -e "  📋 Verify AI responses"
echo -e "  📋 Monitor application logs"
echo -e "  📋 Set up monitoring and alerts"

echo -e "\n${GREEN}✨ Your MAMA-AI system is ready for production deployment!${NC}"
echo -e "Follow the steps above to deploy to Heroku."
echo -e "\nFor detailed instructions, see: ${BLUE}PRODUCTION_DEPLOYMENT.md${NC}"

# Quick deployment command
echo -e "\n${BLUE}🚀 Quick Deploy Command:${NC}"
echo -e "After setting up Heroku app and environment variables:"
echo -e "${GREEN}git add . && git commit -m 'Production deployment' && git push heroku main${NC}"
