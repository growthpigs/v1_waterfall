#!/bin/bash

# Brand BOS Deployment Readiness Checker
# This script verifies your project is ready for deployment to Render

echo "🚀 Brand BOS Deployment Readiness Check"
echo "======================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Function to check command exists
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $2"
        WARNINGS=$((WARNINGS + 1))
        return 1
    fi
}

echo "📁 Checking Required Files..."
echo "----------------------------"
check_file "Dockerfile" "Dockerfile exists"
check_file "docker-compose.yml" "docker-compose.yml exists"
check_file "render.yaml" "render.yaml exists"
check_file "requirements.txt" "requirements.txt exists"
check_file ".env.example" ".env.example exists"
check_file "scripts/start.sh" "Startup script exists"
echo ""

echo "📂 Checking Project Structure..."
echo "-------------------------------"
check_dir "src" "Backend source directory exists"
check_dir "frontend" "Frontend directory exists"
check_dir "scripts" "Scripts directory exists"
check_dir "src/database/migrations" "Database migrations exist"
echo ""

echo "🔧 Checking Local Tools..."
echo "-------------------------"
check_command "docker" "Docker installed"
check_command "git" "Git installed"
check_command "node" "Node.js installed"
check_command "python3" "Python 3 installed"
echo ""

echo "🐳 Testing Docker Build..."
echo "-------------------------"
if command -v docker &> /dev/null; then
    echo "Building Docker image (this may take a moment)..."
    if docker build -t brand-bos-test . > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Docker build successful"
        docker rmi brand-bos-test > /dev/null 2>&1
    else
        echo -e "${RED}✗${NC} Docker build failed"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠${NC} Skipping Docker build test (Docker not installed)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

echo "🔍 Checking Environment Configuration..."
echo "--------------------------------------"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    
    # Check for required variables
    REQUIRED_VARS=(
        "SUPABASE_URL"
        "SUPABASE_ANON_KEY"
        "ANTHROPIC_API_KEY"
        "SECRET_KEY"
    )
    
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${var}=" .env && ! grep -q "^${var}=your" .env; then
            echo -e "${GREEN}✓${NC} ${var} is set"
        else
            echo -e "${YELLOW}⚠${NC} ${var} needs to be configured"
            WARNINGS=$((WARNINGS + 1))
        fi
    done
else
    echo -e "${YELLOW}⚠${NC} .env file not found (create from .env.example)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

echo "📦 Checking Frontend Build..."
echo "----------------------------"
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "package.json" ]; then
        echo -e "${GREEN}✓${NC} Frontend package.json exists"
        
        # Check if node_modules exists
        if [ -d "node_modules" ]; then
            echo -e "${GREEN}✓${NC} Frontend dependencies installed"
        else
            echo -e "${YELLOW}⚠${NC} Frontend dependencies not installed (run: cd frontend && npm install)"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
    cd ..
fi
echo ""

echo "🚦 Checking Git Status..."
echo "------------------------"
if [ -d ".git" ]; then
    # Check if there are uncommitted changes
    if git diff-index --quiet HEAD --; then
        echo -e "${GREEN}✓${NC} No uncommitted changes"
    else
        echo -e "${YELLOW}⚠${NC} You have uncommitted changes"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Check current branch
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo -e "${GREEN}✓${NC} Current branch: $BRANCH"
else
    echo -e "${RED}✗${NC} Not a git repository"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "📊 Summary"
echo "----------"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Your project is ready for deployment.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Push your code to GitHub"
    echo "2. Connect your repository to Render"
    echo "3. Configure environment variables in Render dashboard"
    echo "4. Deploy!"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found. You can deploy, but review the warnings.${NC}"
else
    echo -e "${RED}❌ $ERRORS error(s) and $WARNINGS warning(s) found. Fix errors before deploying.${NC}"
fi
echo ""

exit $ERRORS