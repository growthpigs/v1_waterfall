#!/bin/bash

# Brand BOS Comprehensive Test Suite
# Runs all tests for frontend and backend before deployment

echo "🧪 Brand BOS Test Suite"
echo "======================="
echo "Running comprehensive tests before deployment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test result tracking
FRONTEND_TESTS=0
BACKEND_TESTS=0
HEALTH_CHECKS=0

# Function to run tests and track results
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "\n${YELLOW}Running: $test_name${NC}"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        return 1
    fi
}

# 1. Frontend Tests
echo -e "\n${YELLOW}=== FRONTEND TESTS ===${NC}"
cd frontend

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Run frontend tests
run_test "Frontend Unit Tests" "npm run test"
FRONTEND_TESTS=$?

run_test "Frontend Type Check" "npm run type-check"
FRONTEND_TESTS=$((FRONTEND_TESTS + $?))

run_test "Frontend Lint Check" "npm run lint"
FRONTEND_TESTS=$((FRONTEND_TESTS + $?))

run_test "Frontend Format Check" "npm run format:check"
FRONTEND_TESTS=$((FRONTEND_TESTS + $?))

# Try to build frontend
run_test "Frontend Build Test" "npm run build"
FRONTEND_TESTS=$((FRONTEND_TESTS + $?))

cd ..

# 2. Backend Tests
echo -e "\n${YELLOW}=== BACKEND TESTS ===${NC}"

# Check if we have Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate 2>/dev/null || true
fi

# Run backend tests
run_test "Backend Unit Tests" "python -m pytest src/tests -v"
BACKEND_TESTS=$?

run_test "Backend Type Check" "python -m mypy src/"
BACKEND_TESTS=$((BACKEND_TESTS + $?))

run_test "Backend Lint Check" "python -m ruff src/"
BACKEND_TESTS=$((BACKEND_TESTS + $?))

run_test "Backend Format Check" "python -m black --check src/"
BACKEND_TESTS=$((BACKEND_TESTS + $?))

# 3. Docker Build Test
echo -e "\n${YELLOW}=== DOCKER BUILD TEST ===${NC}"
run_test "Docker Build" "docker build -t brand-bos-test . --quiet"
DOCKER_TEST=$?

# Clean up test image
docker rmi brand-bos-test 2>/dev/null || true

# 4. Health Checks
echo -e "\n${YELLOW}=== HEALTH CHECKS ===${NC}"
run_test "Deployment Readiness" "./scripts/check-deployment-ready.sh"
HEALTH_CHECKS=$?

# Summary
echo -e "\n${YELLOW}=== TEST SUMMARY ===${NC}"
echo "===================="

TOTAL_FAILURES=$((FRONTEND_TESTS + BACKEND_TESTS + DOCKER_TEST + HEALTH_CHECKS))

if [ $TOTAL_FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo "Your project is ready for deployment! 🚀"
    echo ""
    echo "Next steps:"
    echo "1. Run: python3 deploy.py"
    echo "2. Deploy frontend to Vercel"
    echo "3. Configure production environment"
else
    echo -e "${RED}❌ TESTS FAILED${NC}"
    echo ""
    echo "Failed test categories:"
    [ $FRONTEND_TESTS -ne 0 ] && echo "  - Frontend: $FRONTEND_TESTS failures"
    [ $BACKEND_TESTS -ne 0 ] && echo "  - Backend: $BACKEND_TESTS failures"
    [ $DOCKER_TEST -ne 0 ] && echo "  - Docker build: Failed"
    [ $HEALTH_CHECKS -ne 0 ] && echo "  - Health checks: Failed"
    echo ""
    echo "Please fix the failing tests before deployment."
fi

echo ""
echo "Test run completed at: $(date)"
echo "===================="

exit $TOTAL_FAILURES