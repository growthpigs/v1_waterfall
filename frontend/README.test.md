# Testing Guide for Brand BOS Dashboard

## 🚀 Quick Start

### Run All Tests
```bash
npm test
```

### Run Tests in Watch Mode
```bash
npm run test:watch
```

### Run Critical Tests Only (Fast)
```bash
npm run test:critical
```

### View Test Coverage
```bash
npm run test:coverage
```

### Interactive Test UI
```bash
npm run test:ui
```

## 🎯 What's Being Tested

### Critical Infrastructure (118 tests)
- **API Client** - All server communication
- **PageLayout** - UI structure wrapper
- **ErrorBoundary** - Crash prevention
- **SidebarNavigation** - Main navigation
- **FloatingChatBar** - User interaction

### Test Coverage Goals
- Critical paths: 90%+ coverage
- Shared components: 80%+ coverage
- Business logic: 70%+ coverage
- Overall: 70%+ coverage

## 🔧 Automated Testing

### Pre-commit Hook
Automatically runs before each commit:
1. Linting checks
2. Critical component tests

### Pre-build Hook
Runs critical tests before building to ensure stability.

### GitHub Actions
On every push/PR:
1. Linting
2. Type checking
3. Full test suite
4. Coverage reporting
5. Build verification

## 📝 Writing New Tests

### Test File Naming
```
ComponentName.test.tsx  # For components
serviceName.test.ts     # For services
```

### Basic Test Structure
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import YourComponent from './YourComponent'

describe('YourComponent', () => {
  it('should render correctly', () => {
    render(<YourComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })
})
```

### Testing Best Practices
1. **Test behavior, not implementation**
2. **Use data-testid for reliable element selection**
3. **Mock external dependencies**
4. **Test error states and edge cases**
5. **Keep tests simple and focused**

## 🏃 Running Tests by Category

### Component Tests
```bash
npm test src/components
```

### Service Tests
```bash
npm test src/services
```

### Specific File
```bash
npm test src/components/shared/PageLayout.test.tsx
```

## 🐛 Debugging Tests

### Run Single Test
```typescript
it.only('should do something', () => {
  // This test runs in isolation
})
```

### Skip Test
```typescript
it.skip('should do something', () => {
  // This test is skipped
})
```

### Debug in VS Code
1. Install "Vitest" extension
2. Click on test CodeLens to debug
3. Set breakpoints as needed

## 📊 Coverage Reports

After running `npm run test:coverage`:
- **Console**: Summary in terminal
- **HTML**: Open `coverage/index.html` in browser
- **JSON**: `coverage/coverage-final.json` for CI

## 🚨 Common Issues

### "Cannot find module" Error
```bash
npm install
```

### Test Timeout
Increase timeout for async operations:
```typescript
it('should fetch data', async () => {
  // test code
}, 10000) // 10 second timeout
```

### Mock Not Working
Ensure mocks are defined before imports:
```typescript
vi.mock('axios')
import axios from 'axios'
```

## 🎉 Test Status

| Component | Tests | Coverage | Status |
|-----------|-------|----------|---------|
| API Client | 29 | 95% | ✅ |
| PageLayout | 24 | 100% | ✅ |
| ErrorBoundary | 20 | 100% | ✅ |
| SidebarNavigation | 25 | 100% | ✅ |
| FloatingChatBar | 20 | 90% | ✅ |

Total: **118 tests** protecting your critical components!

## 🔗 Useful Commands

```bash
# Run all checks before pushing
npm run check-all

# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Type checking
npm run type-check
```

Remember: **Tests are your safety net!** 🛡️