const mongoose = require('mongoose');
const Schema = mongoose.Schema;

/**
 * Operation Cost Schema
 * Defines the cost in Ops Credits for different operations in the system
 * Admin-configurable through the admin panel
 */
const operationCostSchema = new Schema({
  // Operation identifier (unique key for the operation)
  operationId: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  // Display name for the operation
  displayName: {
    type: String,
    required: true,
    trim: true
  },
  // Category for grouping operations
  category: {
    type: String,
    required: true,
    enum: ['cia', 'seo', 'content', 'social', 'analysis', 'export'],
    default: 'content'
  },
  // Cost in Ops Credits
  creditCost: {
    type: Number,
    required: true,
    min: 0,
    default: 1
  },
  // Optional description of what the operation does
  description: {
    type: String,
    trim: true
  },
  // Whether this operation is active/available
  isActive: {
    type: Boolean,
    default: true
  },
  // Additional configuration options (JSON blob)
  config: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  }
}, {
  timestamps: true
});

/**
 * Credit Package Schema
 * Defines available credit packages for purchase
 * Admin-configurable through the admin panel
 */
const creditPackageSchema = new Schema({
  // Package name
  name: {
    type: String,
    required: true,
    trim: true
  },
  // Number of credits in the package
  creditAmount: {
    type: Number,
    required: true,
    min: 1
  },
  // Base price in cents (currency-agnostic)
  basePrice: {
    type: Number,
    required: true,
    min: 0
  },
  // Currency code (EUR, USD, etc.)
  currency: {
    type: String,
    required: true,
    default: 'EUR',
    enum: ['EUR', 'USD', 'GBP']
  },
  // Bonus credits (additional free credits)
  bonusCredits: {
    type: Number,
    default: 0,
    min: 0
  },
  // Sort order for display
  sortOrder: {
    type: Number,
    default: 0
  },
  // Whether this package is active/available
  isActive: {
    type: Boolean,
    default: true
  },
  // Whether this is a featured package
  isFeatured: {
    type: Boolean,
    default: false
  },
  // Package description
  description: {
    type: String,
    trim: true
  }
}, {
  timestamps: true
});

/**
 * Credit Transaction Schema
 * Records all credit transactions (purchases, usage, etc.)
 */
const creditTransactionSchema = new Schema({
  // User who owns the transaction
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  // Transaction type
  type: {
    type: String,
    required: true,
    enum: ['purchase', 'usage', 'refund', 'adjustment', 'expiration', 'subscription_allocation'],
    default: 'usage'
  },
  // Amount of credits (positive for additions, negative for deductions)
  amount: {
    type: Number,
    required: true
  },
  // Balance after transaction
  balanceAfter: {
    type: Number,
    required: true
  },
  // Reference to the operation if type is 'usage'
  operation: {
    type: String,
    ref: 'OperationCost',
    sparse: true
  },
  // Reference to the credit package if type is 'purchase'
  package: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'CreditPackage',
    sparse: true
  },
  // Reference to payment ID if applicable
  paymentId: {
    type: String,
    sparse: true
  },
  // Reference to coupon/discount if applied
  coupon: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Coupon',
    sparse: true
  },
  // Additional notes about the transaction
  notes: {
    type: String
  },
  // Metadata for additional information
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  }
}, {
  timestamps: true
});

// Index for efficient user transaction history queries
creditTransactionSchema.index({ user: 1, createdAt: -1 });

/**
 * User Credit Balance Schema
 * Tracks the current credit balance for each user
 */
const userCreditBalanceSchema = new Schema({
  // User reference
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    unique: true
  },
  // Current balance
  balance: {
    type: Number,
    required: true,
    default: 0,
    min: 0
  },
  // Total credits ever purchased
  totalPurchased: {
    type: Number,
    default: 0,
    min: 0
  },
  // Total credits ever used
  totalUsed: {
    type: Number,
    default: 0,
    min: 0
  },
  // Last transaction date
  lastTransaction: {
    type: Date
  },
  // Low balance notification threshold
  lowBalanceThreshold: {
    type: Number,
    default: 10,
    min: 0
  },
  // Whether low balance notifications are enabled
  lowBalanceNotificationsEnabled: {
    type: Boolean,
    default: true
  },
  // Last low balance notification date
  lastLowBalanceNotification: {
    type: Date
  }
}, {
  timestamps: true
});

// Create models
const OperationCost = mongoose.model('OperationCost', operationCostSchema);
const CreditPackage = mongoose.model('CreditPackage', creditPackageSchema);
const CreditTransaction = mongoose.model('CreditTransaction', creditTransactionSchema);
const UserCreditBalance = mongoose.model('UserCreditBalance', userCreditBalanceSchema);

// Create default operation costs if none exist
const createDefaultOperationCosts = async () => {
  const count = await OperationCost.countDocuments();
  if (count === 0) {
    const defaults = [
      {
        operationId: 'cia_report',
        displayName: 'CIA Report',
        category: 'cia',
        creditCost: 50,
        description: 'Complete marketing intelligence report'
      },
      {
        operationId: 'cia_report_with_competitors',
        displayName: 'CIA Report with Competitor Analysis',
        category: 'cia',
        creditCost: 65,
        description: 'Marketing intelligence report with detailed competitor analysis'
      },
      {
        operationId: 'seo_blog_article',
        displayName: 'SEO Blog Article',
        category: 'content',
        creditCost: 15,
        description: 'SEO-optimized blog article generation'
      },
      {
        operationId: 'social_media_bundle',
        displayName: 'Social Media Bundle',
        category: 'social',
        creditCost: 10,
        description: 'Bundle of social media posts across platforms'
      },
      {
        operationId: 'keyword_research',
        displayName: 'Keyword Research',
        category: 'seo',
        creditCost: 20,
        description: 'In-depth keyword research and analysis'
      },
      {
        operationId: 'competitor_analysis',
        displayName: 'Competitor Analysis',
        category: 'analysis',
        creditCost: 25,
        description: 'Detailed analysis of competitor websites and strategies'
      },
      {
        operationId: 'content_export_pdf',
        displayName: 'Export to PDF',
        category: 'export',
        creditCost: 5,
        description: 'Export content to PDF format'
      }
    ];
    
    await OperationCost.insertMany(defaults);
    console.log('Default operation costs created');
  }
};

// Create default credit packages if none exist
const createDefaultCreditPackages = async () => {
  const count = await CreditPackage.countDocuments();
  if (count === 0) {
    const defaults = [
      {
        name: 'Starter Pack',
        creditAmount: 100,
        basePrice: 1000, // €10.00
        currency: 'EUR',
        bonusCredits: 0,
        sortOrder: 1,
        isFeatured: false,
        description: 'Perfect for small projects and testing'
      },
      {
        name: 'Professional Pack',
        creditAmount: 500,
        basePrice: 4000, // €40.00
        currency: 'EUR',
        bonusCredits: 50, // 10% bonus
        sortOrder: 2,
        isFeatured: true,
        description: 'Best value for regular content creators'
      },
      {
        name: 'Enterprise Pack',
        creditAmount: 1000,
        basePrice: 6500, // €65.00
        currency: 'EUR',
        bonusCredits: 150, // 15% bonus
        sortOrder: 3,
        isFeatured: false,
        description: 'Maximum credits with the biggest bonus'
      }
    ];
    
    await CreditPackage.insertMany(defaults);
    console.log('Default credit packages created');
  }
};

// Initialize defaults when the module is imported
const initDefaults = async () => {
  try {
    await createDefaultOperationCosts();
    await createDefaultCreditPackages();
  } catch (error) {
    console.error('Error creating default Ops Credits data:', error);
  }
};

// Call initialization with a slight delay to ensure DB connection is established
setTimeout(initDefaults, 3000);

module.exports = {
  OperationCost,
  CreditPackage,
  CreditTransaction,
  UserCreditBalance
};
