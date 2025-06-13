const express = require('express');
const router = express.Router();
const { body, query, param, validationResult } = require('express-validator');
const creditsService = require('../../services/credits.service');
const auth = require('../../middlewares/auth.middleware');
const authorize = require('../../middlewares/authorize.middleware');
const ApiError = require('../../utils/ApiError');

// Validation middleware
const validate = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  next();
};

/**
 * @route GET /api/credits/balance
 * @description Get current user's credit balance
 * @access Private
 */
router.get('/balance', auth(), async (req, res, next) => {
  try {
    const balance = await creditsService.getUserBalance(req.user.id);
    res.json(balance);
  } catch (error) {
    next(error);
  }
});

/**
 * @route GET /api/credits/packages
 * @description Get available credit packages
 * @access Public
 */
router.get('/packages', async (req, res, next) => {
  try {
    const packages = await creditsService.getCreditPackages();
    res.json(packages);
  } catch (error) {
    next(error);
  }
});

/**
 * @route GET /api/credits/operations
 * @description Get operation costs
 * @access Public
 */
router.get('/operations', async (req, res, next) => {
  try {
    const { category } = req.query;
    const operations = await creditsService.getOperationCosts({ category });
    res.json(operations);
  } catch (error) {
    next(error);
  }
});

/**
 * @route GET /api/credits/operations/:operationId
 * @description Get specific operation cost
 * @access Public
 */
router.get('/operations/:operationId', async (req, res, next) => {
  try {
    const operation = await creditsService.getOperationCost(req.params.operationId);
    res.json(operation);
  } catch (error) {
    next(error);
  }
});

/**
 * @route GET /api/credits/check/:operationId
 * @description Check if user has enough credits for an operation
 * @access Private
 */
router.get('/check/:operationId', auth(), async (req, res, next) => {
  try {
    const result = await creditsService.checkUserCredits(req.user.id, req.params.operationId);
    res.json(result);
  } catch (error) {
    next(error);
  }
});

/**
 * @route POST /api/credits/use/:operationId
 * @description Use credits for an operation
 * @access Private
 */
router.post(
  '/use/:operationId',
  auth(),
  [
    param('operationId').notEmpty().withMessage('Operation ID is required'),
    body('metadata').optional().isObject().withMessage('Metadata must be an object')
  ],
  validate,
  async (req, res, next) => {
    try {
      const result = await creditsService.useCredits(
        req.user.id,
        req.params.operationId,
        req.body.metadata || {}
      );
      res.json(result);
    } catch (error) {
      if (error instanceof ApiError && error.statusCode === 402) {
        // Special handling for insufficient credits
        return res.status(402).json({
          message: error.message,
          ...error.details
        });
      }
      next(error);
    }
  }
);

/**
 * @route POST /api/credits/purchase
 * @description Purchase credits using a credit package
 * @access Private
 */
router.post(
  '/purchase',
  auth(),
  [
    body('packageId').notEmpty().withMessage('Package ID is required'),
    body('paymentDetails').isObject().withMessage('Payment details are required'),
    body('couponId').optional()
  ],
  validate,
  async (req, res, next) => {
    try {
      const result = await creditsService.purchaseCredits(
        req.user.id,
        req.body.packageId,
        req.body.paymentDetails,
        req.body.couponId || null
      );
      res.json(result);
    } catch (error) {
      next(error);
    }
  }
);

/**
 * @route GET /api/credits/transactions
 * @description Get user transaction history
 * @access Private
 */
router.get(
  '/transactions',
  auth(),
  [
    query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
    query('type').optional().isIn(['purchase', 'usage', 'refund', 'adjustment', 'expiration', 'subscription_allocation']).withMessage('Invalid transaction type'),
    query('startDate').optional().isISO8601().withMessage('Start date must be a valid date'),
    query('endDate').optional().isISO8601().withMessage('End date must be a valid date')
  ],
  validate,
  async (req, res, next) => {
    try {
      const { page, limit, type, startDate, endDate } = req.query;
      const transactions = await creditsService.getUserTransactions(req.user.id, {
        page: parseInt(page) || 1,
        limit: parseInt(limit) || 10,
        type,
        startDate,
        endDate
      });
      res.json(transactions);
    } catch (error) {
      next(error);
    }
  }
);

// ==================== ADMIN ROUTES ====================

/**
 * @route GET /api/credits/admin/users/:userId/balance
 * @description Get a specific user's credit balance (admin only)
 * @access Admin
 */
router.get(
  '/admin/users/:userId/balance',
  auth(),
  authorize('admin', 'superadmin'),
  async (req, res, next) => {
    try {
      const balance = await creditsService.getUserBalance(req.params.userId);
      res.json(balance);
    } catch (error) {
      next(error);
    }
  }
);

/**
 * @route GET /api/credits/admin/users/:userId/transactions
 * @description Get a specific user's transaction history (admin only)
 * @access Admin
 */
router.get(
  '/admin/users/:userId/transactions',
  auth(),
  authorize('admin', 'superadmin'),
  [
    query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
    query('type').optional().isIn(['purchase', 'usage', 'refund', 'adjustment', 'expiration', 'subscription_allocation']).withMessage('Invalid transaction type'),
    query('startDate').optional().isISO8601().withMessage('Start date must be a valid date'),
    query('endDate').optional().isISO8601().withMessage('End date must be a valid date')
  ],
  validate,
  async (req, res, next) => {
    try {
      const { page, limit, type, startDate, endDate } = req.query;
      const transactions = await creditsService.getUserTransactions(req.params.userId, {
        page: parseInt(page) || 1,
        limit: parseInt(limit) || 10,
        type,
        startDate,
        endDate
      });
      res.json(transactions);
    } catch (error) {
      next(error);
    }
  }
);

/**
 * @route POST /api/credits/admin/operations
 * @description Create a new operation cost (admin only)
 * @access Admin
 */
router.post(
  '/admin/operations',
  auth(),
  authorize('admin', 'superadmin'),
  [
    body('operationId').notEmpty().withMessage('Operation ID is required'),
    body('displayName').notEmpty().withMessage('Display name is required'),
    body('category').isIn(['cia', 'seo', 'content', 'social', 'analysis', 'export']).withMessage('Invalid category'),
    body('creditCost').isInt({ min: 0 }).withMessage('Credit cost must be a non-negative integer'),
    body('description').optional(),
    body('isActive').optional().isBoolean().withMessage('isActive must be a boolean'),
    body('config').optional().isObject().withMessage('Config must be an object')
  ],
  validate,
  async (req, res, next) => {
    try {
      const operation = await creditsService.createOperationCost(req.body);
      res.status(201).json(operation);
    } catch (error) {
      next(error);
    }
  }
);

/**
 * @route PUT /api/credits/admin/operations/:operationId
 * @description Update an operation cost (admin only)
 * @access Admin
 */
router.put(
  '/admin/operations/:operationId',
  auth(),
  authorize('admin', 'superadmin'),
  [
    body('creditCost').optional().isInt({ min: 0 }).withMessage('Credit cost must be a non-negative integer'),
    body('displayName').optional().notEmpty().withMessage('Display name cannot be empty'),
    body('description').optional(),
    body('isActive').optional().isBoolean().withMessage('isActive must be a boolean'),
    body('config').optional().isObject().withMessage('Config must be an object')
  ],
  validate,
  async (req, res, next) => {
    try {
      const operation = await creditsService.updateOperationCost(req.params.operationId, req.body);
      res.json(operation);
    } catch (error) {
      next(error);
    }
  }
);

/**
 * @route POST /api/credits/admin/packages
 * @description Create a new credit package (admin only)
 * @access Admin
 */
router.post(
  '/admin/packages',
  auth(),
  authorize('admin', 'superadmin'),
  [
    body('name').notEmpty().withMessage('Name is required'),
    body('creditAmount').isInt({ min: 1 }).withMessage('Credit amount must be a positive integer'),
    body('basePrice').isInt({ min: 0 }).withMessage('Base price must be a non-negative integer'),
    body('currency').isIn(['EUR', 'USD', 'GBP']).withMessage('Invalid currency'),
    body('bonusCredits').optional().isInt({ min: 0 }).withMessage('Bonus credits must be a non-negative integer'),
    body('sortOrder').optional().isInt().withMessage('Sort order must be an integer'),
    body('isActive').optional().isBoolean().withMessage('isActive must be a boolean'),
    body('isFeatured').optional().isBoolean().withMessage('isFeatured must be a boolean'),
    body('description').optional()
  ],
  validate,
  async (req, res, next) => {
    try {
      const creditPackage = await creditsService.createCreditPackage(req.body);
      res.status(201).json(creditPackage);
    } catch (error) {
      next(error);
    }
  }
);

/**
 * @route PUT /api/credits/admin/packages/:packageId
 * @description Update a credit package (admin only)
 * @access Admin
 */
router.put(
  '/admin/packages/:packageId',
  auth(),
  authorize('admin', 'superadmin'),
  [
    body('name').optional().notEmpty().withMessage('Name cannot be empty'),
    body('creditAmount').optional().isInt({ min: 1 }).withMessage('Credit amount must be a positive integer'),
    body('basePrice').optional().isInt({ min: 0 }).withMessage('Base price must be a non-negative integer'),
    body('bonusCredits').optional().isInt({ min: 0 }).withMessage('Bonus credits must be a non-negative integer'),
    body('sortOrder').optional().isInt().withMessage('Sort order must be an integer'),
    body('isActive').optional().isBoolean().withMessage('isActive must be a boolean'),
    body('isFeatured').optional().isBoolean().withMessage('isFeatured must be a boolean'),
    body('description').optional()
  ],
  validate,
  async (req, res, next) => {
    try {
      const creditPackage = await creditsService.updateCreditPackage(req.params.packageId, req.body);
      res.json(creditPackage);
    } catch (error) {
      next(error);
    }
  }
);

/**
 * @route POST /api/credits/admin/users/:userId/adjust
 * @description Manually adjust a user's credit balance (admin only)
 * @access Admin
 */
router.post(
  '/admin/users/:userId/adjust',
  auth(),
  authorize('admin', 'superadmin'),
  [
    body('amount').isInt({ min: -1000000, max: 1000000 }).withMessage('Amount must be an integer between -1,000,000 and 1,000,000'),
    body('reason').notEmpty().withMessage('Reason is required')
  ],
  validate,
  async (req, res, next) => {
    try {
      const result = await creditsService.adjustUserBalance(
        req.params.userId,
        parseInt(req.body.amount),
        req.body.reason
      );
      res.json(result);
    } catch (error) {
      next(error);
    }
  }
);

module.exports = router;
