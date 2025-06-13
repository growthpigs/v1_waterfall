const mongoose = require('mongoose');
const Schema = mongoose.Schema;

// Content generation status enum
const CONTENT_STATUS = {
  QUEUED: 'queued',
  GENERATING: 'generating',
  COMPLETED: 'completed',
  FAILED: 'failed'
};

// Military classification content types
const CONTENT_TYPES = {
  // Blog Content & Articles
  SNIPER: 'Long-form articles (precision-targeted, high-impact content)',
  RECON: 'Research articles (intelligence-gathering content)',
  PHANTOM: 'Pillar content (comprehensive cornerstone content)',
  BLACKOUT: 'Authority pieces (thought leadership content)',
  INTEL: 'Industry insights (market analysis reports)',
  OVERWATCH: 'Trend analysis (timely content on emerging trends)',
  CLASSIFIED: 'Exclusive content (premium subscriber content)',
  BRIEFING: 'Summary articles (concise overviews)',
  
  // Social Media Operations
  VIPER: 'Instagram posts (visual content with impact)',
  GHOST: 'Facebook content (engagement-focused posts)',
  TANGO: 'LinkedIn posts (professional networking content)',
  ECHO: 'Twitter/X posts (concise, shareable messages)',
  BRAVO: 'TikTok content (short-form video content)',
  DELTA: 'YouTube Shorts (brief video content)',
  FOXTROT: 'Pinterest posts (visual discovery content)',
  SIERRA: 'Snapchat content (ephemeral content)',
  
  // Video Content Arsenal
  APACHE: 'Brand videos (promotional content)',
  STEALTH: 'UGC videos (user-generated content)',
  PREDATOR: 'Video ads (targeted advertising)',
  BLACKHAWK: 'Testimonial videos (customer success stories)',
  COBRA: 'Product demos (feature demonstrations)',
  FALCON: 'Educational videos (informative content)',
  RAPTOR: 'Tutorial videos (instructional content)',
  HAWK: 'Behind-the-scenes (company culture content)',
  
  // Email & Communication
  CIPHER: 'Newsletters (regular subscriber communications)',
  WHISKEY: 'Email campaigns (targeted email sequences)',
  RADIO: 'Automated sequences (drip campaigns)',
  ALPHA: 'Welcome series (onboarding communications)',
  OSCAR: 'Promotional emails (sales communications)',
  UNIFORM: 'Template emails (standardized communications)',
  VICTOR: 'Victory emails (achievement announcements)',
  YANKEE: 'Announcement emails (important updates)',
  
  // Landing Pages & Web Operations
  FORTRESS: 'Landing pages (conversion-focused pages)',
  STRONGHOLD: 'Sales pages (revenue-generating pages)',
  BUNKER: 'Lead magnets (prospect-capturing resources)',
  OUTPOST: 'Thank you pages (post-conversion pages)',
  CHECKPOINT: 'Opt-in pages (subscriber acquisition pages)',
  BARRICADE: 'Squeeze pages (focused conversion pages)',
  WATCHTOWER: 'About pages (company information pages)',
  COMMAND: 'Homepage (main website entry point)',
  
  // Podcast & Audio Intelligence
  RADIO_SILENCE: 'Podcast episodes (audio content series)',
  TRANSMISSION: 'Audio ads (audio promotional content)',
  FREQUENCY: 'Voice content (voice-optimized content)',
  SIGNAL: 'Audio announcements (important audio updates)',
  BEACON: 'Audio guides (instructional audio content)',
  SONAR: 'Interview shows (conversation-based content)',
  RADAR: 'News podcasts (current events coverage)',
  
  // Special Operations Content
  BLACK_OPS: 'Confidential reports (exclusive analysis)',
  NIGHT_VISION: 'Dark social content (private sharing content)',
  INFILTRATE: 'Competitor analysis (competitive intelligence)',
  EXTRACTION: 'Data reports (insights from raw data)',
  SABOTAGE: 'Disruptive content (industry-challenging content)',
  AMBUSH: 'Surprise launches (unexpected content releases)',
  FLANKING: 'Alternative perspective content (unique viewpoints)',
  SIEGE: 'Long-term campaigns (sustained content pressure)',
  
  // Advanced Tactical Classifications
  GUNSHIP: 'Multi-format campaigns (cross-platform content)',
  SNATCH: 'Lead capture content (prospect acquisition content)',
  THUNDER: 'Viral content attempts (high-sharing potential content)',
  LIGHTNING: 'Rapid response content (timely reactive content)',
  TORNADO: 'Trending topic content (current events content)',
  HURRICANE: 'Major announcement content (significant updates)',
  EARTHQUAKE: 'Industry-shaking content (disruptive revelations)',
  AVALANCHE: 'Overwhelming content series (massive content deployment)'
};

// Content item schema
const contentItemSchema = new Schema({
  // Owner and source
  user: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  ciaReport: {
    type: Schema.Types.ObjectId,
    ref: 'CIAReport',
    required: true
  },
  
  // Content metadata
  title: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  contentType: {
    type: String,
    enum: Object.keys(CONTENT_TYPES),
    required: true
  },
  keywords: [{
    type: String,
    trim: true
  }],
  
  // Content parameters and style
  parameters: {
    type: Schema.Types.Mixed,
    default: {}
  },
  promptStyle: {
    type: String,
    trim: true
  },
  
  // Content data
  rawContent: {
    type: String
  },
  editedContent: {
    type: String
  },
  isEdited: {
    type: Boolean,
    default: false
  },
  
  // Generation status
  status: {
    type: String,
    enum: Object.values(CONTENT_STATUS),
    default: CONTENT_STATUS.QUEUED
  },
  progress: {
    type: Number,
    min: 0,
    max: 100,
    default: 0
  },
  errorMessage: String,
  
  // Regeneration tracking
  regeneratedAt: Date,
  regenerationCount: {
    type: Number,
    default: 0
  },
  
  // Export history
  exports: [{
    format: {
      type: String,
      enum: ['pdf', 'docx', 'notion', 'google_sheets', 'markdown', 'html']
    },
    url: String,
    createdAt: {
      type: Date,
      default: Date.now
    }
  }],
  
  // Performance metrics
  metrics: {
    views: {
      type: Number,
      default: 0
    },
    engagements: {
      type: Number,
      default: 0
    },
    clicks: {
      type: Number,
      default: 0
    },
    conversions: {
      type: Number,
      default: 0
    },
    shares: {
      type: Number,
      default: 0
    },
    likes: {
      type: Number,
      default: 0
    },
    comments: {
      type: Number,
      default: 0
    }
  },
  
  // Publishing information
  published: {
    isPublished: {
      type: Boolean,
      default: false
    },
    publishedAt: Date,
    scheduledFor: Date,
    platform: String,
    url: String
  },
  
  // Version history
  versions: [{
    content: String,
    createdAt: {
      type: Date,
      default: Date.now
    },
    description: String
  }],
  
  // Timestamps
  lastEditedAt: Date
}, {
  timestamps: true
});

// Virtual for content category
contentItemSchema.virtual('category').get(function() {
  const type = this.contentType;
  
  if (['SNIPER', 'RECON', 'PHANTOM', 'BLACKOUT', 'INTEL', 'OVERWATCH', 'CLASSIFIED', 'BRIEFING'].includes(type)) {
    return 'Blog Content & Articles';
  } else if (['VIPER', 'GHOST', 'TANGO', 'ECHO', 'BRAVO', 'DELTA', 'FOXTROT', 'SIERRA'].includes(type)) {
    return 'Social Media Operations';
  } else if (['APACHE', 'STEALTH', 'PREDATOR', 'BLACKHAWK', 'COBRA', 'FALCON', 'RAPTOR', 'HAWK'].includes(type)) {
    return 'Video Content Arsenal';
  } else if (['CIPHER', 'WHISKEY', 'RADIO', 'ALPHA', 'OSCAR', 'UNIFORM', 'VICTOR', 'YANKEE'].includes(type)) {
    return 'Email & Communication';
  } else if (['FORTRESS', 'STRONGHOLD', 'BUNKER', 'OUTPOST', 'CHECKPOINT', 'BARRICADE', 'WATCHTOWER', 'COMMAND'].includes(type)) {
    return 'Landing Pages & Web Operations';
  } else if (['RADIO_SILENCE', 'TRANSMISSION', 'FREQUENCY', 'SIGNAL', 'BEACON', 'SONAR', 'RADAR'].includes(type)) {
    return 'Podcast & Audio Intelligence';
  } else if (['BLACK_OPS', 'NIGHT_VISION', 'INFILTRATE', 'EXTRACTION', 'SABOTAGE', 'AMBUSH', 'FLANKING', 'SIEGE'].includes(type)) {
    return 'Special Operations Content';
  } else if (['GUNSHIP', 'SNATCH', 'THUNDER', 'LIGHTNING', 'TORNADO', 'HURRICANE', 'EARTHQUAKE', 'AVALANCHE'].includes(type)) {
    return 'Advanced Tactical Classifications';
  } else {
    return 'Other';
  }
});

// Virtual for content description
contentItemSchema.virtual('typeDescription').get(function() {
  return CONTENT_TYPES[this.contentType] || 'Unknown content type';
});

// Virtual for content length
contentItemSchema.virtual('contentLength').get(function() {
  const content = this.editedContent || this.rawContent || '';
  return content.length;
});

// Virtual for word count
contentItemSchema.virtual('wordCount').get(function() {
  const content = this.editedContent || this.rawContent || '';
  return content.split(/\s+/).filter(Boolean).length;
});

// Method to update status
contentItemSchema.methods.updateStatus = function(status, progress = null) {
  this.status = status;
  if (progress !== null) {
    this.progress = progress;
  }
  return this.save();
};

// Method to add error
contentItemSchema.methods.setError = function(errorMessage) {
  this.status = CONTENT_STATUS.FAILED;
  this.errorMessage = errorMessage;
  return this.save();
};

// Method to save version
contentItemSchema.methods.saveVersion = function(description = 'Version update') {
  const content = this.editedContent || this.rawContent;
  
  if (!content) {
    return this;
  }
  
  if (!this.versions) {
    this.versions = [];
  }
  
  this.versions.push({
    content,
    createdAt: new Date(),
    description
  });
  
  return this.save();
};

// Method to add export record
contentItemSchema.methods.addExport = function(format, url) {
  if (!this.exports) {
    this.exports = [];
  }
  
  this.exports.push({
    format,
    url,
    createdAt: new Date()
  });
  
  return this.save();
};

// Static method to find content by type
contentItemSchema.statics.findByType = function(contentType) {
  return this.find({ contentType });
};

// Static method to find content by category
contentItemSchema.statics.findByCategory = function(category) {
  let types = [];
  
  switch (category) {
    case 'Blog Content & Articles':
      types = ['SNIPER', 'RECON', 'PHANTOM', 'BLACKOUT', 'INTEL', 'OVERWATCH', 'CLASSIFIED', 'BRIEFING'];
      break;
    case 'Social Media Operations':
      types = ['VIPER', 'GHOST', 'TANGO', 'ECHO', 'BRAVO', 'DELTA', 'FOXTROT', 'SIERRA'];
      break;
    case 'Video Content Arsenal':
      types = ['APACHE', 'STEALTH', 'PREDATOR', 'BLACKHAWK', 'COBRA', 'FALCON', 'RAPTOR', 'HAWK'];
      break;
    case 'Email & Communication':
      types = ['CIPHER', 'WHISKEY', 'RADIO', 'ALPHA', 'OSCAR', 'UNIFORM', 'VICTOR', 'YANKEE'];
      break;
    case 'Landing Pages & Web Operations':
      types = ['FORTRESS', 'STRONGHOLD', 'BUNKER', 'OUTPOST', 'CHECKPOINT', 'BARRICADE', 'WATCHTOWER', 'COMMAND'];
      break;
    case 'Podcast & Audio Intelligence':
      types = ['RADIO_SILENCE', 'TRANSMISSION', 'FREQUENCY', 'SIGNAL', 'BEACON', 'SONAR', 'RADAR'];
      break;
    case 'Special Operations Content':
      types = ['BLACK_OPS', 'NIGHT_VISION', 'INFILTRATE', 'EXTRACTION', 'SABOTAGE', 'AMBUSH', 'FLANKING', 'SIEGE'];
      break;
    case 'Advanced Tactical Classifications':
      types = ['GUNSHIP', 'SNATCH', 'THUNDER', 'LIGHTNING', 'TORNADO', 'HURRICANE', 'EARTHQUAKE', 'AVALANCHE'];
      break;
    default:
      return this.find({});
  }
  
  return this.find({ contentType: { $in: types } });
};

// Create and export the model
const ContentItem = mongoose.model('ContentItem', contentItemSchema);
module.exports = ContentItem;
