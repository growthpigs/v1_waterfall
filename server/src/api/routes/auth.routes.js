const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const { check, validationResult } = require('express-validator');
const User = require('../../models/user.model');
const config = require('../../config');
// Passport for OAuth
const passport = require('passport');
// Ensure strategies are loaded
require('../../config/passport');

// Middleware for authentication
const auth = require('../../middlewares/auth.middleware');

/**
 * @route   POST api/auth/register
 * @desc    Register a new user
 * @access  Public
 */
router.post(
  '/register',
  [
    check('email', 'Please include a valid email').isEmail(),
    check('password', 'Password must be at least 8 characters long').isLength({ min: 8 }),
    check('firstName', 'First name is required').not().isEmpty(),
    check('lastName', 'Last name is required').not().isEmpty(),
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, password, firstName, lastName, company } = req.body;

    try {
      // Check if user already exists
      let user = await User.findOne({ email });
      if (user) {
        return res.status(400).json({ message: 'User already exists' });
      }

      // Generate verification token
      const verificationToken = crypto.randomBytes(20).toString('hex');
      const verificationTokenExpires = Date.now() + 24 * 60 * 60 * 1000; // 24 hours

      // Create new user
      user = new User({
        email,
        password,
        firstName,
        lastName,
        company,
        verificationToken,
        verificationTokenExpires,
      });

      // Save user to database
      await user.save();

      // TODO: Send verification email

      // Generate tokens
      const token = user.generateAuthToken();
      const refreshToken = user.generateRefreshToken();

      res.status(201).json({
        message: 'User registered successfully. Please verify your email.',
        token,
        refreshToken,
        user: {
          id: user._id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          fullName: user.fullName,
          isEmailVerified: user.isEmailVerified,
          subscription: user.subscription.tier,
          role: user.role,
        },
      });
    } catch (error) {
      console.error('Registration error:', error);
      res.status(500).json({ message: 'Server error during registration' });
    }
  }
);

/**
 * @route   POST api/auth/login
 * @desc    Authenticate user & get token
 * @access  Public
 */
router.post(
  '/login',
  [
    check('email', 'Please include a valid email').isEmail(),
    check('password', 'Password is required').exists(),
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, password } = req.body;

    try {
      // Check if user exists
      const user = await User.findOne({ email }).select('+password');
      if (!user) {
        return res.status(400).json({ message: 'Invalid credentials' });
      }

      // Check if password matches
      const isMatch = await user.matchPassword(password);
      if (!isMatch) {
        return res.status(400).json({ message: 'Invalid credentials' });
      }

      // Check if user is active
      if (!user.isActive) {
        return res.status(403).json({ message: 'Account is deactivated' });
      }

      // Check if user is banned
      if (user.isBanned) {
        return res.status(403).json({ message: 'Account is banned' });
      }

      // Update last login
      user.lastLogin = Date.now();
      await user.save();

      // Generate tokens
      const token = user.generateAuthToken();
      const refreshToken = user.generateRefreshToken();

      res.json({
        token,
        refreshToken,
        user: {
          id: user._id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          fullName: user.fullName,
          isEmailVerified: user.isEmailVerified,
          subscription: user.subscription.tier,
          role: user.role,
        },
      });
    } catch (error) {
      console.error('Login error:', error);
      res.status(500).json({ message: 'Server error during login' });
    }
  }
);

/**
 * @route   GET api/auth/verify/:token
 * @desc    Verify user email
 * @access  Public
 */
router.get('/verify/:token', async (req, res) => {
  try {
    // Find user with verification token
    const user = await User.findOne({
      verificationToken: req.params.token,
      verificationTokenExpires: { $gt: Date.now() },
    });

    if (!user) {
      return res.status(400).json({ message: 'Invalid or expired verification token' });
    }

    // Update user
    user.isEmailVerified = true;
    user.verificationToken = undefined;
    user.verificationTokenExpires = undefined;
    await user.save();

    res.json({ message: 'Email verified successfully' });
  } catch (error) {
    console.error('Verification error:', error);
    res.status(500).json({ message: 'Server error during verification' });
  }
});

/**
 * @route   POST api/auth/forgot-password
 * @desc    Request password reset
 * @access  Public
 */
router.post(
  '/forgot-password',
  [check('email', 'Please include a valid email').isEmail()],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const user = await User.findOne({ email: req.body.email });
      if (!user) {
        // For security reasons, don't reveal that the email doesn't exist
        return res.status(200).json({ message: 'Password reset email sent if account exists' });
      }

      // Generate reset token
      const resetToken = crypto.randomBytes(20).toString('hex');
      user.resetPasswordToken = resetToken;
      user.resetPasswordExpires = Date.now() + 3600000; // 1 hour

      await user.save();

      // TODO: Send password reset email

      res.status(200).json({ message: 'Password reset email sent' });
    } catch (error) {
      console.error('Forgot password error:', error);
      res.status(500).json({ message: 'Server error during password reset request' });
    }
  }
);

/**
 * @route   POST api/auth/reset-password/:token
 * @desc    Reset password
 * @access  Public
 */
router.post(
  '/reset-password/:token',
  [check('password', 'Password must be at least 8 characters long').isLength({ min: 8 })],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      // Find user with reset token
      const user = await User.findOne({
        resetPasswordToken: req.params.token,
        resetPasswordExpires: { $gt: Date.now() },
      });

      if (!user) {
        return res.status(400).json({ message: 'Invalid or expired reset token' });
      }

      // Update password
      user.password = req.body.password;
      user.resetPasswordToken = undefined;
      user.resetPasswordExpires = undefined;
      await user.save();

      // TODO: Send password changed confirmation email

      res.json({ message: 'Password reset successful' });
    } catch (error) {
      console.error('Reset password error:', error);
      res.status(500).json({ message: 'Server error during password reset' });
    }
  }
);

/**
 * @route   POST api/auth/refresh-token
 * @desc    Refresh access token
 * @access  Public (with refresh token)
 */
router.post('/refresh-token', async (req, res) => {
  const { refreshToken } = req.body;

  if (!refreshToken) {
    return res.status(401).json({ message: 'Refresh token is required' });
  }

  try {
    // Verify refresh token
    const decoded = jwt.verify(refreshToken, config.jwt.refreshSecret);

    // Get user
    const user = await User.findById(decoded.id);
    if (!user) {
      return res.status(401).json({ message: 'Invalid refresh token' });
    }

    // Check if user is active and not banned
    if (!user.isActive || user.isBanned) {
      return res.status(403).json({ message: 'Account is deactivated or banned' });
    }

    // Generate new tokens
    const newToken = user.generateAuthToken();
    const newRefreshToken = user.generateRefreshToken();

    res.json({
      token: newToken,
      refreshToken: newRefreshToken,
    });
  } catch (error) {
    console.error('Refresh token error:', error);
    res.status(401).json({ message: 'Invalid or expired refresh token' });
  }
});

/**
 * @route   GET api/auth/me
 * @desc    Get current user
 * @access  Private
 */
router.get('/me', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    res.json(user);
  } catch (error) {
    console.error('Get current user error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

/**
 * @route   PUT api/auth/change-password
 * @desc    Change password
 * @access  Private
 */
router.put(
  '/change-password',
  [
    auth,
    check('currentPassword', 'Current password is required').exists(),
    check('newPassword', 'New password must be at least 8 characters long').isLength({ min: 8 }),
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const user = await User.findById(req.user.id).select('+password');
      if (!user) {
        return res.status(404).json({ message: 'User not found' });
      }

      // Check if current password matches
      const isMatch = await user.matchPassword(req.body.currentPassword);
      if (!isMatch) {
        return res.status(400).json({ message: 'Current password is incorrect' });
      }

      // Update password
      user.password = req.body.newPassword;
      await user.save();

      res.json({ message: 'Password changed successfully' });
    } catch (error) {
      console.error('Change password error:', error);
      res.status(500).json({ message: 'Server error during password change' });
    }
  }
);

/**
 * @route   POST api/auth/logout
 * @desc    Logout user (client-side only)
 * @access  Public
 */
router.post('/logout', (req, res) => {
  // JWT is stateless, so logout is handled client-side by removing the token
  // This endpoint is for consistency and potential future server-side logout functionality
  res.json({ message: 'Logged out successfully' });
});

/**
 * --------------------------------------------------------------------------
 * Google OAuth Routes
 * --------------------------------------------------------------------------
 */

/**
 * @route   GET api/auth/google
 * @desc    Initiate Google OAuth
 * @access  Public
 */
router.get(
  '/google',
  passport.authenticate('google', {
    scope: ['profile', 'email'],
    session: false,
  })
);

/**
 * @route   GET api/auth/google/callback
 * @desc    Google OAuth callback
 * @access  Public
 */
router.get(
  '/google/callback',
  passport.authenticate('google', {
    session: false,
    failureRedirect: '/login', // Front-end route for failure
  }),
  async (req, res) => {
    try {
      // Passport sets req.user
      const user = req.user;

      // Generate JWT + refresh token
      const token = user.generateAuthToken();
      const refreshToken = user.generateRefreshToken();

      // In a traditional web app we'd redirect. In SPA we can close window
      // or send data for the opener window to consume.
      // For Factory we simply return JSON the client JS can handle.
      res.set(
        'Content-Type',
        'text/html; charset=utf-8'
      ).send(`
        <script>
          (function() {
            window.opener && window.opener.postMessage(
              ${JSON.stringify({
                token,
                refreshToken,
                user: {
                  id: user._id,
                  email: user.email,
                  firstName: user.firstName,
                  lastName: user.lastName,
                  fullName: user.fullName,
                  isEmailVerified: user.isEmailVerified,
                  subscription: user.subscription.tier,
                  role: user.role,
                },
              })},
              '*'
            );
            window.close();
          })();
        </script>
      `);
    } catch (error) {
      console.error('Google OAuth callback error:', error);
      res.status(500).json({ message: 'Server error during Google OAuth' });
    }
  }
);

module.exports = router;
