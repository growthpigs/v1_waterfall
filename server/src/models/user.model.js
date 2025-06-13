const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const config = require('../config');

// Define subscription tier enum
const SUBSCRIPTION_TIERS = {
  FREE: 'free', // Clarity Board access only
  BASIC: 'basic', // Full CIA access and limited Cartwheel usage
  PREMIUM: 'premium', // Unlimited access to all features
  ENTERPRISE: 'enterprise' // Team features and custom integrations
};

// Define user schema
const userSchema = new mongoose.Schema(
  {
    // Authentication fields
    email: {
      type: String,
      required: [true, 'Email is required'],
      unique: true,
      lowercase: true,
      trim: true,
      match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please provide a valid email address']
    },
    password: {
      type: String,
      required: [true, 'Password is required'],
      minlength: [8, 'Password must be at least 8 characters long'],
      select: false // Don't return password in queries by default
    },
    firstName: {
      type: String,
      required: [true, 'First name is required'],
      trim: true
    },
    lastName: {
      type: String,
      required: [true, 'Last name is required'],
      trim: true
    },
    isEmailVerified: {
      type: Boolean,
      default: false
    },
    verificationToken: String,
    verificationTokenExpires: Date,
    resetPasswordToken: String,
    resetPasswordExpires: Date,
    lastLogin: Date,
    
    // OAuth / SSO information
    oauth: {
      google: {
        id: String,
        email: String,
        name: String,
        picture: String,
        accessToken: String,
        refreshToken: String,
        lastLogin: Date
      }
      // Additional providers (facebook, github, etc.) can be added here later
    },
    
    // Subscription information
    subscription: {
      tier: {
        type: String,
        enum: Object.values(SUBSCRIPTION_TIERS),
        default: SUBSCRIPTION_TIERS.FREE
      },
      startDate: Date,
      endDate: Date,
      autoRenew: {
        type: Boolean,
        default: true
      },
      paymentMethod: {
        type: String,
        enum: ['credit_card', 'paypal', 'bank_transfer', 'crypto', null],
        default: null
      },
      paymentId: String, // Reference to payment provider
      credits: {
        type: Number,
        default: 0 // For pay-as-you-go model
      }
    },
    
    // User profile and preferences
    company: {
      name: String,
      website: String,
      industry: String,
      size: String
    },
    profile: {
      avatar: String,
      bio: String,
      title: String,
      phone: String,
      timezone: String,
      language: {
        type: String,
        default: 'en-US'
      }
    },
    preferences: {
      theme: {
        type: String,
        enum: ['light', 'dark', 'system'],
        default: 'system'
      },
      emailNotifications: {
        marketing: {
          type: Boolean,
          default: true
        },
        reports: {
          type: Boolean,
          default: true
        },
        alerts: {
          type: Boolean,
          default: true
        }
      },
      defaultExportFormat: {
        type: String,
        enum: ['pdf', 'docx', 'notion', 'google_sheets'],
        default: 'pdf'
      }
    },
    
    // API integrations
    integrations: {
      dataForSEO: {
        enabled: {
          type: Boolean,
          default: false
        },
        login: String,
        password: String,
        useLiveData: {
          type: Boolean,
          default: false
        }
      },
      /* Generic social-media data source (e.g. Apify, custom scrapers, etc.) */
      socialMedia: {
        enabled: {                   // enable / disable integration
          type: Boolean,
          default: false
        },
        provider: {                  // 'apify', 'custom', 'direct', etc.
          type: String,
          enum: ['apify', 'custom', 'direct'],
          default: 'apify'
        },
        apiKey: String,              // token / key if required by provider
        config: Schema.Types.Mixed   // flexible config blob for provider-specific options
      },
      notion: {
        enabled: {
          type: Boolean,
          default: false
        },
        apiKey: String,
        workspaceId: String,
        databaseId: String
      }
    },
    
    // Usage tracking
    usage: {
      ciaReports: {
        count: {
          type: Number,
          default: 0
        },
        lastUsed: Date
      },
      clarityBoard: {
        count: {
          type: Number,
          default: 0
        },
        lastUsed: Date
      },
      cartwheelContent: {
        count: {
          type: Number,
          default: 0
        },
        byType: {
          type: Map,
          of: Number,
          default: {}
        },
        lastUsed: Date
      },
      apiCalls: {
        dataForSEO: {
          type: Number,
          default: 0
        },
        socialMedia: {
          type: Number,
          default: 0
        }
      }
    },
    
    // Role-based access control
    role: {
      type: String,
      enum: ['user', 'admin', 'superadmin'],
      default: 'user'
    },
    
    // Account status
    isActive: {
      type: Boolean,
      default: true
    },
    isBanned: {
      type: Boolean,
      default: false
    },
    
    // Referral information
    referral: {
      code: String,
      referredBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
      },
      referrals: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
      }]
    }
  },
  {
    timestamps: true, // Adds createdAt and updatedAt
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
  }
);

// Virtual for full name
userSchema.virtual('fullName').get(function() {
  return `${this.firstName} ${this.lastName}`;
});

// Virtual for subscription status
userSchema.virtual('subscriptionStatus').get(function() {
  if (!this.subscription.endDate) return 'inactive';
  return new Date() < new Date(this.subscription.endDate) ? 'active' : 'expired';
});

// Hash password before saving
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) {
    return next();
  }
  
  try {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Method to check if password matches
userSchema.methods.matchPassword = async function(enteredPassword) {
  return await bcrypt.compare(enteredPassword, this.password);
};

// Method to generate JWT token
userSchema.methods.generateAuthToken = function() {
  return jwt.sign(
    { id: this._id, role: this.role },
    config.jwt.secret,
    { expiresIn: config.jwt.expiresIn }
  );
};

// Method to generate refresh token
userSchema.methods.generateRefreshToken = function() {
  return jwt.sign(
    { id: this._id },
    config.jwt.refreshSecret,
    { expiresIn: config.jwt.refreshExpiresIn }
  );
};

// Method to check if user can access a specific feature based on subscription
userSchema.methods.canAccess = function(feature) {
  const tier = this.subscription.tier;
  
  // Define feature access by subscription tier
  const featureAccess = {
    'cia': [SUBSCRIPTION_TIERS.BASIC, SUBSCRIPTION_TIERS.PREMIUM, SUBSCRIPTION_TIERS.ENTERPRISE],
    'clarityBoard': [SUBSCRIPTION_TIERS.FREE, SUBSCRIPTION_TIERS.BASIC, SUBSCRIPTION_TIERS.PREMIUM, SUBSCRIPTION_TIERS.ENTERPRISE],
    'cartwheel': [SUBSCRIPTION_TIERS.PREMIUM, SUBSCRIPTION_TIERS.ENTERPRISE],
    'cartwheelLimited': [SUBSCRIPTION_TIERS.BASIC, SUBSCRIPTION_TIERS.PREMIUM, SUBSCRIPTION_TIERS.ENTERPRISE],
    'dataForSEOLive': [SUBSCRIPTION_TIERS.PREMIUM, SUBSCRIPTION_TIERS.ENTERPRISE],
    'teamFeatures': [SUBSCRIPTION_TIERS.ENTERPRISE],
    'apiAccess': [SUBSCRIPTION_TIERS.ENTERPRISE]
  };
  
  // Check if user's subscription tier allows access to the feature
  return featureAccess[feature]?.includes(tier) || false;
};

// Create and export the User model
const User = mongoose.model('User', userSchema);
module.exports = User;
