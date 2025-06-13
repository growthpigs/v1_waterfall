const mongoose = require('mongoose');
const Schema = mongoose.Schema;

// Status enum for CIA report generation process
const REPORT_STATUS = {
  INITIATED: 'initiated',
  DATA_COLLECTION: 'data_collection',
  WEBSITE_ANALYSIS: 'website_analysis',
  COMPETITOR_ANALYSIS: 'competitor_analysis',
  SEO_ANALYSIS: 'seo_analysis',
  MARKET_RESEARCH: 'market_research',
  SOCIAL_PROOF_ANALYSIS: 'social_proof_analysis',
  GENERATING_CONTENT_BIBLE: 'generating_content_bible',
  COMPLETED: 'completed',
  FAILED: 'failed'
};

// Schema for the CIA Report
const ciaReportSchema = new Schema({
  // Report metadata
  user: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  status: {
    type: String,
    enum: Object.values(REPORT_STATUS),
    default: REPORT_STATUS.INITIATED
  },
  progress: {
    type: Number,
    min: 0,
    max: 100,
    default: 0
  },
  errorMessage: String,
  
  // Initial data collection
  initialData: {
    companyName: {
      type: String,
      required: true,
      trim: true
    },
    websiteUrl: {
      type: String,
      required: true,
      trim: true
    },
    keyPersonOfInfluence: {
      name: String,
      role: String,
      socialProfiles: {
        linkedin: String,
        twitter: String,
        instagram: String,
        facebook: String,
        other: [String]
      }
    },
    industry: String,
    targetAudience: [String],
    businessGoals: [String],
    contentGoals: [String],
    brandVoice: {
      tone: String,
      style: String,
      examples: [String]
    }
  },
  
  // Website analysis
  websiteAnalysis: {
    completed: {
      type: Boolean,
      default: false
    },
    pages: [{
      url: String,
      title: String,
      metaDescription: String,
      h1: String,
      wordCount: Number,
      contentQuality: {
        type: String,
        enum: ['poor', 'fair', 'good', 'excellent']
      },
      keywordDensity: Map,
      internalLinks: Number,
      externalLinks: Number,
      images: Number,
      hasSchema: Boolean
    }],
    contentTypes: [{
      type: String,
      count: Number,
      examples: [String]
    }],
    messaging: {
      primaryMessage: String,
      secondaryMessages: [String],
      callsToAction: [String],
      valuePropositions: [String]
    },
    branding: {
      logoUrl: String,
      colorPalette: [String],
      typography: [String],
      imageStyle: String,
      brandConsistency: {
        type: String,
        enum: ['poor', 'fair', 'good', 'excellent']
      }
    },
    technical: {
      pagespeed: {
        mobile: Number,
        desktop: Number
      },
      mobileResponsive: Boolean,
      secureConnection: Boolean,
      crawlability: {
        type: String,
        enum: ['poor', 'fair', 'good', 'excellent']
      },
      sitemapPresent: Boolean,
      robotsTxtPresent: Boolean,
      issues: [{
        type: String,
        severity: {
          type: String,
          enum: ['low', 'medium', 'high', 'critical']
        },
        description: String
      }]
    }
  },
  
  // Competitor analysis
  competitorAnalysis: {
    completed: {
      type: Boolean,
      default: false
    },
    competitors: [{
      name: String,
      websiteUrl: String,
      strengths: [String],
      weaknesses: [String],
      contentStrategy: String,
      socialPresence: {
        platforms: [String],
        followerCounts: Map,
        engagementRate: Number
      },
      keywordRankings: [{
        keyword: String,
        position: Number
      }],
      contentTypes: [String],
      uniqueSellingPoints: [String]
    }]
  },
  
  // SEO intelligence
  seoIntelligence: {
    completed: {
      type: Boolean,
      default: false
    },
    domainAuthority: Number,
    organicTraffic: Number,
    organicKeywords: Number,
    keywordResearch: {
      primaryKeywords: [{
        keyword: String,
        searchVolume: Number,
        difficulty: Number,
        cpc: Number,
        currentRanking: Number
      }],
      secondaryKeywords: [{
        keyword: String,
        searchVolume: Number,
        difficulty: Number,
        cpc: Number,
        currentRanking: Number
      }],
      longTailKeywords: [{
        keyword: String,
        searchVolume: Number,
        difficulty: Number,
        cpc: Number,
        currentRanking: Number
      }]
    },
    gapAnalysis: {
      missingKeywords: [{
        keyword: String,
        searchVolume: Number,
        difficulty: Number,
        competitor: String,
        competitorRanking: Number
      }],
      contentGaps: [{
        topic: String,
        relatedKeywords: [String],
        competitorCoverage: [String]
      }]
    },
    opportunities: [{
      keyword: String,
      searchVolume: Number,
      difficulty: Number,
      potentialTraffic: Number,
      suggestedContentType: String,
      priority: {
        type: String,
        enum: ['low', 'medium', 'high']
      }
    }]
  },
  
  // Market research
  marketResearch: {
    completed: {
      type: Boolean,
      default: false
    },
    industryTrends: [{
      trend: String,
      growthRate: Number,
      relevance: {
        type: String,
        enum: ['low', 'medium', 'high']
      },
      sources: [String]
    }],
    audienceInsights: {
      demographics: {
        ageRanges: [String],
        genders: [String],
        locations: [String],
        incomeRanges: [String],
        educationLevels: [String]
      },
      psychographics: {
        interests: [String],
        values: [String],
        painPoints: [String],
        goals: [String]
      },
      behaviors: {
        purchasePatterns: [String],
        contentConsumptionHabits: [String],
        deviceUsage: Map,
        socialPlatformPreferences: [String]
      }
    },
    marketPositioning: {
      currentPosition: String,
      recommendedPosition: String,
      differentiators: [String],
      marketGaps: [String]
    }
  },
  
  // Social proof analysis
  socialProofAnalysis: {
    completed: {
      type: Boolean,
      default: false
    },
    testimonials: [{
      source: String,
      text: String,
      author: String,
      rating: Number,
      date: Date,
      sentiment: {
        type: String,
        enum: ['negative', 'neutral', 'positive']
      },
      keywords: [String]
    }],
    reviews: {
      platforms: [{
        name: String,
        averageRating: Number,
        totalReviews: Number,
        positivePercentage: Number,
        negativePercentage: Number
      }],
      commonThemes: {
        positive: [{
          theme: String,
          frequency: Number,
          examples: [String]
        }],
        negative: [{
          theme: String,
          frequency: Number,
          examples: [String]
        }]
      }
    },
    socialMentions: {
      volume: Number,
      sentiment: {
        positive: Number,
        neutral: Number,
        negative: Number
      },
      influencers: [{
        name: String,
        platform: String,
        reach: Number,
        engagement: Number,
        sentiment: {
          type: String,
          enum: ['negative', 'neutral', 'positive']
        }
      }],
      topPosts: [{
        platform: String,
        url: String,
        engagement: Number,
        sentiment: {
          type: String,
          enum: ['negative', 'neutral', 'positive']
        }
      }]
    }
  },
  
  // Master Content Bible
  masterContentBible: {
    completed: {
      type: Boolean,
      default: false
    },
    brandNarrative: {
      story: String,
      mission: String,
      vision: String,
      values: [String],
      uniqueSellingProposition: String,
      targetAudiencePersonas: [{
        name: String,
        description: String,
        demographics: Map,
        goals: [String],
        challenges: [String],
        contentPreferences: [String]
      }]
    },
    contentStrategy: {
      goals: [String],
      kpis: [String],
      channels: [{
        name: String,
        purpose: String,
        audience: String,
        contentTypes: [String],
        frequency: String,
        metrics: [String]
      }],
      contentCalendar: {
        themes: [String],
        seasonalOpportunities: [{
          name: String,
          timing: String,
          contentIdeas: [String]
        }]
      }
    },
    keywordStrategy: {
      primaryKeywords: [String],
      secondaryKeywords: [String],
      semanticKeywordClusters: [{
        mainKeyword: String,
        relatedKeywords: [String]
      }]
    },
    contentRecommendations: {
      blogs: [{
        title: String,
        targetKeywords: [String],
        outline: [String],
        estimatedWordCount: Number,
        contentType: {
          type: String,
          enum: ['SNIPER', 'RECON', 'PHANTOM', 'BLACKOUT', 'INTEL', 'OVERWATCH', 'CLASSIFIED', 'BRIEFING']
        }
      }],
      socialMedia: [{
        platform: String,
        contentIdeas: [String],
        hashtags: [String],
        contentType: {
          type: String,
          enum: ['VIPER', 'GHOST', 'TANGO', 'ECHO', 'BRAVO', 'DELTA', 'FOXTROT', 'SIERRA']
        }
      }],
      video: [{
        title: String,
        description: String,
        keyPoints: [String],
        estimatedDuration: String,
        contentType: {
          type: String,
          enum: ['APACHE', 'STEALTH', 'PREDATOR', 'BLACKHAWK', 'COBRA', 'FALCON', 'RAPTOR', 'HAWK']
        }
      }],
      email: [{
        subject: String,
        purpose: String,
        keyPoints: [String],
        callToAction: String,
        contentType: {
          type: String,
          enum: ['CIPHER', 'WHISKEY', 'RADIO', 'ALPHA', 'OSCAR', 'UNIFORM', 'VICTOR', 'YANKEE']
        }
      }],
      landingPages: [{
        title: String,
        purpose: String,
        keyElements: [String],
        callToAction: String,
        contentType: {
          type: String,
          enum: ['FORTRESS', 'STRONGHOLD', 'BUNKER', 'OUTPOST', 'CHECKPOINT', 'BARRICADE', 'WATCHTOWER', 'COMMAND']
        }
      }],
      podcast: [{
        title: String,
        description: String,
        potentialGuests: [String],
        keyTopics: [String],
        contentType: {
          type: String,
          enum: ['RADIO SILENCE', 'TRANSMISSION', 'FREQUENCY', 'SIGNAL', 'BEACON', 'SONAR', 'RADAR']
        }
      }]
    },
    contentFormulas: {
      headlines: [String],
      emailSubjects: [String],
      callsToAction: [String],
      valuePropositions: [String]
    },
    brandGuidelines: {
      voice: {
        tone: String,
        vocabulary: [String],
        examples: [String]
      },
      messaging: {
        primaryMessage: String,
        supportingMessages: [String],
        doSay: [String],
        dontSay: [String]
      },
      visualGuidelines: {
        colorHexCodes: [String],
        fonts: [String],
        imageStyle: String,
        logoUsage: [String]
      }
    },
    competitiveInsights: {
      strengthsToEmphasize: [String],
      weaknessesToAddress: [String],
      opportunitiesToTarget: [String],
      threatsToMonitor: [String]
    }
  },
  
  // Export history
  exports: [{
    format: {
      type: String,
      enum: ['pdf', 'docx', 'notion', 'google_sheets']
    },
    url: String,
    createdAt: {
      type: Date,
      default: Date.now
    }
  }],
  
  // Processing metadata
  processingMetadata: {
    startTime: Date,
    endTime: Date,
    totalDuration: Number, // in seconds
    apiCalls: {
      // Only DataForSEO is tracked; it now covers trends & SEO
      dataForSEO: Number
    },
    errors: [{
      stage: String,
      message: String,
      timestamp: Date
    }]
  }
}, {
  timestamps: true
});

// Virtual for report age
ciaReportSchema.virtual('age').get(function() {
  return Math.floor((Date.now() - this.createdAt) / (1000 * 60 * 60 * 24)); // in days
});

// Method to update report status
ciaReportSchema.methods.updateStatus = function(status, progress = null) {
  this.status = status;
  if (progress !== null) {
    this.progress = progress;
  }
  
  // Update timestamps based on status
  if (status === REPORT_STATUS.INITIATED) {
    this.processingMetadata.startTime = new Date();
  } else if (status === REPORT_STATUS.COMPLETED || status === REPORT_STATUS.FAILED) {
    this.processingMetadata.endTime = new Date();
    this.processingMetadata.totalDuration = 
      (this.processingMetadata.endTime - this.processingMetadata.startTime) / 1000;
  }
  
  return this.save();
};

// Method to add error
ciaReportSchema.methods.addError = function(stage, message) {
  if (!this.processingMetadata.errors) {
    this.processingMetadata.errors = [];
  }
  
  this.processingMetadata.errors.push({
    stage,
    message,
    timestamp: new Date()
  });
  
  return this.save();
};

// Method to add export record
ciaReportSchema.methods.addExport = function(format, url) {
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

// Static method to find reports by status
ciaReportSchema.statics.findByStatus = function(status) {
  return this.find({ status });
};

// Create and export the model
const CIAReport = mongoose.model('CIAReport', ciaReportSchema);
module.exports = CIAReport;
