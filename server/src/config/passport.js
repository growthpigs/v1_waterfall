const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const JwtStrategy = require('passport-jwt').Strategy;
const ExtractJwt = require('passport-jwt').ExtractJwt;
const User = require('../models/user.model');
const config = require('./index');

// Options for JWT strategy
const jwtOptions = {
  jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
  secretOrKey: config.jwt.secret,
};

// Configure JWT Strategy
passport.use(
  new JwtStrategy(jwtOptions, async (payload, done) => {
    try {
      // Find the user by ID from JWT payload
      const user = await User.findById(payload.id);
      
      if (!user) {
        return done(null, false, { message: 'User not found' });
      }
      
      // Check if user is active and not banned
      if (!user.isActive) {
        return done(null, false, { message: 'Account is deactivated' });
      }
      
      if (user.isBanned) {
        return done(null, false, { message: 'Account is banned' });
      }
      
      // User authenticated successfully
      return done(null, user);
    } catch (error) {
      return done(error, false);
    }
  })
);

// Configure Google OAuth Strategy
passport.use(
  new GoogleStrategy(
    {
      clientID: config.oauth?.google?.clientId || process.env.GOOGLE_CLIENT_ID,
      clientSecret: config.oauth?.google?.clientSecret || process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: config.oauth?.google?.callbackUrl || process.env.GOOGLE_CALLBACK_URL || '/api/auth/google/callback',
      scope: ['profile', 'email'],
    },
    async (accessToken, refreshToken, profile, done) => {
      try {
        // Check if user already exists
        let user = await User.findOne({ 'oauth.google.id': profile.id });
        
        if (user) {
          // Update user's Google profile data
          user.oauth = {
            ...user.oauth,
            google: {
              id: profile.id,
              email: profile.emails[0].value,
              name: profile.displayName,
              picture: profile.photos?.[0]?.value,
              accessToken,
              refreshToken,
              lastLogin: new Date()
            }
          };
          
          await user.save();
          return done(null, user);
        }
        
        // Check if user exists with same email
        user = await User.findOne({ email: profile.emails[0].value });
        
        if (user) {
          // Link Google account to existing user
          user.oauth = {
            ...user.oauth,
            google: {
              id: profile.id,
              email: profile.emails[0].value,
              name: profile.displayName,
              picture: profile.photos?.[0]?.value,
              accessToken,
              refreshToken,
              lastLogin: new Date()
            }
          };
          
          await user.save();
          return done(null, user);
        }
        
        // Create new user with Google profile
        const newUser = new User({
          email: profile.emails[0].value,
          firstName: profile.name?.givenName || profile.displayName.split(' ')[0],
          lastName: profile.name?.familyName || profile.displayName.split(' ').slice(1).join(' '),
          password: Math.random().toString(36).slice(-12) + Math.random().toString(36).slice(-12), // Random password
          isEmailVerified: true, // Email is verified through Google
          oauth: {
            google: {
              id: profile.id,
              email: profile.emails[0].value,
              name: profile.displayName,
              picture: profile.photos?.[0]?.value,
              accessToken,
              refreshToken,
              lastLogin: new Date()
            }
          }
        });
        
        await newUser.save();
        return done(null, newUser);
      } catch (error) {
        return done(error, false);
      }
    }
  )
);

// Serialize user to session
passport.serializeUser((user, done) => {
  done(null, user.id);
});

// Deserialize user from session
passport.deserializeUser(async (id, done) => {
  try {
    const user = await User.findById(id);
    done(null, user);
  } catch (error) {
    done(error, null);
  }
});

module.exports = passport;
