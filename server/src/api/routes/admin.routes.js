const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');
const mongoose = require('mongoose');
const auth = require('../../middlewares/auth.middleware');
const User = require('../../models/user.model');
const CIAReport = require('../../models/cia-report.model');
const ContentItem = require('../../models/content-item.model');
const Coupon = require('../../models/coupon.model'); // Will create this model next

/**
 * Middleware to ensure user is an admin
 */
const adminOnly = [
  auth,
  auth.authorize(['admin', 'superadmin'])
];

/**
 * Middleware to ensure user is a superadmin
 */
const superAdminOnly = [
  auth,
  auth.authorize(['superadmin'])
];

/**
 * --------------------------------------------------------------------------
 * User Management Routes
 * --------------------------------------------------------------------------
 */

/**
 * @route   GET api/admin/users
 * @desc    Get all users with pagination and filtering
 * @access  Admin
 */
router.get('/users', adminOnly, async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    
    // Build filter object
    const filter = {};
    
    if (req.query.search) {
      const searchRegex = new RegExp(req.query.search, 'i');
      filter.$or = [
        { email: searchRegex },
        { firstName: searchRegex },
        { lastName: searchRegex }
      ];
    }
    
    if (req.query.role) {
      filter.role = req.query.role;
    }
    
    if (req.query.subscription) {
      filter['subscription.tier'] = req.query.subscription;
    }
    
    if (req.query.status === 'active') {
      filter.isActive = true;
      filter.isBanned = false;
    } else if (req.query.status === 'inactive') {
      filter.isActive = false;
    } else if (req.query.status === 'banned') {
      filter.isBanned = true;
    }
    
    // Get users with pagination
    const users = await User.find(filter)
      .select('-password')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);
    
    // Get total count
    const total = await User.countDocuments(filter);
    
    res.json({
      users,
      pagination: {
        total,
        page,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Admin get users error:', error);
    res.status(500).json({ message: 'Server error while retrieving users' });
  }
});

/**
 * @route   GET api/admin/users/:id
 * @desc    Get user details by ID
 * @access  Admin
 */
router.get('/users/:id', adminOnly, async (req, res) => {
  try {
    const user = await User.findById(req.params.id).select('-password');
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    // Get user's reports count
    const reportsCount = await CIAReport.countDocuments({ user: user._id });
    
    // Get user's content items count
    const contentCount = await ContentItem.countDocuments({ user: user._id });
    
    res.json({
      user,
      stats: {
        reportsCount,
        contentCount
      }
    });
  } catch (error) {
    console.error('Admin get user error:', error);
    res.status(500).json({ message: 'Server error while retrieving user' });
  }
});

/**
 * @route   PUT api/admin/users/:id/subscription
 * @desc    Update user subscription
 * @access  Admin
 */
router.put('/users/:id/subscription', adminOnly, async (req, res) => {
  try {
    const {
      tier,
      startDate,
      endDate,
      autoRenew,
      credits
    } = req.body;
    
    // Build subscription update object
    const subscriptionUpdate = {};
    
    if (tier) subscriptionUpdate['subscription.tier'] = tier;
    if (startDate) subscriptionUpdate['subscription.startDate'] = startDate;
    if (endDate) subscriptionUpdate['subscription.endDate'] = endDate;
    if (autoRenew !== undefined) subscriptionUpdate['subscription.autoRenew'] = autoRenew;
    if (credits !== undefined) subscriptionUpdate['subscription.credits'] = credits;
    
    // Update user subscription
    const user = await User.findByIdAndUpdate(
      req.params.id,
      { $set: subscriptionUpdate },
      { new: true }
    ).select('subscription');
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    res.json({
      message: 'User subscription updated successfully',
      subscription: user.subscription
    });
  } catch (error) {
    console.error('Admin update subscription error:', error);
    res.status(500).json({ message: 'Server error while updating subscription' });
  }
});

/**
 * @route   PUT api/admin/users/:id/status
 * @desc    Update user status (active/banned)
 * @access  Admin
 */
router.put('/users/:id/status', adminOnly, async (req, res) => {
  try {
    const { isActive, isBanned } = req.body;
    
    // Build status update object
    const statusUpdate = {};
    
    if (isActive !== undefined) statusUpdate.isActive = isActive;
    if (isBanned !== undefined) statusUpdate.isBanned = isBanned;
    
    // Update user status
    const user = await User.findByIdAndUpdate(
      req.params.id,
      { $set: statusUpdate },
      { new: true }
    ).select('isActive isBanned');
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    res.json({
      message: 'User status updated successfully',
      status: {
        isActive: user.isActive,
        isBanned: user.isBanned
      }
    });
  } catch (error) {
    console.error('Admin update status error:', error);
    res.status(500).json({ message: 'Server error while updating status' });
  }
});

/**
 * @route   DELETE api/admin/users/:id
 * @desc    Delete user (superadmin only)
 * @access  Superadmin
 */
router.delete('/users/:id', superAdminOnly, async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    // Check if trying to delete an admin/superadmin
    if ((user.role === 'admin' || user.role === 'superadmin') && req.user.id !== req.params.id) {
      return res.status(403).json({ message: 'Cannot delete admin users' });
    }
    
    await user.deleteOne();
    
    res.json({ message: 'User deleted successfully' });
  } catch (error) {
    console.error('Admin delete user error:', error);
    res.status(500).json({ message: 'Server error while deleting user' });
  }
});

/**
 * --------------------------------------------------------------------------
 * Coupon Management Routes
 * --------------------------------------------------------------------------
 */

/**
 * @route   POST api/admin/coupons
 * @desc    Create a new coupon
 * @access  Admin
 */
router.post(
  '/coupons',
  [
    adminOnly,
    check('code', 'Coupon code is required').notEmpty(),
    check('discountType', 'Discount type is required').isIn(['percentage', 'fixed', 'free']),
    check('discountValue', 'Discount value is required').optional().isNumeric(),
    check('expiresAt', 'Expiration date must be valid').optional().isISO8601(),
    check('maxUses', 'Maximum uses must be a number').optional().isNumeric(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    
    try {
      const {
        code,
        discountType,
        discountValue,
        expiresAt,
        maxUses,
        description,
        isActive,
        appliesTo,
        freeUsageLimits
      } = req.body;
      
      // Check if coupon code already exists
      const existingCoupon = await Coupon.findOne({ code });
      if (existingCoupon) {
        return res.status(400).json({ message: 'Coupon code already exists' });
      }
      
      // Create new coupon
      const coupon = new Coupon({
        code,
        discountType,
        discountValue: discountType === 'free' ? 100 : discountValue,
        expiresAt,
        maxUses,
        description,
        isActive: isActive !== undefined ? isActive : true,
        appliesTo,
        freeUsageLimits: freeUsageLimits || {}
      });
      
      await coupon.save();
      
      res.status(201).json({
        message: 'Coupon created successfully',
        coupon
      });
    } catch (error) {
      console.error('Create coupon error:', error);
      res.status(500).json({ message: 'Server error while creating coupon' });
    }
  }
);

/**
 * @route   GET api/admin/coupons
 * @desc    Get all coupons with pagination and filtering
 * @access  Admin
 */
router.get('/coupons', adminOnly, async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    
    // Build filter object
    const filter = {};
    
    if (req.query.search) {
      filter.code = new RegExp(req.query.search, 'i');
    }
    
    if (req.query.isActive) {
      filter.isActive = req.query.isActive === 'true';
    }
    
    if (req.query.discountType) {
      filter.discountType = req.query.discountType;
    }
    
    // Get coupons with pagination
    const coupons = await Coupon.find(filter)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);
    
    // Get total count
    const total = await Coupon.countDocuments(filter);
    
    res.json({
      coupons,
      pagination: {
        total,
        page,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Admin get coupons error:', error);
    res.status(500).json({ message: 'Server error while retrieving coupons' });
  }
});

/**
 * @route   GET api/admin/coupons/:id
 * @desc    Get coupon details by ID
 * @access  Admin
 */
router.get('/coupons/:id', adminOnly, async (req, res) => {
  try {
    const coupon = await Coupon.findById(req.params.id);
    
    if (!coupon) {
      return res.status(404).json({ message: 'Coupon not found' });
    }
    
    res.json(coupon);
  } catch (error) {
    console.error('Admin get coupon error:', error);
    res.status(500).json({ message: 'Server error while retrieving coupon' });
  }
});

/**
 * @route   PUT api/admin/coupons/:id
 * @desc    Update coupon
 * @access  Admin
 */
router.put(
  '/coupons/:id',
  [
    adminOnly,
    check('discountType', 'Discount type must be valid').optional().isIn(['percentage', 'fixed', 'free']),
    check('discountValue', 'Discount value must be a number').optional().isNumeric(),
    check('expiresAt', 'Expiration date must be valid').optional().isISO8601(),
    check('maxUses', 'Maximum uses must be a number').optional().isNumeric(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    
    try {
      const {
        discountType,
        discountValue,
        expiresAt,
        maxUses,
        description,
        isActive,
        appliesTo,
        freeUsageLimits
      } = req.body;
      
      // Build coupon update object
      const couponUpdate = {};
      
      if (discountType) {
        couponUpdate.discountType = discountType;
        if (discountType === 'free') {
          couponUpdate.discountValue = 100;
        }
      }
      
      if (discountValue !== undefined && couponUpdate.discountType !== 'free') {
        couponUpdate.discountValue = discountValue;
      }
      
      if (expiresAt) couponUpdate.expiresAt = expiresAt;
      if (maxUses !== undefined) couponUpdate.maxUses = maxUses;
      if (description) couponUpdate.description = description;
      if (isActive !== undefined) couponUpdate.isActive = isActive;
      if (appliesTo) couponUpdate.appliesTo = appliesTo;
      if (freeUsageLimits) couponUpdate.freeUsageLimits = freeUsageLimits;
      
      // Update coupon
      const coupon = await Coupon.findByIdAndUpdate(
        req.params.id,
        { $set: couponUpdate },
        { new: true }
      );
      
      if (!coupon) {
        return res.status(404).json({ message: 'Coupon not found' });
      }
      
      res.json({
        message: 'Coupon updated successfully',
        coupon
      });
    } catch (error) {
      console.error('Admin update coupon error:', error);
      res.status(500).json({ message: 'Server error while updating coupon' });
    }
  }
);

/**
 * @route   DELETE api/admin/coupons/:id
 * @desc    Delete coupon
 * @access  Admin
 */
router.delete('/coupons/:id', adminOnly, async (req, res) => {
  try {
    const coupon = await Coupon.findById(req.params.id);
    
    if (!coupon) {
      return res.status(404).json({ message: 'Coupon not found' });
    }
    
    await coupon.deleteOne();
    
    res.json({ message: 'Coupon deleted successfully' });
  } catch (error) {
    console.error('Admin delete coupon error:', error);
    res.status(500).json({ message: 'Server error while deleting coupon' });
  }
});

/**
 * @route   GET api/admin/coupons/:code/generate-link
 * @desc    Generate a shareable link for a coupon
 * @access  Admin
 */
router.get('/coupons/:code/generate-link', adminOnly, async (req, res) => {
  try {
    const coupon = await Coupon.findOne({ code: req.params.code });
    
    if (!coupon) {
      return res.status(404).json({ message: 'Coupon not found' });
    }
    
    // Generate a shareable link
    const baseUrl = process.env.FRONTEND_URL || 'https://waterfall.app';
    const shareableLink = `${baseUrl}/signup?coupon=${coupon.code}`;
    
    res.json({
      code: coupon.code,
      shareableLink,
      coupon
    });
  } catch (error) {
    console.error('Generate coupon link error:', error);
    res.status(500).json({ message: 'Server error while generating coupon link' });
  }
});

/**
 * --------------------------------------------------------------------------
 * System Monitoring Routes
 * --------------------------------------------------------------------------
 */

/**
 * @route   GET api/admin/system/stats
 * @desc    Get system statistics
 * @access  Admin
 */
router.get('/system/stats', adminOnly, async (req, res) => {
  try {
    // Get user counts
    const totalUsers = await User.countDocuments();
    const activeUsers = await User.countDocuments({ isActive: true, isBanned: false });
    const premiumUsers = await User.countDocuments({ 'subscription.tier': { $in: ['premium', 'enterprise'] } });
    
    // Get content counts
    const totalReports = await CIAReport.countDocuments();
    const totalContentItems = await ContentItem.countDocuments();
    
    // Get API usage
    const apiUsage = await User.aggregate([
      {
        $group: {
          _id: null,
          dataForSEO: { $sum: '$usage.apiCalls.dataForSEO' },
          socialMedia: { $sum: '$usage.apiCalls.socialMedia' }
        }
      }
    ]);
    
    // Get content generation by type
    const contentByType = await ContentItem.aggregate([
      {
        $group: {
          _id: '$contentType',
          count: { $sum: 1 }
        }
      },
      { $sort: { count: -1 } }
    ]);
    
    res.json({
      users: {
        total: totalUsers,
        active: activeUsers,
        premium: premiumUsers
      },
      content: {
        reports: totalReports,
        contentItems: totalContentItems,
        byType: contentByType
      },
      apiUsage: apiUsage[0] || { dataForSEO: 0, socialMedia: 0 }
    });
  } catch (error) {
    console.error('Admin system stats error:', error);
    res.status(500).json({ message: 'Server error while retrieving system stats' });
  }
});

/**
 * @route   GET api/admin/system/api-usage
 * @desc    Get detailed API usage statistics
 * @access  Admin
 */
router.get('/system/api-usage', adminOnly, async (req, res) => {
  try {
    // Get time range from query params
    const startDate = req.query.startDate ? new Date(req.query.startDate) : new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // Default to last 30 days
    const endDate = req.query.endDate ? new Date(req.query.endDate) : new Date();
    
    // Get API usage by day
    const dailyUsage = await CIAReport.aggregate([
      {
        $match: {
          createdAt: { $gte: startDate, $lte: endDate }
        }
      },
      {
        $group: {
          _id: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
          dataForSEO: { $sum: '$processingMetadata.apiCalls.dataForSEO' }
        }
      },
      { $sort: { _id: 1 } }
    ]);
    
    // Get API usage by user
    const userUsage = await User.aggregate([
      {
        $match: {
          'usage.apiCalls.dataForSEO': { $gt: 0 }
        }
      },
      {
        $project: {
          _id: 1,
          email: 1,
          fullName: { $concat: ['$firstName', ' ', '$lastName'] },
          dataForSEO: '$usage.apiCalls.dataForSEO',
          socialMedia: '$usage.apiCalls.socialMedia'
        }
      },
      { $sort: { dataForSEO: -1 } },
      { $limit: 10 }
    ]);
    
    res.json({
      dailyUsage,
      userUsage,
      totals: {
        dataForSEO: dailyUsage.reduce((sum, day) => sum + day.dataForSEO, 0)
      }
    });
  } catch (error) {
    console.error('Admin API usage stats error:', error);
    res.status(500).json({ message: 'Server error while retrieving API usage stats' });
  }
});

/**
 * --------------------------------------------------------------------------
 * Pricing Control Routes
 * --------------------------------------------------------------------------
 */

/**
 * @route   GET api/admin/pricing
 * @desc    Get pricing configuration
 * @access  Admin
 */
router.get('/pricing', adminOnly, async (req, res) => {
  try {
    // In a real implementation, this would fetch from a pricing configuration collection
    // For now, we'll return a hardcoded pricing structure that can be updated
    
    const pricing = {
      tiers: [
        {
          id: 'free',
          name: 'Free',
          price: 0,
          billingCycle: 'monthly',
          features: [
            { name: 'Clarity Board', included: true, limit: 5 },
            { name: 'CIA Reports', included: false },
            { name: 'Cartwheel Content', included: false },
            { name: 'DataForSEO Live', included: false },
          ]
        },
        {
          id: 'basic',
          name: 'Basic',
          price: 49,
          billingCycle: 'monthly',
          features: [
            { name: 'Clarity Board', included: true, limit: 'Unlimited' },
            { name: 'CIA Reports', included: true, limit: 5 },
            { name: 'Cartwheel Content', included: true, limit: 10 },
            { name: 'DataForSEO Live', included: false },
          ]
        },
        {
          id: 'premium',
          name: 'Premium',
          price: 99,
          billingCycle: 'monthly',
          features: [
            { name: 'Clarity Board', included: true, limit: 'Unlimited' },
            { name: 'CIA Reports', included: true, limit: 20 },
            { name: 'Cartwheel Content', included: true, limit: 50 },
            { name: 'DataForSEO Live', included: true },
          ]
        },
        {
          id: 'enterprise',
          name: 'Enterprise',
          price: 299,
          billingCycle: 'monthly',
          features: [
            { name: 'Clarity Board', included: true, limit: 'Unlimited' },
            { name: 'CIA Reports', included: true, limit: 'Unlimited' },
            { name: 'Cartwheel Content', included: true, limit: 'Unlimited' },
            { name: 'DataForSEO Live', included: true },
            { name: 'Team Features', included: true },
            { name: 'API Access', included: true },
          ]
        }
      ],
      featureDescriptions: {
        'Clarity Board': 'Lightweight marketing intelligence dashboard',
        'CIA Reports': 'Comprehensive marketing intelligence reports',
        'Cartwheel Content': 'AI-powered content generation',
        'DataForSEO Live': 'Real-time SEO data',
        'Team Features': 'Collaboration tools for teams',
        'API Access': 'Programmatic access to Waterfall API'
      }
    };
    
    res.json(pricing);
  } catch (error) {
    console.error('Admin get pricing error:', error);
    res.status(500).json({ message: 'Server error while retrieving pricing' });
  }
});

/**
 * @route   PUT api/admin/pricing
 * @desc    Update pricing configuration
 * @access  Superadmin
 */
router.put('/pricing', superAdminOnly, async (req, res) => {
  try {
    const { tiers, featureDescriptions } = req.body;
    
    // In a real implementation, this would update a pricing configuration collection
    // For now, we'll just return the updated pricing structure
    
    res.json({
      message: 'Pricing updated successfully',
      pricing: {
        tiers,
        featureDescriptions
      }
    });
  } catch (error) {
    console.error('Admin update pricing error:', error);
    res.status(500).json({ message: 'Server error while updating pricing' });
  }
});

/**
 * --------------------------------------------------------------------------
 * Analytics Routes
 * --------------------------------------------------------------------------
 */

/**
 * @route   GET api/admin/analytics/users
 * @desc    Get user analytics
 * @access  Admin
 */
router.get('/analytics/users', adminOnly, async (req, res) => {
  try {
    // Get time range from query params
    const startDate = req.query.startDate ? new Date(req.query.startDate) : new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // Default to last 30 days
    const endDate = req.query.endDate ? new Date(req.query.endDate) : new Date();
    
    // Get user signups by day
    const signups = await User.aggregate([
      {
        $match: {
          createdAt: { $gte: startDate, $lte: endDate }
        }
      },
      {
        $group: {
          _id: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
          count: { $sum: 1 }
        }
      },
      { $sort: { _id: 1 } }
    ]);
    
    // Get users by subscription tier
    const subscriptionTiers = await User.aggregate([
      {
        $group: {
          _id: '$subscription.tier',
          count: { $sum: 1 }
        }
      },
      { $sort: { _id: 1 } }
    ]);
    
    // Get users by authentication method
    const authMethods = await User.aggregate([
      {
        $group: {
          _id: {
            $cond: {
              if: { $ifNull: ['$oauth.google.id', false] },
              then: 'google',
              else: 'email'
            }
          },
          count: { $sum: 1 }
        }
      }
    ]);
    
    res.json({
      signups,
      subscriptionTiers,
      authMethods,
      totals: {
        users: await User.countDocuments(),
        newUsers: await User.countDocuments({ createdAt: { $gte: startDate, $lte: endDate } })
      }
    });
  } catch (error) {
    console.error('Admin user analytics error:', error);
    res.status(500).json({ message: 'Server error while retrieving user analytics' });
  }
});

/**
 * @route   GET api/admin/analytics/content
 * @desc    Get content analytics
 * @access  Admin
 */
router.get('/analytics/content', adminOnly, async (req, res) => {
  try {
    // Get time range from query params
    const startDate = req.query.startDate ? new Date(req.query.startDate) : new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // Default to last 30 days
    const endDate = req.query.endDate ? new Date(req.query.endDate) : new Date();
    
    // Get CIA reports by day
    const reports = await CIAReport.aggregate([
      {
        $match: {
          createdAt: { $gte: startDate, $lte: endDate }
        }
      },
      {
        $group: {
          _id: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
          count: { $sum: 1 }
        }
      },
      { $sort: { _id: 1 } }
    ]);
    
    // Get content items by day
    const contentItems = await ContentItem.aggregate([
      {
        $match: {
          createdAt: { $gte: startDate, $lte: endDate }
        }
      },
      {
        $group: {
          _id: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
          count: { $sum: 1 }
        }
      },
      { $sort: { _id: 1 } }
    ]);
    
    // Get content by type
    const contentByType = await ContentItem.aggregate([
      {
        $match: {
          createdAt: { $gte: startDate, $lte: endDate }
        }
      },
      {
        $group: {
          _id: '$contentType',
          count: { $sum: 1 }
        }
      },
      { $sort: { count: -1 } }
    ]);
    
    res.json({
      reports,
      contentItems,
      contentByType,
      totals: {
        reports: await CIAReport.countDocuments({ createdAt: { $gte: startDate, $lte: endDate } }),
        contentItems: await ContentItem.countDocuments({ createdAt: { $gte: startDate, $lte: endDate } })
      }
    });
  } catch (error) {
    console.error('Admin content analytics error:', error);
    res.status(500).json({ message: 'Server error while retrieving content analytics' });
  }
});

module.exports = router;
