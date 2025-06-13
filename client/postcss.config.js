/**
 * PostCSS configuration
 * 
 * Tailwind CSS’s PostCSS plugin moved to a separate package
 * (`@tailwindcss/postcss`).  Loading it via `require()` avoids
 * the “trying to use tailwindcss directly as a PostCSS plugin”
 * error thrown by CRA’s build pipeline.
 */

module.exports = {
  // Standard CRA-compatible PostCSS plugin notation
  plugins: [
    // Use the dedicated Tailwind PostCSS shim to avoid
    // “trying to use tailwindcss directly as a PostCSS plugin” errors.
    require('@tailwindcss/postcss'),
    require('autoprefixer'),
  ],
};
