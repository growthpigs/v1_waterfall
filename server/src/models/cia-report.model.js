const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const errorSchema = new Schema({
  stage: { type: String, required: true },
  message: { type: String, required: true },
  timestamp: { type: Date, default: Date.now }
}, { _id: false });

const processingMetadataSchema = new Schema({
  startTime: { type: Date },
  endTime: { type: Date },
  totalDuration: { type: Number }, // in seconds
  apiCalls: {
    openRouter: { type: Number, default: 0 },
    dataForSEO: { type: Number, default: 0 }
  }
}, { _id: false });

const phaseOutputBaseSchema = {
  completed: { type: Boolean, default: false },
  timestamp: { type: Date },
  aiMetadata: {
    model: String,
    tokensUsed: Number,
    processingTime: Number // in ms for this specific AI call
  },
  // Common analysis structure
  analysis: { type: Schema.Types.Mixed } 
};

const websiteAnalysisSchema = new Schema({
  ...phaseOutputBaseSchema,
  websiteAnalysis: {
    url: String,
    completed: Boolean,
    timestamp: Date
  },
  competitorAnalysis: {
    completed: Boolean,
    timestamp: Date
  }
}, { _id: false });

const seoIntelligenceSchema = new Schema({
  ...phaseOutputBaseSchema,
  seoAnalysis: {
    completed: Boolean,
    keywords: Schema.Types.Mixed,
    timestamp: Date
  },
  socialAnalysis: {
    completed: Boolean,
    platforms: Schema.Types.Mixed,
    timestamp: Date
  },
  dataForSEOResults: Schema.Types.Mixed
}, { _id: false });

const marketResearchSchema = new Schema({
  ...phaseOutputBaseSchema,
  marketResearch: {
    completed: Boolean,
    insights: Schema.Types.Mixed,
    timestamp: Date
  }
}, { _id: false });

const socialProofAnalysisSchema = new Schema({ // Corresponds to Golden Hippo Offer
  ...phaseOutputBaseSchema,
  offerStrategy: {
    completed: Boolean,
    offers: [Schema.Types.Mixed],
    pricingStrategy: Schema.Types.Mixed,
    valueProposition: Schema.Types.Mixed,
    timestamp: Date
  },
  ninetyDayPlan: {
    completed: Boolean,
    milestones: [Schema.Types.Mixed],
    timestamp: Date
  }
}, { _id: false });

const competitorAnalysisSchema = new Schema({ // Corresponds to Convergence Blender
  ...phaseOutputBaseSchema,
  contentSilos: {
    completed: Boolean,
    silos: [Schema.Types.Mixed],
    weeklyPlan: Schema.Types.Mixed,
    timestamp: Date
  },
  contentTypes: {
    completed: Boolean,
    recommendations: Schema.Types.Mixed,
    timestamp: Date
  }
}, { _id: false });

const masterContentBibleSchema = new Schema({
  ...phaseOutputBaseSchema,
  brandNarrative: Schema.Types.Mixed,
  contentStrategy: Schema.Types.Mixed,
  keywordStrategy: Schema.Types.Mixed,
  contentRecommendations: Schema.Types.Mixed,
  contentFormulas: Schema.Types.Mixed,
  brandGuidelines: Schema.Types.Mixed,
  competitiveInsights: Schema.Types.Mixed,
  timestamp: Date
}, { _id: false });


const ciaReportSchema = new Schema({
  user: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  name: { type: String, required: true },
  description: { type: String },
  initialData: {
    companyName: { type: String, required: true },
    websiteUrl: { type: String, required: true },
    industry: { type: String },
    targetAudience: { type: String },
    businessGoals: { type: String },
    contentGoals: { type: String },
    brandVoice: { type: String },
    keyPersonOfInfluence: {
      name: String,
      role: String,
      socialLinks: [String]
    },
    primaryKeyword: { type: String }
  },
  status: { 
    type: String, 
    enum: [
      'initiated', 
      'website_analysis', // Phase 1: Business Intelligence
      'seo_analysis',       // Phase 2: SEO & Social Intelligence
      'market_research',    // Phase 3: Strategic Synthesis
      'social_proof_analysis', // Phase 4: Golden Hippo Offer
      'generating_content_bible', // Phase 5: Convergence Blender
      'completed',          // Phase 6: Master Content Bible (final)
      'failed'
    ], 
    default: 'initiated' 
  },
  progress: { type: Number, default: 0, min: 0, max: 100 }, // Overall progress
  currentPhase: { type: Number, default: 0 }, // 1-6, 0 if idle/not started
  phaseProgress: { type: Number, default: 0, min: 0, max: 100 }, // Progress of the currentPhase

  // Phase-specific outputs
  websiteAnalysis: websiteAnalysisSchema,         // Phase 1 output
  seoIntelligence: seoIntelligenceSchema,       // Phase 2 output
  marketResearch: marketResearchSchema,         // Phase 3 output
  socialProofAnalysis: socialProofAnalysisSchema, // Phase 4 output (Golden Hippo)
  competitorAnalysis: competitorAnalysisSchema,  // Phase 5 output (Convergence Blender)
  masterContentBible: masterContentBibleSchema,   // Phase 6 output

  errors: [errorSchema],
  processingMetadata: processingMetadataSchema,
  
  // Export related fields
  exports: {
    pdf: {
      url: String,
      generatedAt: Date,
      status: { type: String, enum: ['pending', 'completed', 'failed'], default: 'pending' }
    },
    google_sheets: {
      url: String,
      generatedAt: Date,
      status: { type: String, enum: ['pending', 'completed', 'failed'], default: 'pending' }
    },
    notion: {
      pageId: String,
      generatedAt: Date,
      status: { type: String, enum: ['pending', 'completed', 'failed'], default: 'pending' }
    }
  },

  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Middleware to update 'updatedAt' field
ciaReportSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  if (this.isNew && !this.processingMetadata.startTime) {
    this.processingMetadata.startTime = new Date();
  }
  next();
});

ciaReportSchema.pre('findOneAndUpdate', function(next) {
  this.set({ updatedAt: new Date() });
  next();
});


// Method to update report status and progress
ciaReportSchema.methods.updateStatus = async function(status, progress, currentPhase, phaseProgress, error = null) {
  console.log(`[CIAReport MODEL DEBUG] updateStatus called with: status=${status}, progress=${progress}, currentPhase=${currentPhase}, phaseProgress=${phaseProgress}, error=${JSON.stringify(error)}`);
  this.status = status;
  if (progress !== undefined) this.progress = progress;
  if (currentPhase !== undefined) this.currentPhase = currentPhase;
  if (phaseProgress !== undefined) this.phaseProgress = phaseProgress;

  if (error) {
    this.errors.push(error); // error should be an object { stage, message }
  }
  
  // Log the status update for easier debugging from the server logs
  // This is separate from the client-facing status polling
  console.log(`[CIA STATUS] id=${this._id} status=${this.status} progress=${this.progress} currentPhase=${this.currentPhase} phaseProgress=${this.phaseProgress}`);
  
  // If you want to send this detailed status payload via websockets or SSE in the future,
  // this would be a good place to emit an event.
  // For now, the client polls the /status endpoint which reads these fields.

  return this.save();
};

// Method to add an error to the report
ciaReportSchema.methods.addError = async function(stage, message) {
  this.errors.push({ stage, message, timestamp: new Date() });
  return this.save();
};

// Method to update export status
ciaReportSchema.methods.updateExportStatus = async function(format, status, urlOrPageId = null) {
  const exportField = `exports.${format}`;
  this[exportField].status = status;
  this[exportField].generatedAt = new Date();
  if (status === 'completed' && urlOrPageId) {
    if (format === 'notion') {
      this[exportField].pageId = urlOrPageId;
    } else {
      this[exportField].url = urlOrPageId;
    }
  }
  return this.save();
};


const CIAReport = mongoose.model('CIAReport', ciaReportSchema);

module.exports = CIAReport;
