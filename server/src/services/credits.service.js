/**
 * Credits Service
 * 
 * Handles all operations related to the Ops Credits system:
 * - Credit purchases
 * - Credit usage
 * - Balance management
 * - Transaction logging
 */

const mongoose = require('mongoose');
const { OperationCost, CreditPackage, CreditTransaction, UserCreditBalance } = require('../models/ops-credit.model');
const User = require('../models/user.model');
const ApiError = require('../utils/ApiError');
const logger = require('../utils/logger');

class CreditsService {
  /**
   * Get a user's current credit balance
   * 
   * @param {string} userId - User ID
   * @returns {Promise<Object>} - User credit balance information
   */
  async getUserBalance(userId) {
    try {
      /* ------------------------------------------------------------------
       * Demo user shortcut:
       * If the request comes from the hard-coded demo user (`demo-user-123`)
       * we return an in-memory mock balance so that the rest of the credits
       * system works without touching the database.
       * ----------------------------------------------------------------- */
      if (userId === 'demo-user-123') {
        const now = new Date();
        return {
          user: 'demo-user-123',
          balance: 1000,
          totalPurchased: 1000,
          totalUsed: 0,
          lowBalanceThreshold: 100,
          lowBalanceNotificationsEnabled: true,
          lastTransaction: now,
          createdAt: now,
          updatedAt: now
        };
      }

      let userBalance = await UserCreditBalance.findOne({ user: userId });
      
      // If no balance record exists, create one with zero balance
      if (!userBalance) {
        userBalance = await this.initializeUserBalance(userId);
      }
      
      return userBalance;
    } catch (error) {
      logger.error(`Error getting user balance: ${error.message}`, { userId, error });
      throw new ApiError(500, 'Failed to retrieve credit balance');
    }
  }

  /**
   * Initialize a new user's credit balance
   * 
   * @param {string} userId - User ID
   * @returns {Promise<Object>} - Created user credit balance
   */
  async initializeUserBalance(userId) {
    try {
      // Verify user exists
      const userExists = await User.exists({ _id: userId });
      if (!userExists) {
        throw new ApiError(404, 'User not found');
      }

      // Create new balance record
      const userBalance = await UserCreditBalance.create({
        user: userId,
        balance: 0,
        totalPurchased: 0,
        totalUsed: 0
      });

      return userBalance;
    } catch (error) {
      logger.error(`Error initializing user balance: ${error.message}`, { userId, error });
      throw new ApiError(500, 'Failed to initialize credit balance');
    }
  }

  /**
   * Check if a user has enough credits for an operation
   * 
   * @param {string} userId - User ID
   * @param {string} operationId - Operation ID
   * @returns {Promise<{hasEnoughCredits: boolean, requiredCredits: number, userBalance: number}>}
   */
  async checkUserCredits(userId, operationId) {
    try {
      // Get operation cost
      const operation = await OperationCost.findOne({ operationId, isActive: true });
      if (!operation) {
        throw new ApiError(404, 'Operation not found or inactive');
      }

      // Get user balance
      const userBalance = await this.getUserBalance(userId);
      
      return {
        hasEnoughCredits: userBalance.balance >= operation.creditCost,
        requiredCredits: operation.creditCost,
        userBalance: userBalance.balance,
        shortfall: Math.max(0, operation.creditCost - userBalance.balance)
      };
    } catch (error) {
      logger.error(`Error checking user credits: ${error.message}`, { userId, operationId, error });
      throw error instanceof ApiError ? error : new ApiError(500, 'Failed to check credit balance');
    }
  }

  /**
   * Use credits for an operation
   * 
   * @param {string} userId - User ID
   * @param {string} operationId - Operation ID
   * @param {Object} metadata - Additional metadata about the operation
   * @returns {Promise<Object>} - Transaction details
   */
  async useCredits(userId, operationId, metadata = {}) {
    const session = await mongoose.startSession();
    session.startTransaction();

    try {
      // Get operation cost
      const operation = await OperationCost.findOne({ operationId, isActive: true });
      if (!operation) {
        throw new ApiError(404, 'Operation not found or inactive');
      }

      // Get user balance
      const userBalance = await UserCreditBalance.findOne({ user: userId }).session(session);
      if (!userBalance) {
        throw new ApiError(404, 'User credit balance not found');
      }

      // Check if user has enough credits
      if (userBalance.balance < operation.creditCost) {
        throw new ApiError(402, 'Insufficient credits', {
          requiredCredits: operation.creditCost,
          userBalance: userBalance.balance,
          shortfall: operation.creditCost - userBalance.balance
        });
      }

      // Update user balance
      const newBalance = userBalance.balance - operation.creditCost;
      userBalance.balance = newBalance;
      userBalance.totalUsed += operation.creditCost;
      userBalance.lastTransaction = new Date();
      await userBalance.save({ session });

      // Create transaction record
      const transaction = await CreditTransaction.create([{
        user: userId,
        type: 'usage',
        amount: -operation.creditCost,
        balanceAfter: newBalance,
        operation: operationId,
        metadata: {
          operationName: operation.displayName,
          category: operation.category,
          ...metadata
        }
      }], { session });

      // Check if balance is below threshold and user should be notified
      const shouldNotify = userBalance.lowBalanceNotificationsEnabled && 
                          userBalance.balance <= userBalance.lowBalanceThreshold &&
                          (!userBalance.lastLowBalanceNotification || 
                           new Date() - userBalance.lastLowBalanceNotification > 24 * 60 * 60 * 1000);
      
      if (shouldNotify) {
        userBalance.lastLowBalanceNotification = new Date();
        await userBalance.save({ session });
        // Note: Actual notification would be handled by a separate notification service
        logger.info(`Low balance notification triggered for user ${userId}`);
      }

      await session.commitTransaction();
      
      return {
        transaction: transaction[0],
        newBalance,
        operationCost: operation.creditCost,
        lowBalance: shouldNotify
      };
    } catch (error) {
      await session.abortTransaction();
      logger.error(`Error using credits: ${error.message}`, { userId, operationId, error });
      throw error instanceof ApiError ? error : new ApiError(500, 'Failed to process credit usage');
    } finally {
      session.endSession();
    }
  }

  /**
   * Add credits to user balance (from purchase or other sources)
   * 
   * @param {string} userId - User ID
   * @param {number} amount - Amount of credits to add
   * @param {string} type - Transaction type ('purchase', 'adjustment', 'subscription_allocation', etc.)
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} - Transaction details
   */
  async addCredits(userId, amount, type = 'purchase', options = {}) {
    if (amount <= 0) {
      throw new ApiError(400, 'Credit amount must be positive');
    }

    const session = await mongoose.startSession();
    session.startTransaction();

    try {
      // Get or create user balance
      let userBalance = await UserCreditBalance.findOne({ user: userId }).session(session);
      if (!userBalance) {
        userBalance = await this.initializeUserBalance(userId);
      }

      // Update user balance
      const newBalance = userBalance.balance + amount;
      userBalance.balance = newBalance;
      
      if (type === 'purchase') {
        userBalance.totalPurchased += amount;
      }
      
      userBalance.lastTransaction = new Date();
      await userBalance.save({ session });

      // Create transaction record
      const transactionData = {
        user: userId,
        type,
        amount,
        balanceAfter: newBalance,
        notes: options.notes || ''
      };

      // Add package reference if provided
      if (options.packageId) {
        transactionData.package = options.packageId;
      }

      // Add payment reference if provided
      if (options.paymentId) {
        transactionData.paymentId = options.paymentId;
      }

      // Add coupon reference if provided
      if (options.couponId) {
        transactionData.coupon = options.couponId;
      }

      // Add metadata if provided
      if (options.metadata) {
        transactionData.metadata = options.metadata;
      }

      const transaction = await CreditTransaction.create([transactionData], { session });

      await session.commitTransaction();
      
      return {
        transaction: transaction[0],
        newBalance
      };
    } catch (error) {
      await session.abortTransaction();
      logger.error(`Error adding credits: ${error.message}`, { userId, amount, type, error });
      throw error instanceof ApiError ? error : new ApiError(500, 'Failed to add credits');
    } finally {
      session.endSession();
    }
  }

  /**
   * Purchase credits using a credit package
   * 
   * @param {string} userId - User ID
   * @param {string} packageId - Credit package ID
   * @param {Object} paymentDetails - Payment details
   * @param {string} [couponId] - Optional coupon ID for discount
   * @returns {Promise<Object>} - Purchase details
   */
  async purchaseCredits(userId, packageId, paymentDetails, couponId = null) {
    try {
      // Get credit package
      const creditPackage = await CreditPackage.findOne({ _id: packageId, isActive: true });
      if (!creditPackage) {
        throw new ApiError(404, 'Credit package not found or inactive');
      }

      // Calculate total credits (including bonus)
      const totalCredits = creditPackage.creditAmount + creditPackage.bonusCredits;
      
      // Process payment (this would integrate with your payment provider)
      // This is a placeholder for actual payment processing
      const paymentResult = {
        success: true,
        id: `payment_${Date.now()}`,
        amount: creditPackage.basePrice,
        currency: creditPackage.currency
      };
      
      if (!paymentResult.success) {
        throw new ApiError(400, 'Payment processing failed');
      }

      // Add credits to user balance
      const result = await this.addCredits(userId, totalCredits, 'purchase', {
        packageId,
        paymentId: paymentResult.id,
        couponId,
        notes: `Purchased ${creditPackage.name} package`,
        metadata: {
          packageName: creditPackage.name,
          baseCredits: creditPackage.creditAmount,
          bonusCredits: creditPackage.bonusCredits,
          price: creditPackage.basePrice,
          currency: creditPackage.currency
        }
      });

      return {
        ...result,
        package: creditPackage,
        payment: paymentResult,
        totalCredits
      };
    } catch (error) {
      logger.error(`Error purchasing credits: ${error.message}`, { userId, packageId, error });
      throw error instanceof ApiError ? error : new ApiError(500, 'Failed to purchase credits');
    }
  }

  /**
   * Get user transaction history
   * 
   * @param {string} userId - User ID
   * @param {Object} options - Query options (pagination, filters)
   * @returns {Promise<Object>} - Transaction history with pagination
   */
  async getUserTransactions(userId, options = {}) {
    const { page = 1, limit = 10, type, startDate, endDate } = options;
    const skip = (page - 1) * limit;

    try {
      // Build query
      const query = { user: userId };
      
      // Add type filter if provided
      if (type) {
        query.type = type;
      }
      
      // Add date range filter if provided
      if (startDate || endDate) {
        query.createdAt = {};
        if (startDate) {
          query.createdAt.$gte = new Date(startDate);
        }
        if (endDate) {
          query.createdAt.$lte = new Date(endDate);
        }
      }

      // Execute query with pagination
      const transactions = await CreditTransaction.find(query)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit)
        .populate('package', 'name creditAmount bonusCredits')
        .populate('coupon', 'code discountValue');

      // Get total count for pagination
      const total = await CreditTransaction.countDocuments(query);

      return {
        transactions,
        pagination: {
          total,
          page,
          limit,
          pages: Math.ceil(total / limit)
        }
      };
    } catch (error) {
      logger.error(`Error getting user transactions: ${error.message}`, { userId, options, error });
      throw new ApiError(500, 'Failed to retrieve transaction history');
    }
  }

  /**
   * Get all available credit packages
   * 
   * @returns {Promise<Array>} - Available credit packages
   */
  async getCreditPackages() {
    try {
      return await CreditPackage.find({ isActive: true }).sort({ sortOrder: 1 });
    } catch (error) {
      logger.error(`Error getting credit packages: ${error.message}`, { error });
      throw new ApiError(500, 'Failed to retrieve credit packages');
    }
  }

  /**
   * Get all operation costs
   * 
   * @param {Object} filters - Optional filters (category, etc.)
   * @returns {Promise<Array>} - Operation costs
   */
  async getOperationCosts(filters = {}) {
    try {
      const query = { isActive: true };
      
      // Add category filter if provided
      if (filters.category) {
        query.category = filters.category;
      }
      
      return await OperationCost.find(query).sort({ category: 1, creditCost: 1 });
    } catch (error) {
      logger.error(`Error getting operation costs: ${error.message}`, { filters, error });
      throw new ApiError(500, 'Failed to retrieve operation costs');
    }
  }

  /**
   * Get cost for a specific operation
   * 
   * @param {string} operationId - Operation ID
   * @returns {Promise<Object>} - Operation cost details
   */
  async getOperationCost(operationId) {
    try {
      const operation = await OperationCost.findOne({ operationId, isActive: true });
      if (!operation) {
        throw new ApiError(404, 'Operation not found or inactive');
      }
      return operation;
    } catch (error) {
      logger.error(`Error getting operation cost: ${error.message}`, { operationId, error });
      throw error instanceof ApiError ? error : new ApiError(500, 'Failed to retrieve operation cost');
    }
  }

  /**
   * Update an operation cost (admin only)
   * 
   * @param {string} operationId - Operation ID
   * @param {Object} updates - Fields to update
   * @returns {Promise<Object>} - Updated operation cost
   */
  async updateOperationCost(operationId, updates) {
    try {
      // Only allow updating specific fields
      const allowedUpdates = ['creditCost', 'displayName', 'description', 'isActive', 'config'];
      const updateData = {};
      
      Object.keys(updates).forEach(key => {
        if (allowedUpdates.includes(key)) {
          updateData[key] = updates[key];
        }
      });
      
      const operation = await OperationCost.findOneAndUpdate(
        { operationId },
        { $set: updateData },
        { new: true, runValidators: true }
      );
      
      if (!operation) {
        throw new ApiError(404, 'Operation not found');
      }
      
      return operation;
    } catch (error) {
      logger.error(`Error updating operation cost: ${error.message}`, { operationId, updates, error });
      throw error instanceof ApiError ? error : new ApiError(500, 'Failed to update operation cost');
    }
  }

  /**
   * Create a new operation cost (admin only)
   * 
   * @param {Object} operationData - Operation data
   * @returns {Promise<Object>} - Created operation cost
   */
  async createOperationCost(operationData) {
    try {
      // Check if operation ID already exists
      const exists = await OperationCost.exists({ operationId: operationData.operationId });
      if (exists) {
        throw new ApiError(409, 'Operation ID already exists');
      }
      
      return await OperationCost.create(operationData);
    } catch (error) {
      logger.error(`Error creating operation cost: ${error.message}`, { operationData, error });
      throw error instanceof ApiError ? error : new ApiError(500, 'Failed to create operation cost');
    }
  }

  /**
   * Update a credit package (admin only)
   * 
   * @param {string} packageId - Package ID
   * @param {Object} updates - Fields to update
   * @returns {Promise<Object>} - Updated credit package
   */
  async updateCreditPackage(packageId, updates) {
    try {
      // Only allow updating specific fields
      const allowedUpdates = ['name', 'creditAmount', 'basePrice', 'bonusCredits', 'isActive', 'isFeatured', 'sortOrder', 'description'];
      const updateData = {};
      
      Object.keys(updates).forEach(key => {
        if (allowedUpdates.includes(key)) {
          updateData[key] = updates[key];
        }
      });
      
      const creditPackage = await CreditPackage.findByIdAndUpdate(
        packageId,
        { $set: updateData },
        { new: true, runValidators: true }
      );
      
      if (!creditPackage) {
        throw new ApiError(404, 'Credit package not found');
      }
      
      return creditPackage;
    } catch (error) {
      logger.error(`Error updating credit package: ${error.message}`, { packageId, updates, error });
      throw error instanceof ApiError ? error : new ApiError(500, 'Failed to update credit package');
    }
  }

  /**
   * Create a new credit package (admin only)
   * 
   * @param {Object} packageData - Package data
   * @returns {Promise<Object>} - Created credit package
   */
  async createCreditPackage(packageData) {
    try {
      return await CreditPackage.create(packageData);
    } catch (error) {
      logger.error(`Error creating credit package: ${error.message}`, { packageData, error });
      throw new ApiError(500, 'Failed to create credit package');
    }
  }

  /**
   * Manually adjust a user's credit balance (admin only)
   * 
   * @param {string} userId - User ID
   * @param {number} amount - Amount to adjust (positive or negative)
   * @param {string} reason - Reason for adjustment
   * @returns {Promise<Object>} - Adjustment details
   */
  async adjustUserBalance(userId, amount, reason) {
    if (amount === 0) {
      throw new ApiError(400, 'Adjustment amount cannot be zero');
    }

    const session = await mongoose.startSession();
    session.startTransaction();

    try {
      // Get user balance
      const userBalance = await UserCreditBalance.findOne({ user: userId }).session(session);
      if (!userBalance) {
        throw new ApiError(404, 'User credit balance not found');
      }

      // Check if adjustment would make balance negative
      if (userBalance.balance + amount < 0) {
        throw new ApiError(400, 'Adjustment would result in negative balance');
      }

      // Update user balance
      const newBalance = userBalance.balance + amount;
      userBalance.balance = newBalance;
      userBalance.lastTransaction = new Date();
      await userBalance.save({ session });

      // Create transaction record
      const transaction = await CreditTransaction.create([{
        user: userId,
        type: 'adjustment',
        amount,
        balanceAfter: newBalance,
        notes: reason || 'Administrative adjustment'
      }], { session });

      await session.commitTransaction();
      
      return {
        transaction: transaction[0],
        previousBalance: userBalance.balance - amount,
        newBalance,
        adjustment: amount
      };
    } catch (error) {
      await session.abortTransaction();
      logger.error(`Error adjusting user balance: ${error.message}`, { userId, amount, reason, error });
      throw error instanceof ApiError ? error : new ApiError(500, 'Failed to adjust credit balance');
    } finally {
      session.endSession();
    }
  }
}

module.exports = new CreditsService();
