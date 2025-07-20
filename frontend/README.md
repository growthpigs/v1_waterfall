# Brand BOS Dashboard

## Overview
React/TypeScript dashboard for the Brand BOS platform, implementing the Authority Avalanche methodology for professional services.

## Phase 1 Integration Guide

### Prerequisites
- Node.js >= 18.0.0
- npm >= 9.0.0
- Backend API running on http://localhost:8000

### Environment Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Configure environment variables:
```env
VITE_API_URL=http://localhost:8000
VITE_GHL_API_KEY=your_ghl_api_key_here
VITE_GOOGLE_ADS_CLIENT_ID=your_google_ads_client_id_here
```

### API Integration

#### 1. Internal Backend API
The main API client is configured in `src/lib/api.ts`:
- Automatic JWT authentication from localStorage
- Comprehensive error handling
- User-friendly error messages

```typescript
import api from '@/lib/api';

// Example usage
const response = await api.get('/cia/analysis');
```

#### 2. GHL (GoHighLevel) Integration
Located in `src/services/ghlService.ts`:

**Authentication:**
```typescript
import { ghlService } from '@/services/ghlService';

// Store API key
await ghlService.authenticateGHL('your-api-key');
```

**Publishing Content:**
```typescript
import { useGHLPost } from '@/services/ghlService';

const ghlPost = useGHLPost();

// Post to multiple platforms
await ghlPost.mutateAsync({
  platform: 'instagram',
  content: {
    text: 'Your content here',
    imageUrl: 'https://example.com/image.jpg', // optional
    scheduleDate: new Date('2024-01-20T10:00:00')
  }
});
```

**Available Platforms:**
- Instagram
- Twitter/X
- LinkedIn
- Facebook
- YouTube

**React Query Hooks:**
- `useGHLAuth()` - Authentication mutation
- `useGHLPost()` - Content posting mutation
- `useGHLSchedules()` - Fetch scheduled posts

#### 3. Google Ads Integration
Located in `src/services/googleAdsService.ts`:

**OAuth Setup:**
1. User authenticates with Google externally
2. Store access token:
```typescript
import { googleAdsService } from '@/services/googleAdsService';

googleAdsService.setAccessToken('access-token');
```

**Campaign Performance:**
```typescript
import { useGoogleAdsPerformance } from '@/services/googleAdsService';

const { data, isLoading } = useGoogleAdsPerformance();
// Returns metrics for 4 active campaigns
```

**Budget Rotation:**
```typescript
import { useRotateBudget } from '@/services/googleAdsService';

const rotateBudget = useRotateBudget();

await rotateBudget.mutateAsync({
  worstCampaignId: 'camp_001',
  newClusterId: 'AI Productivity Tools'
});
```

### UI Integration

#### Content Engine Page
The Content Engine page (`/content-engine`) now includes:
- GHL social publishing interface
- Platform selection checkboxes
- Content textarea with scheduling
- Upcoming scheduled posts preview

#### Performance Page
The Performance page (`/performance`) now displays:
- Google Ads $10k grant overview
- Campaign performance by cluster
- Budget utilization metrics
- Low performer alerts with rotation option

### Mock Data Toggle
Both GHL and Google Ads services use mock data by default. To switch to real APIs:

1. **GHL Service**: Update the service functions to use actual endpoints
2. **Google Ads Service**: Set `USE_MOCK_DATA = false` in `googleAdsService.ts`

### Testing

Run integration tests:
```bash
npm test src/test/api.test.tsx
```

### Development Workflow

1. Start the backend API:
```bash
cd ../backend
python -m uvserver
```

2. Start the dashboard:
```bash
npm run dev
```

3. Access at http://localhost:3000

### React Query DevTools
In development, React Query DevTools are available at the bottom of the screen for debugging data fetching.

### Error Handling
All API errors are handled gracefully with user-friendly messages:
- 401: Redirects to login (implement login flow)
- 403: Permission denied message
- 404: Resource not found
- 500: Server error with retry
- Network errors: Connection error message

### Next Steps
1. Implement real GHL MCP endpoints when available
2. Complete Google OAuth flow integration
3. Add file upload for image content
4. Implement real-time updates with WebSockets
5. Add comprehensive error tracking (Sentry)

## Tech Stack
- React 18 + TypeScript
- Vite
- React Query (TanStack Query v4)
- Axios
- Zod (validation)
- Tailwind CSS
- Framer Motion
- Lucide Icons

## Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm test` - Run tests
- `npm run lint` - Lint code
- `npm run type-check` - Type check