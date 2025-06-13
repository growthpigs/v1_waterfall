require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const session = require('express-session');
const passport = require('passport');
const xss = require('xss-clean');
const rateLimit = require('express-rate-limit');
const path = require('path');

// Import configuration
const config = require('./config');

// Import routes (to be created)
const authRoutes = require('./api/routes/auth.routes');
const userRoutes = require('./api/routes/user.routes');
const ciaRoutes = require('./api/routes/cia.routes');
const cartwheelRoutes = require('./api/routes/cartwheel.routes');
const dataForSEORoutes = require('./api/routes/dataForSEO.routes');
const adminRoutes = require('./api/routes/admin.routes');
const creditsRoutes = require('./api/routes/credits.routes'); // Ops Credits system

// Import error handling middleware
const { errorHandler, notFound } = require('./middlewares/error.middleware');

// Load passport strategies
require('./config/passport');

// Initialize Express app
const app = express();

// Set up rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
});

// Apply middleware
app.use(cors());
app.use(helmet());
app.use(
  session({
    secret: config.jwt.secret, // reuse JWT secret for simplicity
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false }, // set to true behind HTTPS proxy
  })
);
app.use(passport.initialize());
app.use(passport.session());
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(morgan('dev'));
app.use(xss());
app.use(limiter);

// Set up MongoDB connection
mongoose
  .connect(config.mongoURI)
  .then(() => {
    console.log('MongoDB connected successfully');
  })
  .catch((err) => {
    console.error('MongoDB connection error:', err);
    process.exit(1);
  });

// API routes
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/cia', ciaRoutes);
app.use('/api/cartwheel', cartwheelRoutes);
app.use('/api/dataforseo', dataForSEORoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/credits', creditsRoutes); // <-- new Ops Credits endpoints

// API health check route
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'ok', message: 'Project Waterfall API is running' });
});

// Serve static assets in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../../client/build')));
  
  app.get('*', (req, res) => {
    res.sendFile(path.resolve(__dirname, '../../client/build', 'index.html'));
  });
}

// Error handling middleware
app.use(notFound);
app.use(errorHandler);

// Start server
const PORT = config.port || 5000;
app.listen(PORT, () => {
  console.log(`Project Waterfall server running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (err) => {
  console.error('Unhandled Promise Rejection:', err);
  // In production, we might want to exit and let the process manager restart the app
  // process.exit(1);
});

module.exports = app; // For testing purposes
