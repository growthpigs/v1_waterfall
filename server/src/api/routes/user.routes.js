const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');
const User = require('../../models/user.model');
const auth = require('../../middlewares/auth.middleware');

/**
 * @route   GET api/users/profile
 * @desc    Get current user's profile
 * @access  Private
 */
router.get('/profile', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    res.json(user);
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({ message: 'Server error while retrieving profile' });
  }
});

/**
 * @route   PUT api/users/profile
 * @desc    Update user profile
 * @access  Private
 */
router.put(
  '/profile',
  [
    auth,
    check('firstName', 'First name is required').optional().notEmpty(),
    check('lastName', 'Last name is required').optional().notEmpty(),
    check('email', 'Please include a valid email').optional().isEmail(),
    check('company.name', 'Company name must not be empty').optional().notEmpty(),
    check('company.website', 'Website must be a valid URL').optional().isURL(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      // Fields that can be updated
      const {
        firstName,
        lastName,
        email,
        company,
        profile
      } = req.body;

      // Build user profile object
      const userFields = {};
      
      if (firstName) userFields.firstName = firstName;
      if (lastName) userFields.lastName = lastName;
      if (email) userFields.email = email;
      
      if (company) {
        userFields.company = {};
        if (company.name) userFields.company.name = company.name;
        if (company.website) userFields.company.website = company.website;
        if (company.industry) userFields.company.industry = company.industry;
        if (company.size) userFields.company.size = company.size;
      }
      
      if (profile) {
        userFields.profile = {};
        if (profile.avatar) userFields.profile.avatar = profile.avatar;
        if (profile.bio) userFields.profile.bio = profile.bio;
        if (profile.title) userFields.profile.title = profile.title;
        if (profile.phone) userFields.profile.phone = profile.phone;
        if (profile.timezone) userFields.profile.timezone = profile.timezone;
        if (profile.language) userFields.profile.language = profile.language;
      }

      // Update user
      const user = await User.findByIdAndUpdate(
        req.user.id,
        { $set: userFields },
        { new: true, runValidators: true }
      ).select('-password');

      res.json(user);
    } catch (error) {
      console.error('Update profile error:', error);
      res.status(500).json({ message: 'Server error while updating profile' });
    }
  }
);

/**
 * @route   PUT api/users/preferences
 * @desc    Update user preferences
 * @access  Private
 */
router.put('/preferences', auth, async (req, res) => {
  try {
    const { theme, emailNotifications, defaultExportFormat } = req.body;

    // Build preferences object
    const preferencesFields = {};
    
    if (theme) preferencesFields['preferences.theme'] = theme;
    
    if (emailNotifications) {
      if (emailNotifications.marketing !== undefined) {
        preferencesFields['preferences.emailNotifications.marketing'] = emailNotifications.marketing;
      }
      if (emailNotifications.reports !== undefined) {
        preferencesFields['preferences.emailNotifications.reports'] = emailNotifications.reports;
      }
      if (emailNotifications.alerts !== undefined) {
        preferencesFields['preferences.emailNotifications.alerts'] = emailNotifications.alerts;
      }
    }
    
    if (defaultExportFormat) {
      preferencesFields['preferences.defaultExportFormat'] = defaultExportFormat;
    }

    // Update user preferences
    const user = await User.findByIdAndUpdate(
      req.user.id,
      { $set: preferencesFields },
      { new: true, runValidators: true }
    ).select('preferences');

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json(user.preferences);
  } catch (error) {
    console.error('Update preferences error:', error);
    res.status(500).json({ message: 'Server error while updating preferences' });
  }
});

/**
 * @route   GET api/users/subscription
 * @desc    Get user subscription details
 * @access  Private
 */
router.get('/subscription', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('subscription subscriptionStatus');
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    res.json({
      subscription: user.subscription,
      status: user.subscriptionStatus
    });
  } catch (error) {
    console.error('Get subscription error:', error);
    res.status(500).json({ message: 'Server error while retrieving subscription' });
  }
});

/**
 * @route   PUT api/users/subscription
 * @desc    Update user subscription (admin only)
 * @access  Private/Admin
 */
router.put(
  '/subscription',
  [auth, auth.authorize(['admin', 'superadmin'])],
  async (req, res) => {
    try {
      const {
        tier,
        startDate,
        endDate,
        autoRenew,
        paymentMethod,
        paymentId,
        credits
      } = req.body;

      // Build subscription object
      const subscriptionFields = {};
      
      if (tier) subscriptionFields['subscription.tier'] = tier;
      if (startDate) subscriptionFields['subscription.startDate'] = startDate;
      if (endDate) subscriptionFields['subscription.endDate'] = endDate;
      if (autoRenew !== undefined) subscriptionFields['subscription.autoRenew'] = autoRenew;
      if (paymentMethod) subscriptionFields['subscription.paymentMethod'] = paymentMethod;
      if (paymentId) subscriptionFields['subscription.paymentId'] = paymentId;
      if (credits !== undefined) subscriptionFields['subscription.credits'] = credits;

      // Update user subscription
      const user = await User.findByIdAndUpdate(
        req.body.userId, // Admin can update any user's subscription
        { $set: subscriptionFields },
        { new: true, runValidators: true }
      ).select('subscription subscriptionStatus');

      if (!user) {
        return res.status(404).json({ message: 'User not found' });
      }

      res.json({
        subscription: user.subscription,
        status: user.subscriptionStatus
      });
    } catch (error) {
      console.error('Update subscription error:', error);
      res.status(500).json({ message: 'Server error while updating subscription' });
    }
  }
);

/**
 * @route   POST api/users/subscription/purchase
 * @desc    Purchase or upgrade subscription
 * @access  Private
 */
router.post(
  '/subscription/purchase',
  [
    auth,
    check('tier', 'Subscription tier is required').isIn(['free', 'basic', 'premium', 'enterprise']),
    check('paymentMethod', 'Payment method is required').isIn(['credit_card', 'paypal', 'bank_transfer', 'crypto']),
    check('paymentToken', 'Payment token is required').not().isEmpty(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { tier, paymentMethod, paymentToken, autoRenew = true } = req.body;

      // TODO: Process payment with payment provider
      // This would typically involve calling a payment service
      
      // For now, simulate a successful payment
      const paymentId = `payment_${Date.now()}`;
      
      // Calculate subscription dates
      const startDate = new Date();
      const endDate = new Date();
      endDate.setMonth(endDate.getMonth() + 1); // 1 month subscription
      
      // Update user subscription
      const subscriptionFields = {
        'subscription.tier': tier,
        'subscription.startDate': startDate,
        'subscription.endDate': endDate,
        'subscription.autoRenew': autoRenew,
        'subscription.paymentMethod': paymentMethod,
        'subscription.paymentId': paymentId
      };
      
      // If upgrading to premium or enterprise, add some credits
      if (tier === 'premium') {
        subscriptionFields['subscription.credits'] = 100;
      } else if (tier === 'enterprise') {
        subscriptionFields['subscription.credits'] = 500;
      }

      const user = await User.findByIdAndUpdate(
        req.user.id,
        { $set: subscriptionFields },
        { new: true, runValidators: true }
      ).select('subscription subscriptionStatus');

      res.json({
        message: `Successfully subscribed to ${tier} plan`,
        subscription: user.subscription,
        status: user.subscriptionStatus
      });
    } catch (error) {
      console.error('Subscription purchase error:', error);
      res.status(500).json({ message: 'Server error during subscription purchase' });
    }
  }
);

/**
 * @route   PUT api/users/subscription/cancel
 * @desc    Cancel subscription auto-renewal
 * @access  Private
 */
router.put('/subscription/cancel', auth, async (req, res) => {
  try {
    // Update user subscription
    const user = await User.findByIdAndUpdate(
      req.user.id,
      { $set: { 'subscription.autoRenew': false } },
      { new: true, runValidators: true }
    ).select('subscription subscriptionStatus');

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json({
      message: 'Subscription auto-renewal cancelled',
      subscription: user.subscription,
      status: user.subscriptionStatus
    });
  } catch (error) {
    console.error('Cancel subscription error:', error);
    res.status(500).json({ message: 'Server error while cancelling subscription' });
  }
});

/**
 * @route   PUT api/users/integrations
 * @desc    Update user API integrations
 * @access  Private
 */
router.put('/integrations', auth, async (req, res) => {
  try {
    const { dataForSEO, googleTrends, twitter, tiktok, notion } = req.body;

    // Build integrations object
    const integrationsFields = {};
    
    if (dataForSEO) {
      if (dataForSEO.enabled !== undefined) {
        integrationsFields['integrations.dataForSEO.enabled'] = dataForSEO.enabled;
      }
      if (dataForSEO.login) {
        integrationsFields['integrations.dataForSEO.login'] = dataForSEO.login;
      }
      if (dataForSEO.password) {
        integrationsFields['integrations.dataForSEO.password'] = dataForSEO.password;
      }
      if (dataForSEO.useLiveData !== undefined) {
        integrationsFields['integrations.dataForSEO.useLiveData'] = dataForSEO.useLiveData;
      }
    }
    
    if (googleTrends) {
      if (googleTrends.enabled !== undefined) {
        integrationsFields['integrations.googleTrends.enabled'] = googleTrends.enabled;
      }
      if (googleTrends.apiKey) {
        integrationsFields['integrations.googleTrends.apiKey'] = googleTrends.apiKey;
      }
    }
    
    if (twitter) {
      if (twitter.enabled !== undefined) {
        integrationsFields['integrations.twitter.enabled'] = twitter.enabled;
      }
      if (twitter.apiKey) {
        integrationsFields['integrations.twitter.apiKey'] = twitter.apiKey;
      }
      if (twitter.apiSecret) {
        integrationsFields['integrations.twitter.apiSecret'] = twitter.apiSecret;
      }
      if (twitter.bearerToken) {
        integrationsFields['integrations.twitter.bearerToken'] = twitter.bearerToken;
      }
    }
    
    if (tiktok) {
      if (tiktok.enabled !== undefined) {
        integrationsFields['integrations.tiktok.enabled'] = tiktok.enabled;
      }
      if (tiktok.apiKey) {
        integrationsFields['integrations.tiktok.apiKey'] = tiktok.apiKey;
      }
      if (tiktok.apiSecret) {
        integrationsFields['integrations.tiktok.apiSecret'] = tiktok.apiSecret;
      }
    }
    
    if (notion) {
      if (notion.enabled !== undefined) {
        integrationsFields['integrations.notion.enabled'] = notion.enabled;
      }
      if (notion.apiKey) {
        integrationsFields['integrations.notion.apiKey'] = notion.apiKey;
      }
      if (notion.workspaceId) {
        integrationsFields['integrations.notion.workspaceId'] = notion.workspaceId;
      }
      if (notion.databaseId) {
        integrationsFields['integrations.notion.databaseId'] = notion.databaseId;
      }
    }

    // Update user integrations
    const user = await User.findByIdAndUpdate(
      req.user.id,
      { $set: integrationsFields },
      { new: true, runValidators: true }
    ).select('integrations');

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json(user.integrations);
  } catch (error) {
    console.error('Update integrations error:', error);
    res.status(500).json({ message: 'Server error while updating integrations' });
  }
});

/**
 * @route   GET api/users/usage
 * @desc    Get user usage statistics
 * @access  Private
 */
router.get('/usage', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('usage');
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    res.json(user.usage);
  } catch (error) {
    console.error('Get usage error:', error);
    res.status(500).json({ message: 'Server error while retrieving usage statistics' });
  }
});

/**
 * @route   GET api/users
 * @desc    Get all users (admin only)
 * @access  Private/Admin
 */
router.get('/', [auth, auth.authorize(['admin', 'superadmin'])], async (req, res) => {
  try {
    const users = await User.find()
      .select('-password')
      .sort({ createdAt: -1 });
    
    res.json(users);
  } catch (error) {
    console.error('Get all users error:', error);
    res.status(500).json({ message: 'Server error while retrieving users' });
  }
});

/**
 * @route   GET api/users/:id
 * @desc    Get user by ID (admin only)
 * @access  Private/Admin
 */
router.get('/:id', [auth, auth.authorize(['admin', 'superadmin'])], async (req, res) => {
  try {
    const user = await User.findById(req.params.id).select('-password');
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    res.json(user);
  } catch (error) {
    console.error('Get user by ID error:', error);
    res.status(500).json({ message: 'Server error while retrieving user' });
  }
});

/**
 * @route   PUT api/users/:id/status
 * @desc    Update user status (active/banned) (admin only)
 * @access  Private/Admin
 */
router.put(
  '/:id/status',
  [
    auth,
    auth.authorize(['admin', 'superadmin']),
    check('isActive', 'isActive field must be a boolean').optional().isBoolean(),
    check('isBanned', 'isBanned field must be a boolean').optional().isBoolean(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { isActive, isBanned } = req.body;

      // Build status update object
      const statusFields = {};
      
      if (isActive !== undefined) statusFields.isActive = isActive;
      if (isBanned !== undefined) statusFields.isBanned = isBanned;

      // Update user status
      const user = await User.findByIdAndUpdate(
        req.params.id,
        { $set: statusFields },
        { new: true, runValidators: true }
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
      console.error('Update user status error:', error);
      res.status(500).json({ message: 'Server error while updating user status' });
    }
  }
);

/**
 * @route   DELETE api/users/:id
 * @desc    Delete user (admin only)
 * @access  Private/Admin
 */
router.delete('/:id', [auth, auth.authorize(['superadmin'])], async (req, res) => {
  try {
    // Only superadmin can delete users
    const user = await User.findById(req.params.id);
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    // Prevent deleting another admin or superadmin
    if ((user.role === 'admin' || user.role === 'superadmin') && req.user.role !== 'superadmin') {
      return res.status(403).json({ message: 'Not authorized to delete admin users' });
    }
    
    await user.remove();
    
    res.json({ message: 'User deleted successfully' });
  } catch (error) {
    console.error('Delete user error:', error);
    res.status(500).json({ message: 'Server error while deleting user' });
  }
});

module.exports = router;
