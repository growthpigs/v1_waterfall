const jwt = require('jsonwebtoken');
const config = require('../config');
const User = require('../models/user.model');

/**
 * Authentication middleware
 * Verifies JWT token and attaches user to request object
 */
const auth = async (req, res, next) => {
  try {
    // Get token from header
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({ message: 'No authentication token, access denied' });
    }

    // Verify token
    const decoded = jwt.verify(token, config.jwt.secret);
    
    // Find user by id
    const user = await User.findById(decoded.id);
    
    if (!user) {
      return res.status(401).json({ message: 'User not found, authentication failed' });
    }
    
    // Check if user is active
    if (!user.isActive) {
      return res.status(403).json({ message: 'Account is deactivated' });
    }
    
    // Check if user is banned
    if (user.isBanned) {
      return res.status(403).json({ message: 'Account is banned' });
    }

    // Add user to request
    req.user = {
      id: user._id,
      email: user.email,
      role: user.role,
      subscription: user.subscription.tier
    };
    
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ message: 'Token expired, please login again' });
    }
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ message: 'Invalid token, authentication failed' });
    }
    console.error('Authentication error:', error);
    return res.status(500).json({ message: 'Server authentication error' });
  }
};

/**
 * Role-based authorization middleware
 * Checks if user has the required role
 * @param {string[]} roles - Array of allowed roles
 */
const authorize = (roles = []) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ message: 'Authentication required' });
    }

    if (roles.length && !roles.includes(req.user.role)) {
      return res.status(403).json({ message: 'Insufficient permissions' });
    }

    next();
  };
};

/**
 * Subscription-based feature access middleware
 * Checks if user's subscription allows access to the feature
 * @param {string} feature - Feature to check access for
 */
const checkFeatureAccess = (feature) => {
  return async (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ message: 'Authentication required' });
    }

    try {
      const user = await User.findById(req.user.id);
      
      if (!user) {
        return res.status(401).json({ message: 'User not found' });
      }
      
      if (!user.canAccess(feature)) {
        return res.status(403).json({ 
          message: 'Subscription upgrade required',
          feature: feature,
          currentTier: user.subscription.tier
        });
      }
      
      next();
    } catch (error) {
      console.error('Feature access check error:', error);
      return res.status(500).json({ message: 'Server error during feature access check' });
    }
  };
};

// Export as a single middleware function with additional methods
module.exports = auth;
module.exports.authorize = authorize;
module.exports.checkFeatureAccess = checkFeatureAccess;
