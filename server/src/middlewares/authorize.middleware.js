/**
 * Role-based authorization middleware
 * 
 * This middleware checks if the authenticated user has one of the required roles.
 * It must be used after the auth middleware which sets req.user.
 */

/**
 * Create a middleware that checks if user has one of the required roles
 * 
 * @param {...string} allowedRoles - Roles that are allowed to access the route
 * @returns {Function} Express middleware function
 */
const authorize = (...allowedRoles) => {
  // Convert arguments to array if single string is passed
  const roles = allowedRoles.flat();
  
  return (req, res, next) => {
    // Check if user is authenticated
    if (!req.user) {
      return res.status(401).json({ 
        message: 'Authentication required',
        error: 'No authenticated user found. The auth middleware must be used before this middleware.'
      });
    }

    // If no roles are specified, allow any authenticated user
    if (roles.length === 0) {
      return next();
    }

    // Check if user has one of the required roles
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ 
        message: 'Insufficient permissions',
        error: `This action requires one of these roles: ${roles.join(', ')}`,
        userRole: req.user.role
      });
    }

    // User has required role, proceed
    next();
  };
};

module.exports = authorize;
