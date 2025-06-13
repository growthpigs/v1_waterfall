const mongoose = require('mongoose');
const Schema = mongoose.Schema;

// Define discount type enum
const DISCOUNT_TYPES = {
  PERCENTAGE: 'percentage', // Percentage off (e.g., 20% off)
  FIXED: 'fixed',           // Fixed amount off (e.g., $10 off)
  FREE: 'free'              // Free access (100% off)
};

// Define subscription tiers that coupons can apply to
const SUBSCRIPTION_TIERS = ['free', 'basic', 'premium', 'enterprise'];

// Define services that can have free usage limits
const SERVICES = ['clarityBoard', 'ciaReports', 'cartwheelContent', 'dataForSEOLive'];

// Define coupon schema
const couponSchema = new mongoose.Schema(
  {
    // Coupon identification
    code: {
      type: String,
      required: [true, 'Coupon code is required'],
      unique: true,
      trim: true,
      uppercase: true
    },
    
    // Discount information
    discountType: {
      type: String,
      enum: Object.values(DISCOUNT_TYPES),
      required: [true, 'Discount type is required']
    },
    discountValue: {
      type: Number,
      required: function() {
        return this.discountType !== DISCOUNT_TYPES.FREE;
      },
      min: [0, 'Discount value cannot be negative'],
      max: [100, 'Percentage discount cannot exceed 100%'],
      default: function() {
        return this.discountType === DISCOUNT_TYPES.FREE ? 100 : 0;
      }
    },
    
    // Validity constraints
    isLifetime: {
      type: Boolean,
      default: false,
      description: 'If true, the coupon never expires'
    },
    expiresAt: {
      type: Date,
      default: function() {
        // Default to 1 year from creation, unless it's a lifetime coupon
        if (this.isLifetime) return null;
        const oneYear = new Date();
        oneYear.setFullYear(oneYear.getFullYear() + 1);
        return oneYear;
      },
      required: function() {
        // Only required if not a lifetime coupon
        return !this.isLifetime;
      }
    },
    maxUses: {
      type: Number,
      min: [0, 'Maximum uses cannot be negative'],
      default: null // null means unlimited
    },
    isActive: {
      type: Boolean,
      default: true
    },
    
    // Billing discount duration (for time-limited discounts)
    billingDiscountDuration: {
      type: Number,
      min: [0, 'Billing discount duration cannot be negative'],
      default: 0, // 0 means applies to all billing cycles (permanent discount)
      description: 'Number of months the discount applies for (0 = permanent)'
    },
    
    // Description and metadata
    description: {
      type: String,
      trim: true
    },
    createdBy: {
      type: Schema.Types.ObjectId,
      ref: 'User'
    },
    
    // Usage tracking
    uses: {
      type: Number,
      default: 0
    },
    usedBy: [{
      user: {
        type: Schema.Types.ObjectId,
        ref: 'User'
      },
      usedAt: {
        type: Date,
        default: Date.now
      },
      discountApplied: Number // Amount of discount applied
    }],
    
    // Application scope
    appliesTo: {
      subscriptionTiers: {
        type: [{
          type: String,
          enum: SUBSCRIPTION_TIERS
        }],
        default: SUBSCRIPTION_TIERS // By default applies to all tiers
      },
      specificFeatures: [{
        type: String,
        enum: SERVICES
      }]
    },
    
    // Free usage limits for specific services
    freeUsageLimits: {
      clarityBoard: {
        type: Number,
        min: 0,
        default: 0
      },
      ciaReports: {
        type: Number,
        min: 0,
        default: 0
      },
      cartwheelContent: {
        type: Number,
        min: 0,
        default: 0
      },
      dataForSEOLive: {
        type: Number,
        min: 0,
        default: 0
      }
      // Additional services can be added here
    }
  },
  {
    timestamps: true, // Adds createdAt and updatedAt
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
  }
);

// Virtual for coupon status
couponSchema.virtual('status').get(function() {
  if (!this.isActive) return 'inactive';
  if (!this.isLifetime && this.expiresAt && new Date() > this.expiresAt) return 'expired';
  if (this.maxUses !== null && this.uses >= this.maxUses) return 'exhausted';
  return 'active';
});

// Virtual for remaining uses
couponSchema.virtual('remainingUses').get(function() {
  if (this.maxUses === null) return 'unlimited';
  return Math.max(0, this.maxUses - this.uses);
});

// Virtual for discount description
couponSchema.virtual('discountDescription').get(function() {
  if (this.discountType === DISCOUNT_TYPES.PERCENTAGE) {
    return `${this.discountValue}% off`;
  } else if (this.discountType === DISCOUNT_TYPES.FIXED) {
    return `$${this.discountValue} off`;
  } else if (this.discountType === DISCOUNT_TYPES.FREE) {
    return 'Free';
  }
  return '';
});

// Virtual for duration description
couponSchema.virtual('durationDescription').get(function() {
  if (this.isLifetime) {
    return 'Lifetime';
  } else if (this.billingDiscountDuration === 0) {
    return 'Permanent';
  } else if (this.billingDiscountDuration === 1) {
    return 'First month only';
  } else {
    return `First ${this.billingDiscountDuration} months`;
  }
});

// Method to check if coupon is valid
couponSchema.methods.isValid = function() {
  // Check if active
  if (!this.isActive) return false;
  
  // Check if expired (unless lifetime)
  if (!this.isLifetime && this.expiresAt && new Date() > this.expiresAt) return false;
  
  // Check if max uses reached
  if (this.maxUses !== null && this.uses >= this.maxUses) return false;
  
  return true;
};

// Method to check if coupon is valid for a specific user and subscription tier
couponSchema.methods.isValidForUser = function(userId, subscriptionTier) {
  // First check general validity
  if (!this.isValid()) return false;
  
  // Check if user has already used this coupon
  const userHasUsed = this.usedBy.some(use => use.user.toString() === userId.toString());
  if (userHasUsed) return false;
  
  // Check if coupon applies to the subscription tier
  if (!this.appliesTo.subscriptionTiers.includes(subscriptionTier)) return false;
  
  return true;
};

// Method to apply coupon to a user
couponSchema.methods.applyToUser = async function(userId, subscriptionTier, amount = 0) {
  // Check if coupon is valid for this user
  if (!this.isValidForUser(userId, subscriptionTier)) {
    throw new Error('Coupon is not valid for this user or subscription tier');
  }
  
  // Calculate discount amount
  let discountAmount = 0;
  if (this.discountType === DISCOUNT_TYPES.PERCENTAGE) {
    discountAmount = (amount * this.discountValue) / 100;
  } else if (this.discountType === DISCOUNT_TYPES.FIXED) {
    discountAmount = Math.min(amount, this.discountValue);
  } else if (this.discountType === DISCOUNT_TYPES.FREE) {
    discountAmount = amount;
  }
  
  // Update usage statistics
  this.uses += 1;
  this.usedBy.push({
    user: userId,
    usedAt: new Date(),
    discountApplied: discountAmount
  });
  
  await this.save();
  
  return {
    discountAmount,
    discountType: this.discountType,
    billingDiscountDuration: this.billingDiscountDuration,
    isLifetime: this.isLifetime,
    freeUsageLimits: this.freeUsageLimits
  };
};

// Method to generate a shareable link
couponSchema.methods.generateShareableLink = function(baseUrl = 'https://waterfall.app') {
  return `${baseUrl}/signup?coupon=${this.code}`;
};

// Static method to find a valid coupon by code
couponSchema.statics.findValidByCode = async function(code, userId, subscriptionTier) {
  const coupon = await this.findOne({ code: code.toUpperCase() });
  
  if (!coupon) return null;
  
  if (!coupon.isValidForUser(userId, subscriptionTier)) return null;
  
  return coupon;
};

// Create and export the Coupon model
const Coupon = mongoose.model('Coupon', couponSchema);
module.exports = Coupon;
