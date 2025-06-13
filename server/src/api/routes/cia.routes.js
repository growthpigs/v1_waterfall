const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');
const CIAReport = require('../../models/cia-report.model');
const User = require('../../models/user.model');
const auth = require('../../middlewares/auth.middleware');

// Import services (to be implemented)
const websiteAnalysisService = require('../../services/website-analysis.service');
const competitorAnalysisService = require('../../services/competitor-analysis.service');
const seoAnalysisService = require('../../services/seo-analysis.service');
const marketResearchService = require('../../services/market-research.service');
const socialProofAnalysisService = require('../../services/social-proof-analysis.service');
const contentBibleGeneratorService = require('../../services/content-bible-generator.service');

/**
 * @route   POST api/cia/reports
 * @desc    Create a new CIA report (start the wizard)
 * @access  Private (requires Basic subscription or higher)
 */
router.post(
  '/reports',
  [
    auth,
    auth.checkFeatureAccess('cia'),
    check('name', 'Report name is required').not().isEmpty(),
    check('initialData.companyName', 'Company name is required').not().isEmpty(),
    check('initialData.websiteUrl', 'Website URL is required').isURL(),
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      // Create new report
      const newReport = new CIAReport({
        user: req.user.id,
        name: req.body.name,
        description: req.body.description,
        initialData: {
          companyName: req.body.initialData.companyName,
          websiteUrl: req.body.initialData.websiteUrl,
          keyPersonOfInfluence: req.body.initialData.keyPersonOfInfluence || {},
          industry: req.body.initialData.industry,
          targetAudience: req.body.initialData.targetAudience || [],
          businessGoals: req.body.initialData.businessGoals || [],
          contentGoals: req.body.initialData.contentGoals || [],
          brandVoice: req.body.initialData.brandVoice || {}
        },
        status: 'initiated',
        progress: 0,
        processingMetadata: {
          startTime: new Date(),
          apiCalls: {
            dataForSEO: 0,
            googleTrends: 0,
            socialMedia: 0
          }
        }
      });

      // Save report
      const savedReport = await newReport.save();

      // Update user usage statistics
      await User.findByIdAndUpdate(req.user.id, {
        $inc: { 'usage.ciaReports.count': 1 },
        $set: { 'usage.ciaReports.lastUsed': new Date() }
      });

      // Start the analysis process asynchronously
      // This would typically be handled by a queue system in production
      process.nextTick(() => {
        startCIAAnalysisProcess(savedReport._id);
      });

      res.status(201).json({
        message: 'CIA report creation initiated',
        report: {
          id: savedReport._id,
          name: savedReport.name,
          status: savedReport.status,
          progress: savedReport.progress,
          createdAt: savedReport.createdAt
        }
      });
    } catch (error) {
      console.error('CIA report creation error:', error);
      res.status(500).json({ message: 'Server error during report creation' });
    }
  }
);

/**
 * @route   GET api/cia/reports
 * @desc    Get all CIA reports for the current user
 * @access  Private
 */
router.get('/reports', auth, async (req, res) => {
  try {
    const reports = await CIAReport.find({ user: req.user.id })
      .select('name description status progress createdAt updatedAt')
      .sort({ createdAt: -1 });

    res.json(reports);
  } catch (error) {
    console.error('Get CIA reports error:', error);
    res.status(500).json({ message: 'Server error while retrieving reports' });
  }
});

/**
 * @route   GET api/cia/reports/:id
 * @desc    Get a specific CIA report
 * @access  Private
 */
router.get('/reports/:id', auth, async (req, res) => {
  try {
    const report = await CIAReport.findById(req.params.id);

    if (!report) {
      return res.status(404).json({ message: 'Report not found' });
    }

    // Check if the report belongs to the user
    if (report.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to access this report' });
    }

    res.json(report);
  } catch (error) {
    console.error('Get CIA report error:', error);
    res.status(500).json({ message: 'Server error while retrieving report' });
  }
});

/**
 * @route   GET api/cia/reports/:id/status
 * @desc    Get the status of a CIA report
 * @access  Private
 */
router.get('/reports/:id/status', auth, async (req, res) => {
  try {
    const report = await CIAReport.findById(req.params.id)
      .select('status progress processingMetadata.errors');

    if (!report) {
      return res.status(404).json({ message: 'Report not found' });
    }

    // Check if the report belongs to the user
    if (report.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to access this report' });
    }

    res.json({
      status: report.status,
      progress: report.progress,
      errors: report.processingMetadata.errors || []
    });
  } catch (error) {
    console.error('Get CIA report status error:', error);
    res.status(500).json({ message: 'Server error while retrieving report status' });
  }
});

/**
 * @route   PUT api/cia/reports/:id
 * @desc    Update a CIA report (manual updates during wizard)
 * @access  Private
 */
router.put('/reports/:id', auth, async (req, res) => {
  try {
    let report = await CIAReport.findById(req.params.id);

    if (!report) {
      return res.status(404).json({ message: 'Report not found' });
    }

    // Check if the report belongs to the user
    if (report.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to update this report' });
    }

    // Check if the report is in a state that can be updated
    if (['completed', 'failed'].includes(report.status)) {
      return res.status(400).json({ message: 'Cannot update a completed or failed report' });
    }

    // Update allowed fields
    const allowedUpdates = [
      'name',
      'description',
      'initialData'
    ];

    // Filter out only the allowed updates
    const updates = {};
    for (const key of Object.keys(req.body)) {
      if (allowedUpdates.includes(key)) {
        updates[key] = req.body[key];
      }
    }

    // Apply updates
    report = await CIAReport.findByIdAndUpdate(
      req.params.id,
      { $set: updates },
      { new: true, runValidators: true }
    );

    res.json({
      message: 'Report updated successfully',
      report
    });
  } catch (error) {
    console.error('Update CIA report error:', error);
    res.status(500).json({ message: 'Server error while updating report' });
  }
});

/**
 * @route   DELETE api/cia/reports/:id
 * @desc    Delete a CIA report
 * @access  Private
 */
router.delete('/reports/:id', auth, async (req, res) => {
  try {
    const report = await CIAReport.findById(req.params.id);

    if (!report) {
      return res.status(404).json({ message: 'Report not found' });
    }

    // Check if the report belongs to the user
    if (report.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to delete this report' });
    }

    await report.remove();

    res.json({ message: 'Report deleted successfully' });
  } catch (error) {
    console.error('Delete CIA report error:', error);
    res.status(500).json({ message: 'Server error while deleting report' });
  }
});

/**
 * @route   POST api/cia/reports/:id/export
 * @desc    Export a CIA report in the specified format
 * @access  Private
 */
router.post(
  '/reports/:id/export',
  [
    auth,
    check('format', 'Export format is required').isIn(['pdf', 'docx', 'notion', 'google_sheets']),
  ],
  async (req, res) => {
    // Validate request
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const report = await CIAReport.findById(req.params.id);

      if (!report) {
        return res.status(404).json({ message: 'Report not found' });
      }

      // Check if the report belongs to the user
      if (report.user.toString() !== req.user.id) {
        return res.status(403).json({ message: 'Not authorized to export this report' });
      }

      // Check if the report is completed
      if (report.status !== 'completed') {
        return res.status(400).json({ message: 'Cannot export an incomplete report' });
      }

      // Handle export based on format
      let exportUrl;
      const format = req.body.format;

      switch (format) {
        case 'pdf':
          // Generate PDF export (to be implemented)
          exportUrl = `/exports/cia/${report._id}/report.pdf`;
          break;
        case 'docx':
          // Generate DOCX export (to be implemented)
          exportUrl = `/exports/cia/${report._id}/report.docx`;
          break;
        case 'notion':
          // Check if user has Notion integration
          const user = await User.findById(req.user.id);
          if (!user.integrations.notion.enabled) {
            return res.status(400).json({ message: 'Notion integration not configured' });
          }
          // Export to Notion (to be implemented)
          exportUrl = `https://notion.so/...`; // Placeholder
          break;
        case 'google_sheets':
          // Export to Google Sheets (to be implemented)
          exportUrl = `https://docs.google.com/spreadsheets/...`; // Placeholder
          break;
        default:
          return res.status(400).json({ message: 'Unsupported export format' });
      }

      // Add export record to report
      await report.addExport(format, exportUrl);

      res.json({
        message: `Report exported to ${format} successfully`,
        exportUrl
      });
    } catch (error) {
      console.error('Export CIA report error:', error);
      res.status(500).json({ message: 'Server error during report export' });
    }
  }
);

/**
 * @route   POST api/cia/reports/:id/analyze/website
 * @desc    Manually trigger website analysis for a report
 * @access  Private
 */
router.post('/reports/:id/analyze/website', auth, async (req, res) => {
  try {
    const report = await CIAReport.findById(req.params.id);

    if (!report) {
      return res.status(404).json({ message: 'Report not found' });
    }

    // Check if the report belongs to the user
    if (report.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to analyze this report' });
    }

    // Update report status
    await report.updateStatus('website_analysis', 20);

    // Trigger website analysis asynchronously
    process.nextTick(async () => {
      try {
        await websiteAnalysisService.analyze(report._id);
      } catch (error) {
        console.error('Website analysis error:', error);
        await report.addError('website_analysis', error.message);
        await report.updateStatus('failed');
      }
    });

    res.json({
      message: 'Website analysis initiated',
      status: report.status,
      progress: report.progress
    });
  } catch (error) {
    console.error('Website analysis initiation error:', error);
    res.status(500).json({ message: 'Server error during analysis initiation' });
  }
});

/**
 * @route   POST api/cia/reports/:id/analyze/competitors
 * @desc    Manually trigger competitor analysis for a report
 * @access  Private
 */
router.post('/reports/:id/analyze/competitors', auth, async (req, res) => {
  try {
    const report = await CIAReport.findById(req.params.id);

    if (!report) {
      return res.status(404).json({ message: 'Report not found' });
    }

    // Check if the report belongs to the user
    if (report.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to analyze this report' });
    }

    // Check if website analysis is completed
    if (!report.websiteAnalysis.completed) {
      return res.status(400).json({ message: 'Website analysis must be completed first' });
    }

    // Update report status
    await report.updateStatus('competitor_analysis', 40);

    // Trigger competitor analysis asynchronously
    process.nextTick(async () => {
      try {
        await competitorAnalysisService.analyze(report._id);
      } catch (error) {
        console.error('Competitor analysis error:', error);
        await report.addError('competitor_analysis', error.message);
        await report.updateStatus('failed');
      }
    });

    res.json({
      message: 'Competitor analysis initiated',
      status: report.status,
      progress: report.progress
    });
  } catch (error) {
    console.error('Competitor analysis initiation error:', error);
    res.status(500).json({ message: 'Server error during analysis initiation' });
  }
});

/**
 * @route   POST api/cia/reports/:id/generate-bible
 * @desc    Manually trigger Master Content Bible generation
 * @access  Private
 */
router.post('/reports/:id/generate-bible', auth, async (req, res) => {
  try {
    const report = await CIAReport.findById(req.params.id);

    if (!report) {
      return res.status(404).json({ message: 'Report not found' });
    }

    // Check if the report belongs to the user
    if (report.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized to generate content bible for this report' });
    }

    // Check if all analyses are completed
    if (!report.websiteAnalysis.completed || 
        !report.competitorAnalysis.completed || 
        !report.seoIntelligence.completed || 
        !report.marketResearch.completed || 
        !report.socialProofAnalysis.completed) {
      return res.status(400).json({ message: 'All analyses must be completed first' });
    }

    // Update report status
    await report.updateStatus('generating_content_bible', 90);

    // Trigger content bible generation asynchronously
    process.nextTick(async () => {
      try {
        await contentBibleGeneratorService.generate(report._id);
        await report.updateStatus('completed', 100);
      } catch (error) {
        console.error('Content bible generation error:', error);
        await report.addError('generating_content_bible', error.message);
        await report.updateStatus('failed');
      }
    });

    res.json({
      message: 'Master Content Bible generation initiated',
      status: report.status,
      progress: report.progress
    });
  } catch (error) {
    console.error('Content bible generation initiation error:', error);
    res.status(500).json({ message: 'Server error during generation initiation' });
  }
});

/**
 * Helper function to start the CIA analysis process
 * In a production environment, this would be handled by a queue system
 */
async function startCIAAnalysisProcess(reportId) {
  try {
    const report = await CIAReport.findById(reportId);
    if (!report) {
      console.error(`Report ${reportId} not found`);
      return;
    }

    // Website Analysis
    await report.updateStatus('website_analysis', 20);
    try {
      await websiteAnalysisService.analyze(reportId);
    } catch (error) {
      await report.addError('website_analysis', error.message);
      await report.updateStatus('failed');
      return;
    }

    // Competitor Analysis
    await report.updateStatus('competitor_analysis', 40);
    try {
      await competitorAnalysisService.analyze(reportId);
    } catch (error) {
      await report.addError('competitor_analysis', error.message);
      await report.updateStatus('failed');
      return;
    }

    // SEO Analysis
    await report.updateStatus('seo_analysis', 60);
    try {
      await seoAnalysisService.analyze(reportId);
    } catch (error) {
      await report.addError('seo_analysis', error.message);
      await report.updateStatus('failed');
      return;
    }

    // Market Research
    await report.updateStatus('market_research', 70);
    try {
      await marketResearchService.analyze(reportId);
    } catch (error) {
      await report.addError('market_research', error.message);
      await report.updateStatus('failed');
      return;
    }

    // Social Proof Analysis
    await report.updateStatus('social_proof_analysis', 80);
    try {
      await socialProofAnalysisService.analyze(reportId);
    } catch (error) {
      await report.addError('social_proof_analysis', error.message);
      await report.updateStatus('failed');
      return;
    }

    // Generate Master Content Bible
    await report.updateStatus('generating_content_bible', 90);
    try {
      await contentBibleGeneratorService.generate(reportId);
    } catch (error) {
      await report.addError('generating_content_bible', error.message);
      await report.updateStatus('failed');
      return;
    }

    // Mark as completed
    await report.updateStatus('completed', 100);
    
    console.log(`CIA analysis completed for report ${reportId}`);
  } catch (error) {
    console.error(`Error in CIA analysis process for report ${reportId}:`, error);
    // Try to update report status if possible
    try {
      const report = await CIAReport.findById(reportId);
      if (report) {
        await report.addError('process', error.message);
        await report.updateStatus('failed');
      }
    } catch (updateError) {
      console.error(`Failed to update error status for report ${reportId}:`, updateError);
    }
  }
}

module.exports = router;
