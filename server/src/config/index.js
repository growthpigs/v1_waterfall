require('dotenv').config();

const config = {
  // Server configuration
  port: process.env.PORT || 5000,
  env: process.env.NODE_ENV || 'development',
  
  // MongoDB configuration
  mongoURI: process.env.MONGODB_URI || 'mongodb://localhost:27017/waterfall',
  
  // JWT configuration
  jwt: {
    secret: process.env.JWT_SECRET || 'waterfall-super-secret-key-change-in-production',
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
    refreshSecret: process.env.JWT_REFRESH_SECRET || 'waterfall-refresh-secret-key-change-in-production',
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '30d',
  },
  
  // OAuth / SSO configuration
  oauth: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackUrl: process.env.GOOGLE_CALLBACK_URL || '/api/auth/google/callback',
    },
    // Additional providers can be added here later (facebook, github, etc.)
  },
  
  // DataForSEO configuration
  dataForSEO: {
    login: process.env.DATAFORSEO_LOGIN,
    // NOTE: use the API password, **not** the web-interface login password
    password: process.env.DATAFORSEO_PASSWORD,
    baseUrl: process.env.DATAFORSEO_BASE_URL || 'https://api.dataforseo.com',
    useLiveData: process.env.DATAFORSEO_USE_LIVE_DATA === 'true' || false,
  },
  
  // Notion API configuration
  notion: {
    apiKey: process.env.NOTION_API_KEY,
    databaseId: process.env.NOTION_DATABASE_ID,
  },
  
  // Redis configuration (for caching)
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    enabled: process.env.REDIS_ENABLED === 'true' || false,
  },
  
  // File storage configuration
  storage: {
    type: process.env.STORAGE_TYPE || 'local', // 'local', 's3', etc.
    s3: {
      bucket: process.env.S3_BUCKET,
      region: process.env.S3_REGION || 'us-east-1',
      accessKeyId: process.env.S3_ACCESS_KEY_ID,
      secretAccessKey: process.env.S3_SECRET_ACCESS_KEY,
    },
    local: {
      path: process.env.LOCAL_STORAGE_PATH || 'uploads',
    },
  },
  
  // Logging configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'dev',
  },
  
  // Rate limiting configuration
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
    max: parseInt(process.env.RATE_LIMIT_MAX) || 100, // limit each IP to 100 requests per windowMs
  },
  
  // CORS configuration
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
    credentials: process.env.CORS_CREDENTIALS === 'true' || true,
  },
};

module.exports = config;
