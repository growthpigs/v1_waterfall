const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');
const mongoose = require('mongoose');
const auth = require('../../middlewares/auth.middleware');
const User = require('../../models/user.model');

// Import models (to be created)
const ContentItem = require('../../models/content-item.model');
const CIAReport = require('../../models/cia-report.model');

// Import services (to be implemented)
const contentGenerationService = require('../../services/content-generation.service');
const notionExportService = require('../../services/notion-export.service');

// Content type classifications
const CONTENT_CLASSIFICATIONS = {
  // Blog Content & Articles
  BLOG: {
    SNIPER: 'Long-form articles (precision-targeted, high-impact content)',
    RECON: 'Research articles (intelligence-gathering content)',
    PHANTOM: 'Pillar content (comprehensive cornerstone content)',
    BLACKOUT: 'Authority pieces (thought leadership content)',
    INTEL: 'Industry insights (market analysis reports)',
    OVERWATCH: 'Trend analysis (timely content on emerging trends)',
    CLASSIFIED: 'Exclusive content (premium subscriber content)',
    BRIEFING: 'Summary articles (concise overviews)'
  },
  // Social Media Operations
  SOCIAL: {
    VIPER: 'Instagram posts (visual content with impact)',
    GHOST: 'Facebook content (engagement-focused posts)',
    TANGO: 'LinkedIn posts (professional networking content)',
    ECHO: 'Twitter/X posts (concise, shareable messages)',
    BRAVO: 'TikTok content (short-form video content)',
    DELTA: 'YouTube Shorts (brief video content)',
    FOXTROT: 'Pinterest posts (visual discovery content)',
    SIERRA: 'Snapchat content (ephemeral content)'
  },
  // Video Content Arsenal
  VIDEO: {
    APACHE: 'Brand videos (promotional content)',
    STEALTH: 'UGC videos (user-generated content)',
    PREDATOR: 'Video ads (targeted advertising)',
    BLACKHAWK: 'Testimonial videos (customer success stories)',
    COBRA: 'Product demos (feature demonstrations)',
    FALCON: 'Educational videos (informative content)',
    RAPTOR: 'Tutorial videos (instructional content)',
    HAWK: 'Behind-the-scenes (company culture content)'
  },
  // Email & Communication
  EMAIL: {
    CIPHER: 'Newsletters (regular subscriber communications)',
    WHISKEY: 'Email campaigns (targeted email sequences)',
    RADIO: 'Automated sequences (drip campaigns)',
    ALPHA: 'Welcome series (onboarding communications)',
    OSCAR: 'Promotional emails (sales communications)',
    UNIFORM: 'Template emails (standardized communications)',
    VICTOR: 'Victory emails (achievement announcements)',
    YANKEE: 'Announcement emails (important updates)'
  },
  // Landing Pages & Web Operations
  LANDING: {
    FORTRESS: 'Landing pages (conversion-focused pages)',
    STRONGHOLD: 'Sales pages (revenue-generating pages)',
    BUNKER: 'Lead magnets (prospect-capturing resources)',
    OUTPOST: 'Thank you pages (post-conversion pages)',
    CHECKPOINT: 'Opt-in pages (subscriber acquisition pages)',
    BARRICADE: 'Squeeze pages (focused conversion pages)',
    WATCHTOWER: 'About pages (company information pages)',
    COMMAND: 'Homepage (main website entry point)'
  },
  // Podcast & Audio Intelligence
  AUDIO: {
    RADIO_SILENCE: 'Podcast episodes (audio content series)',
    TRANSMISSION: 'Audio ads (audio promotional content)',
    FREQUENCY: 'Voice content (voice-optimized content)',
    SIGNAL: 'Audio announcements (important audio updates)',
    BEACON: 'Audio guides (instructional audio content)',
    SONAR: 'Interview shows (conversation-based content)',
    RADAR: 'News podcasts (current events coverage)'
  },
  // Special Operations Content
  SPECIAL_OPS: {
    BLACK_OPS: 'Confidential reports (exclusive analysis)',
    NIGHT_VISION: 'Dark social content (private sharing content)',
    INFILTRATE: 'Competitor analysis (competitive intelligence)',
    EXTRACTION: 'Data reports (insights from raw data)',
    SABOTAGE: 'Disruptive content (industry-challenging content)',
    AMBUSH: 'Surprise launches (unexpected content releases)',
    FLANKING: 'Alternative perspective content (unique viewpoints)',
    SIEGE: 'Long-term campaigns (sustained content pressure)'
  },
  // Advanced Tactical Classifications
  ADVANCED: {
    GUNSHIP: 'Multi-format campaigns (cross-platform content)',
    SNATCH: 'Lead capture content (prospect acquisition content)',
    THUNDER: 'Viral content attempts (high-sharing potential content)',
    LIGHTNING: 'Rapid response content (timely reactive content)',
    TORNADO: 'Trending topic content (current events content)',
    HURRICANE: 'Major announcement content (significant updates)',
    EARTHQUAKE: 'Industry-shaking content (disruptive revelations)',
    AVALANCHE: 'Overwhelming content series (massive content deployment)'
  }
};

// Helper function to get all content types as a flat array
function getAllContentTypes() {
  const types = [];
  for (const category in CONTENT_CLASSIFICATIONS) {
    for (const type in CONTENT_CLASSIFICATIONS[category]) {
      types.push(type);
    }
  }
  return types;
}

// Helper function to validate content type
function isValidContentType(type) {
  return getAllContentTypes().includes(type);
}

/**
 * @route   POST api/cartwheel/content
 * @desc    Generate new content
 * @access  Private (requires Premium subscription for full access, Basic for limited)
 */
router.post(
  '/content',
  [
    auth,
    check('ciaReportId', 'CIA Report ID is required').isMongoId(),
    check('contentType', 'Valid content type is required').custom(isValidContentType),
    check('title', 'Title is required').not().isEmpty(),
    check('parameters', 'Parameters must be an object').isObject(),
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { ciaReportId, contentType, title, parameters, promptStyle, keywords } = req.body;

      // Check if user has access to Cartwheel
      const user = await User.findById(req.user.id);
      
      // Determine access level based on subscription
      let fullAccess = false;
      if (user.canAccess('cartwheel')) {
        fullAccess = true;
      } else if (!user.canAccess('cartwheelLimited')) {
        return res.status(403).json({ 
          message: 'Subscription upgrade required for Cartwheel access',
          currentTier: user.subscription.tier
        });
      }

      // Check if CIA report exists and belongs to user
      const ciaReport = await CIAReport.findOne({ 
        _id: ciaReportId, 
        user: req.user.id,
        status: 'completed' // Only completed reports can be used
      });

      if (!ciaReport) {
        return res.status(404).json({ message: 'CIA Report not found or not completed' });
      }

      // Check content type restrictions for limited access
      if (!fullAccess) {
        // Limited users can only access certain content types
        const allowedTypes = [
          'SNIPER', 'RECON', // Blog content
          'ECHO', 'TANGO',   // Social media
          'CIPHER', 'ALPHA'  // Email
        ];
        
        if (!allowedTypes.includes(contentType)) {
          return res.status(403).json({ 
            message: `Content type ${contentType} requires Premium subscription`,
            currentTier: user.subscription.tier
          });
        }
        
        // Check usage limits for limited access
        const monthStart = new Date();
        monthStart.setDate(1);
        monthStart.setHours(0, 0, 0, 0);
        
        const contentCount = await ContentItem.countDocuments({
          user: req.user.id,
          createdAt: { $gte: monthStart }
        });
        
        if (contentCount >= 10) { // Basic tier limit
          return res.status(403).json({ 
            message: 'Monthly content generation limit reached for Basic subscription',
            currentTier: user.subscription.tier,
            limit: 10,
            used: contentCount
          });
        }
      }

      // Create content item
      const contentItem = new ContentItem({
        user: req.user.id,
        ciaReport: ciaReportId,
        contentType,
        title,
        parameters,
        promptStyle,
        keywords: keywords || [],
        status: 'queued'
      });

      await contentItem.save();

      // Update user usage statistics
      await User.findByIdAndUpdate(req.user.id, {
        $inc: { 'usage.cartwheelContent.count': 1, [`usage.cartwheelContent.byType.${contentType}`]: 1 },
        $set: { 'usage.cartwheelContent.lastUsed': new Date() }
      });

      // Generate content asynchronously
      process.nextTick(async () => {
        try {
          await contentGenerationService.generate(contentItem._id);
        } catch (error) {
          console.error('Content generation error:', error);
          await ContentItem.findByIdAndUpdate(contentItem._id, {
            status: 'failed',
            errorMessage: error.message
          });
        }
      });

      res.status(201).json({
        message: 'Content generation initiated',
        content: {
          id: contentItem._id,
          title: contentItem.title,
          contentType,
          status: contentItem.status,
          createdAt: contentItem.createdAt
        }
      });
    } catch (error) {
      console.error('Content creation error:', error);
      res.status(500).json({ message: 'Server error during content creation' });
    }
  }
);

/**
 * @route   GET api/cartwheel/content
 * @desc    Get all content items for current user
 * @access  Private
 */
router.get('/content', auth, async (req, res) => {
  try {
    // Pagination parameters
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    // Filtering parameters
    const filters = { user: req.user.id };
    
    if (req.query.contentType && isValidContentType(req.query.contentType)) {
      filters.contentType = req.query.contentType;
    }
    
    if (req.query.status) {
      filters.status = req.query.status;
    }
    
    if (req.query.ciaReport) {
      filters.ciaReport = req.query.ciaReport;
    }

    // Sorting parameters
    const sort = {};
    if (req.query.sortBy) {
      const parts = req.query.sortBy.split(':');
      sort[parts[0]] = parts[1] === 'desc' ? -1 : 1;
    } else {
      sort.createdAt = -1; // Default sort by creation date, newest first
    }

    // Execute query with pagination
    const contentItems = await ContentItem.find(filters)
      .sort(sort)
      .skip(skip)
      .limit(limit)
      .populate('ciaReport', 'name')
      .select('-rawContent -editedContent'); // Exclude large content fields

    // Get total count for pagination
    const total = await ContentItem.countDocuments(filters);

    res.json({
      content: contentItems,
      pagination: {
        total,
        page,
        limit,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Get content items error:', error);
    res.status(500).json({ message: 'Server error while retrieving content items' });
  }
});

/**
 * @route   GET api/cartwheel/content/:id
 * @desc    Get a specific content item
 * @access  Private
 */
router.get('/content/:id', auth, async (req, res) => {
  try {
    const contentItem = await ContentItem.findById(req.params.id)
      .populate('ciaReport', 'name');

    if (!contentItem) {
      return res.status(404).json({ message: 'Content item not found' });
    }

    // Check if the content belongs to the user
    if (contentItem.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to access this content' });
    }

    res.json(contentItem);
  } catch (error) {
    console.error('Get content item error:', error);
    res.status(500).json({ message: 'Server error while retrieving content item' });
  }
});

/**
 * @route   GET api/cartwheel/content/:id/status
 * @desc    Get the status of a content item
 * @access  Private
 */
router.get('/content/:id/status', auth, async (req, res) => {
  try {
    const contentItem = await ContentItem.findById(req.params.id)
      .select('status progress errorMessage');

    if (!contentItem) {
      return res.status(404).json({ message: 'Content item not found' });
    }

    // Check if the content belongs to the user
    if (contentItem.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to access this content' });
    }

    res.json({
      status: contentItem.status,
      progress: contentItem.progress,
      errorMessage: contentItem.errorMessage
    });
  } catch (error) {
    console.error('Get content status error:', error);
    res.status(500).json({ message: 'Server error while retrieving content status' });
  }
});

/**
 * @route   PUT api/cartwheel/content/:id
 * @desc    Update a content item (edit generated content)
 * @access  Private
 */
router.put(
  '/content/:id',
  [
    auth,
    check('editedContent', 'Edited content is required').optional().isString(),
    check('title', 'Title must not be empty').optional().notEmpty(),
    check('keywords', 'Keywords must be an array').optional().isArray(),
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      let contentItem = await ContentItem.findById(req.params.id);

      if (!contentItem) {
        return res.status(404).json({ message: 'Content item not found' });
      }

      // Check if the content belongs to the user
      if (contentItem.user.toString() !== req.user.id) {
        return res.status(403).json({ message: 'Not authorized to update this content' });
      }

      // Check if the content is in a state that can be updated
      if (contentItem.status === 'queued' || contentItem.status === 'generating') {
        return res.status(400).json({ message: 'Cannot update content while it is being generated' });
      }

      // Update allowed fields
      const allowedUpdates = {
        editedContent: req.body.editedContent,
        title: req.body.title,
        keywords: req.body.keywords,
        isEdited: true,
        lastEditedAt: new Date()
      };

      // Filter out undefined values
      Object.keys(allowedUpdates).forEach(key => 
        allowedUpdates[key] === undefined && delete allowedUpdates[key]
      );

      // Apply updates
      contentItem = await ContentItem.findByIdAndUpdate(
        req.params.id,
        { $set: allowedUpdates },
        { new: true, runValidators: true }
      );

      res.json({
        message: 'Content updated successfully',
        content: contentItem
      });
    } catch (error) {
      console.error('Update content error:', error);
      res.status(500).json({ message: 'Server error while updating content' });
    }
  }
);

/**
 * @route   DELETE api/cartwheel/content/:id
 * @desc    Delete a content item
 * @access  Private
 */
router.delete('/content/:id', auth, async (req, res) => {
  try {
    const contentItem = await ContentItem.findById(req.params.id);

    if (!contentItem) {
      return res.status(404).json({ message: 'Content item not found' });
    }

    // Check if the content belongs to the user
    if (contentItem.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to delete this content' });
    }

    await contentItem.remove();

    res.json({ message: 'Content deleted successfully' });
  } catch (error) {
    console.error('Delete content error:', error);
    res.status(500).json({ message: 'Server error while deleting content' });
  }
});

/**
 * @route   POST api/cartwheel/content/:id/regenerate
 * @desc    Regenerate content
 * @access  Private
 */
router.post('/content/:id/regenerate', auth, async (req, res) => {
  try {
    const contentItem = await ContentItem.findById(req.params.id);

    if (!contentItem) {
      return res.status(404).json({ message: 'Content item not found' });
    }

    // Check if the content belongs to the user
    if (contentItem.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to regenerate this content' });
    }

    // Check if user has access to Cartwheel
    const user = await User.findById(req.user.id);
    if (!user.canAccess('cartwheel') && !user.canAccess('cartwheelLimited')) {
      return res.status(403).json({ 
        message: 'Subscription upgrade required for Cartwheel access',
        currentTier: user.subscription.tier
      });
    }

    // Update content status
    await ContentItem.findByIdAndUpdate(req.params.id, {
      status: 'queued',
      progress: 0,
      errorMessage: null,
      regeneratedAt: new Date(),
      regenerationCount: (contentItem.regenerationCount || 0) + 1
    });

    // Generate content asynchronously
    process.nextTick(async () => {
      try {
        await contentGenerationService.generate(contentItem._id);
      } catch (error) {
        console.error('Content regeneration error:', error);
        await ContentItem.findByIdAndUpdate(contentItem._id, {
          status: 'failed',
          errorMessage: error.message
        });
      }
    });

    res.json({
      message: 'Content regeneration initiated',
      content: {
        id: contentItem._id,
        title: contentItem.title,
        contentType: contentItem.contentType,
        status: 'queued'
      }
    });
  } catch (error) {
    console.error('Content regeneration error:', error);
    res.status(500).json({ message: 'Server error during content regeneration' });
  }
});

/**
 * @route   POST api/cartwheel/content/:id/export
 * @desc    Export content to various formats
 * @access  Private
 */
router.post(
  '/content/:id/export',
  [
    auth,
    check('format', 'Export format is required').isIn(['pdf', 'docx', 'notion', 'google_sheets', 'markdown', 'html']),
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const contentItem = await ContentItem.findById(req.params.id);

      if (!contentItem) {
        return res.status(404).json({ message: 'Content item not found' });
      }

      // Check if the content belongs to the user
      if (contentItem.user.toString() !== req.user.id) {
        return res.status(403).json({ message: 'Not authorized to export this content' });
      }

      // Check if the content is completed
      if (contentItem.status !== 'completed') {
        return res.status(400).json({ message: 'Cannot export incomplete content' });
      }

      // Handle export based on format
      let exportUrl;
      const format = req.body.format;

      switch (format) {
        case 'pdf':
          // Generate PDF export (to be implemented)
          exportUrl = `/exports/cartwheel/${contentItem._id}/content.pdf`;
          break;
        case 'docx':
          // Generate DOCX export (to be implemented)
          exportUrl = `/exports/cartwheel/${contentItem._id}/content.docx`;
          break;
        case 'notion':
          // Check if user has Notion integration
          const user = await User.findById(req.user.id);
          if (!user.integrations.notion.enabled) {
            return res.status(400).json({ message: 'Notion integration not configured' });
          }
          // Export to Notion (to be implemented)
          exportUrl = await notionExportService.exportContent(contentItem._id);
          break;
        case 'google_sheets':
          // Export to Google Sheets (to be implemented)
          exportUrl = `https://docs.google.com/spreadsheets/...`; // Placeholder
          break;
        case 'markdown':
          // Generate Markdown export (to be implemented)
          exportUrl = `/exports/cartwheel/${contentItem._id}/content.md`;
          break;
        case 'html':
          // Generate HTML export (to be implemented)
          exportUrl = `/exports/cartwheel/${contentItem._id}/content.html`;
          break;
        default:
          return res.status(400).json({ message: 'Unsupported export format' });
      }

      // Add export record to content item
      await ContentItem.findByIdAndUpdate(req.params.id, {
        $push: {
          exports: {
            format,
            url: exportUrl,
            createdAt: new Date()
          }
        }
      });

      res.json({
        message: `Content exported to ${format} successfully`,
        exportUrl
      });
    } catch (error) {
      console.error('Export content error:', error);
      res.status(500).json({ message: 'Server error during content export' });
    }
  }
);

/**
 * @route   GET api/cartwheel/classifications
 * @desc    Get all content classifications
 * @access  Private
 */
router.get('/classifications', auth, async (req, res) => {
  try {
    res.json(CONTENT_CLASSIFICATIONS);
  } catch (error) {
    console.error('Get classifications error:', error);
    res.status(500).json({ message: 'Server error while retrieving classifications' });
  }
});

/**
 * @route   POST api/cartwheel/batch
 * @desc    Generate multiple content items in batch
 * @access  Private (Premium subscription only)
 */
router.post(
  '/batch',
  [
    auth,
    auth.checkFeatureAccess('cartwheel'), // Only premium users can batch generate
    check('ciaReportId', 'CIA Report ID is required').isMongoId(),
    check('items', 'Items array is required').isArray(),
    check('items.*.contentType', 'Valid content type is required for each item').custom(isValidContentType),
    check('items.*.title', 'Title is required for each item').not().isEmpty(),
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { ciaReportId, items, commonPromptStyle } = req.body;

      // Check if CIA report exists and belongs to user
      const ciaReport = await CIAReport.findOne({ 
        _id: ciaReportId, 
        user: req.user.id,
        status: 'completed' // Only completed reports can be used
      });

      if (!ciaReport) {
        return res.status(404).json({ message: 'CIA Report not found or not completed' });
      }

      // Check batch size limit
      if (items.length > 10) {
        return res.status(400).json({ message: 'Batch size cannot exceed 10 items' });
      }

      // Create content items
      const contentItems = [];
      for (const item of items) {
        const contentItem = new ContentItem({
          user: req.user.id,
          ciaReport: ciaReportId,
          contentType: item.contentType,
          title: item.title,
          parameters: item.parameters || {},
          promptStyle: item.promptStyle || commonPromptStyle,
          keywords: item.keywords || [],
          status: 'queued'
        });

        await contentItem.save();
        contentItems.push(contentItem);
      }

      // Update user usage statistics
      await User.findByIdAndUpdate(req.user.id, {
        $inc: { 'usage.cartwheelContent.count': items.length },
        $set: { 'usage.cartwheelContent.lastUsed': new Date() }
      });

      // Generate content asynchronously
      process.nextTick(async () => {
        for (const contentItem of contentItems) {
          try {
            await contentGenerationService.generate(contentItem._id);
          } catch (error) {
            console.error(`Content generation error for item ${contentItem._id}:`, error);
            await ContentItem.findByIdAndUpdate(contentItem._id, {
              status: 'failed',
              errorMessage: error.message
            });
          }
        }
      });

      res.status(201).json({
        message: `Batch content generation initiated for ${items.length} items`,
        content: contentItems.map(item => ({
          id: item._id,
          title: item.title,
          contentType: item.contentType,
          status: item.status
        }))
      });
    } catch (error) {
      console.error('Batch content creation error:', error);
      res.status(500).json({ message: 'Server error during batch content creation' });
    }
  }
);

/**
 * @route   POST api/cartwheel/calendar
 * @desc    Generate a content calendar
 * @access  Private (Premium subscription only)
 */
router.post(
  '/calendar',
  [
    auth,
    auth.checkFeatureAccess('cartwheel'), // Only premium users can use calendar
    check('ciaReportId', 'CIA Report ID is required').isMongoId(),
    check('startDate', 'Start date is required').isISO8601(),
    check('endDate', 'End date is required').isISO8601(),
    check('frequency', 'Frequency must be a number').isInt({ min: 1 }),
    check('contentTypes', 'Content types must be an array').isArray(),
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { 
        ciaReportId, 
        startDate, 
        endDate, 
        frequency, 
        contentTypes, 
        promptStyle,
        generateContent
      } = req.body;

      // Check if CIA report exists and belongs to user
      const ciaReport = await CIAReport.findOne({ 
        _id: ciaReportId, 
        user: req.user.id,
        status: 'completed' // Only completed reports can be used
      });

      if (!ciaReport) {
        return res.status(404).json({ message: 'CIA Report not found or not completed' });
      }

      // Validate content types
      for (const type of contentTypes) {
        if (!isValidContentType(type)) {
          return res.status(400).json({ message: `Invalid content type: ${type}` });
        }
      }

      // Calculate date range
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      if (start >= end) {
        return res.status(400).json({ message: 'End date must be after start date' });
      }
      
      // Calculate number of days in range
      const daysDiff = Math.floor((end - start) / (1000 * 60 * 60 * 24));
      
      // Calculate number of content items
      const numItems = Math.ceil(daysDiff / frequency) * contentTypes.length;
      
      // Check if number of items is reasonable
      if (numItems > 100) {
        return res.status(400).json({ 
          message: 'Calendar would generate too many items. Please reduce date range, increase frequency, or reduce content types.',
          numItems
        });
      }

      // Generate calendar (to be implemented)
      // This would create a content calendar with scheduled content items
      
      // Placeholder response
      res.json({
        message: 'Content calendar generated',
        calendar: {
          startDate,
          endDate,
          frequency,
          contentTypes,
          totalItems: numItems,
          // Additional calendar details would be returned here
        }
      });
    } catch (error) {
      console.error('Calendar generation error:', error);
      res.status(500).json({ message: 'Server error during calendar generation' });
    }
  }
);

module.exports = router;
