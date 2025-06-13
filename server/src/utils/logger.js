/**
 * Logger Utility
 * 
 * A simple logging utility that provides consistent logging throughout the application.
 * Features:
 * - Different log levels (error, warn, info, debug)
 * - Timestamp formatting
 * - Environment-based configuration
 * - Structured logging with metadata
 * - Console-based logging with proper formatting
 * - Error stack trace preservation
 */

// Log levels with numeric values for comparison
const LOG_LEVELS = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3
};

// Default minimum log level based on environment
const DEFAULT_LOG_LEVEL = process.env.NODE_ENV === 'production' 
  ? LOG_LEVELS.INFO 
  : LOG_LEVELS.DEBUG;

// Current log level (can be overridden)
let currentLogLevel = process.env.LOG_LEVEL 
  ? (LOG_LEVELS[process.env.LOG_LEVEL.toUpperCase()] || DEFAULT_LOG_LEVEL)
  : DEFAULT_LOG_LEVEL;

/**
 * Format the current timestamp
 * @returns {string} Formatted timestamp
 */
const getTimestamp = () => {
  return new Date().toISOString();
};

/**
 * Format a log message with timestamp and optional metadata
 * 
 * @param {string} level - Log level
 * @param {string} message - Log message
 * @param {Object} [metadata] - Optional metadata
 * @returns {Array} Arguments to pass to console methods
 */
const formatLogArgs = (level, message, metadata) => {
  const timestamp = getTimestamp();
  const prefix = `[${timestamp}] [${level}]`;
  
  if (metadata) {
    if (metadata instanceof Error) {
      // Special handling for Error objects to preserve stack trace
      return [
        `${prefix} ${message}`,
        '\n',
        metadata
      ];
    } else {
      // Format other metadata as JSON
      return [
        `${prefix} ${message}`,
        metadata
      ];
    }
  }
  
  return [`${prefix} ${message}`];
};

/**
 * Logger class with methods for different log levels
 */
class Logger {
  /**
   * Set the log level
   * 
   * @param {string} level - Log level (ERROR, WARN, INFO, DEBUG)
   */
  static setLogLevel(level) {
    if (LOG_LEVELS[level.toUpperCase()] !== undefined) {
      currentLogLevel = LOG_LEVELS[level.toUpperCase()];
    }
  }

  /**
   * Get the current log level
   * 
   * @returns {string} Current log level name
   */
  static getLogLevel() {
    return Object.keys(LOG_LEVELS).find(key => LOG_LEVELS[key] === currentLogLevel);
  }

  /**
   * Log an error message
   * 
   * @param {string} message - Error message
   * @param {Object|Error} [metadata] - Additional context or Error object
   */
  static error(message, metadata) {
    if (currentLogLevel >= LOG_LEVELS.ERROR) {
      console.error(...formatLogArgs('ERROR', message, metadata));
    }
  }

  /**
   * Log a warning message
   * 
   * @param {string} message - Warning message
   * @param {Object} [metadata] - Additional context
   */
  static warn(message, metadata) {
    if (currentLogLevel >= LOG_LEVELS.WARN) {
      console.warn(...formatLogArgs('WARN', message, metadata));
    }
  }

  /**
   * Log an info message
   * 
   * @param {string} message - Info message
   * @param {Object} [metadata] - Additional context
   */
  static info(message, metadata) {
    if (currentLogLevel >= LOG_LEVELS.INFO) {
      console.info(...formatLogArgs('INFO', message, metadata));
    }
  }

  /**
   * Log a debug message
   * 
   * @param {string} message - Debug message
   * @param {Object} [metadata] - Additional context
   */
  static debug(message, metadata) {
    if (currentLogLevel >= LOG_LEVELS.DEBUG) {
      console.debug(...formatLogArgs('DEBUG', message, metadata));
    }
  }

  /**
   * Log a message with custom level and formatting
   * 
   * @param {Object} options - Log options
   * @param {string} options.level - Log level
   * @param {string} options.message - Log message
   * @param {Object} [options.metadata] - Additional context
   * @param {Function} [options.formatter] - Custom formatter function
   */
  static log(options) {
    const { level = 'INFO', message, metadata, formatter } = options;
    const logLevel = LOG_LEVELS[level.toUpperCase()] || LOG_LEVELS.INFO;
    
    if (currentLogLevel >= logLevel) {
      if (formatter && typeof formatter === 'function') {
        console.log(formatter(level, message, metadata));
      } else {
        console.log(...formatLogArgs(level, message, metadata));
      }
    }
  }
}

module.exports = Logger;
