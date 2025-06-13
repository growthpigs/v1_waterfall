/**
 * Custom API Error class for consistent error handling across the application
 * Extends the built-in Error class with additional properties for API errors
 */
class ApiError extends Error {
  /**
   * Create a new API error
   * 
   * @param {number} statusCode - HTTP status code
   * @param {string} message - Error message
   * @param {Object} [data=null] - Additional error data/context
   * @param {boolean} [isOperational=true] - Whether this is an operational error
   */
  constructor(statusCode, message, data = null, isOperational = true) {
    super(message);
    
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    this.data = data;
    this.name = this.constructor.name;
    
    // Capture stack trace (excludes the constructor call from the stack)
    Error.captureStackTrace(this, this.constructor);
  }

  /**
   * Create a 400 Bad Request error
   * 
   * @param {string} message - Error message
   * @param {Object} [data=null] - Additional error data
   * @returns {ApiError} - Bad request error
   */
  static badRequest(message = 'Bad request', data = null) {
    return new ApiError(400, message, data);
  }

  /**
   * Create a 401 Unauthorized error
   * 
   * @param {string} message - Error message
   * @param {Object} [data=null] - Additional error data
   * @returns {ApiError} - Unauthorized error
   */
  static unauthorized(message = 'Unauthorized', data = null) {
    return new ApiError(401, message, data);
  }

  /**
   * Create a 403 Forbidden error
   * 
   * @param {string} message - Error message
   * @param {Object} [data=null] - Additional error data
   * @returns {ApiError} - Forbidden error
   */
  static forbidden(message = 'Forbidden', data = null) {
    return new ApiError(403, message, data);
  }

  /**
   * Create a 404 Not Found error
   * 
   * @param {string} message - Error message
   * @param {Object} [data=null] - Additional error data
   * @returns {ApiError} - Not found error
   */
  static notFound(message = 'Resource not found', data = null) {
    return new ApiError(404, message, data);
  }

  /**
   * Create a 409 Conflict error
   * 
   * @param {string} message - Error message
   * @param {Object} [data=null] - Additional error data
   * @returns {ApiError} - Conflict error
   */
  static conflict(message = 'Resource conflict', data = null) {
    return new ApiError(409, message, data);
  }

  /**
   * Create a 422 Unprocessable Entity error
   * 
   * @param {string} message - Error message
   * @param {Object} [data=null] - Additional error data
   * @returns {ApiError} - Validation error
   */
  static validationError(message = 'Validation failed', data = null) {
    return new ApiError(422, message, data);
  }

  /**
   * Create a 500 Internal Server Error
   * 
   * @param {string} message - Error message
   * @param {Object} [data=null] - Additional error data
   * @param {boolean} [isOperational=true] - Whether this is an operational error
   * @returns {ApiError} - Server error
   */
  static internal(message = 'Internal server error', data = null, isOperational = true) {
    return new ApiError(500, message, data, isOperational);
  }

  /**
   * Create a 503 Service Unavailable error
   * 
   * @param {string} message - Error message
   * @param {Object} [data=null] - Additional error data
   * @returns {ApiError} - Service unavailable error
   */
  static serviceUnavailable(message = 'Service unavailable', data = null) {
    return new ApiError(503, message, data);
  }

  /**
   * Create a programming error (non-operational)
   * 
   * @param {string} message - Error message
   * @param {Object} [data=null] - Additional error data
   * @returns {ApiError} - Programming error
   */
  static programmingError(message = 'Programming error', data = null) {
    return new ApiError(500, message, data, false);
  }
}

module.exports = ApiError;
