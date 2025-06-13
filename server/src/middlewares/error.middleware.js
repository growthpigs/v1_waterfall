/**
 * Error Handling Middleware
 * 
 * This module provides middleware functions for handling errors in the Express application:
 * - 404 Not Found handler for undefined routes
 * - Global error handler with support for different error types
 * - Environment-specific error responses
 */

const mongoose = require('mongoose');
const ApiError = require('../utils/ApiError');
const logger = require('../utils/logger');

/**
 * 404 Not Found middleware for handling undefined routes
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
const notFound = (req, res, next) => {
  const error = new ApiError(404, `Not Found - ${req.originalUrl}`);
  next(error);
};

/**
 * Global error handler middleware
 * Handles different types of errors and formats appropriate responses
 * 
 * @param {Error} err - Error object
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
const errorHandler = (err, req, res, next) => {
  let error = err;
  let statusCode = 500;
  let message = 'Server Error';
  let errorDetails = null;
  
  // Log the original error
  if (error instanceof ApiError) {
    logger.error(`API Error: ${error.message}`, error);
  } else {
    logger.error(`Unhandled Error: ${error.message}`, error);
  }

  // Convert known error types to ApiError
  if (error.name === 'ValidationError' && error instanceof mongoose.Error.ValidationError) {
    // Mongoose validation error
    statusCode = 400;
    message = 'Validation Error';
    errorDetails = Object.values(error.errors).map(err => ({
      field: err.path,
      message: err.message
    }));
    error = new ApiError(statusCode, message, errorDetails);
  } else if (error.name === 'MongoServerError' && error.code === 11000) {
    // MongoDB duplicate key error
    statusCode = 409;
    message = 'Duplicate Key Error';
    const field = Object.keys(error.keyValue)[0];
    errorDetails = { field, value: error.keyValue[field] };
    error = new ApiError(statusCode, `${field} already exists`, errorDetails);
  } else if (error.name === 'CastError' && error instanceof mongoose.Error.CastError) {
    // MongoDB invalid ID error
    statusCode = 400;
    message = 'Invalid ID Format';
    errorDetails = { field: error.path, value: error.value };
    error = new ApiError(statusCode, message, errorDetails);
  } else if (error.name === 'JsonWebTokenError') {
    // JWT errors
    statusCode = 401;
    message = 'Invalid Token';
    error = new ApiError(statusCode, message);
  } else if (error.name === 'TokenExpiredError') {
    // JWT expiration
    statusCode = 401;
    message = 'Token Expired';
    error = new ApiError(statusCode, message);
  } else if (error.type === 'entity.parse.failed') {
    // JSON parsing error
    statusCode = 400;
    message = 'Invalid JSON';
    error = new ApiError(statusCode, message);
  }

  // Use ApiError properties if available
  if (error instanceof ApiError) {
    statusCode = error.statusCode;
    message = error.message;
    errorDetails = error.data;
  }

  // Prepare response object
  const responseObj = {
    success: false,
    message
  };

  // Add error details based on environment
  if (process.env.NODE_ENV === 'development') {
    // Detailed error information for development
    responseObj.error = {
      statusCode,
      message: error.message,
      stack: error.stack,
      details: errorDetails
    };
  } else {
    // Minimal error information for production
    if (errorDetails) {
      responseObj.details = errorDetails;
    }
    
    // Only include stack in production for non-operational errors if they're not 4xx errors
    if (!error.isOperational && statusCode >= 500) {
      // Log the error with stack trace but don't send it to the client
      logger.error('Non-operational error occurred:', { 
        message: error.message,
        stack: error.stack
      });
    }
  }

  res.status(statusCode).json(responseObj);
};

module.exports = { notFound, errorHandler };
