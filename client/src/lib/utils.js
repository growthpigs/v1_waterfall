import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge class names with Tailwind CSS classes priority handling
 * Combines clsx for conditional classes with tailwind-merge for proper class overrides
 * 
 * @param {...string} inputs - Class names to merge
 * @returns {string} - Merged class string
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Format a number as currency with the specified currency symbol
 * 
 * @param {number} amount - Amount to format
 * @param {string} [currency='€'] - Currency symbol
 * @param {string} [locale='en-US'] - Locale for number formatting
 * @returns {string} - Formatted currency string
 */
export function formatCurrency(amount, currency = '€', locale = 'en-US') {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency === '€' ? 'EUR' : 'USD',
    currencyDisplay: 'symbol',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount).replace(/^(\D+)/, currency);
}

/**
 * Generate a unique ID with optional prefix
 * Useful for form elements that require unique IDs
 * 
 * @param {string} [prefix='id'] - Prefix for the ID
 * @returns {string} - Unique ID string
 */
export function generateId(prefix = 'id') {
  return `${prefix}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Format a date with the specified format
 * 
 * @param {Date|string|number} date - Date to format
 * @param {string} [format='medium'] - Format style: 'short', 'medium', 'long', 'full'
 * @param {string} [locale='en-US'] - Locale for date formatting
 * @returns {string} - Formatted date string
 */
export function formatDate(date, format = 'medium', locale = 'en-US') {
  const dateObj = date instanceof Date ? date : new Date(date);
  return new Intl.DateTimeFormat(locale, {
    dateStyle: format,
  }).format(dateObj);
}

/**
 * Truncate text to specified length with ellipsis
 * 
 * @param {string} text - Text to truncate
 * @param {number} [length=50] - Maximum length before truncation
 * @returns {string} - Truncated text with ellipsis if needed
 */
export function truncateText(text, length = 50) {
  if (!text || text.length <= length) return text;
  return `${text.substring(0, length).trim()}...`;
}

/**
 * Debounce function to limit how often a function is called
 * 
 * @param {Function} fn - Function to debounce
 * @param {number} [delay=300] - Delay in milliseconds
 * @returns {Function} - Debounced function
 */
export function debounce(fn, delay = 300) {
  let timeoutId;
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}
