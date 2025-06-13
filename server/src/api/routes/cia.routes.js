const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');
const CIAReport = require('../../models/cia-report.model');
const User = require('../../models/user.model');
const auth = require('../../middlewares/auth.middleware');

// CIA Workflow Orchestrator
const ciaWorkflowService = require('../../services/cia-workflow.service');

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

      // Kick off the CIA workflow asynchronously (queue in prod)
      process.nextTick(() => {
        ciaWorkflowService
          .startWorkflow(savedReport._id)
          .catch(err => console.error('CIA workflow error:', err));
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
/**
 * @route   POST api/cia/reports/:id/run
 * @desc    Start or resume the full CIA workflow
 * @access  Private
 */
router.post('/reports/:id/run', auth, async (req, res) => {
  try {
    const report = await CIAReport.findById(req.params.id);
    if (!report) {
      return res.status(404).json({ message: 'Report not found' });
    }
    if (report.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized' });
    }

    process.nextTick(() =>
      ciaWorkflowService
        .startWorkflow(report._id)
        .catch(err => console.error('CIA workflow error:', err))
    );

    res.json({ message: 'Workflow started/resumed' });
  } catch (error) {
    console.error('Start workflow error:', error);
    res.status(500).json({ message: 'Server error while starting workflow' });
  }
});

/**
 * @route   POST api/cia/reports/:id/phase/:phaseId
 * @desc    Trigger a single CIA phase manually
 * @access  Private
 */
router.post('/reports/:id/phase/:phaseId', auth, async (req, res) => {
  try {
    const { id, phaseId } = req.params;
    const report = await CIAReport.findById(id);
    if (!report) {
      return res.status(404).json({ message: 'Report not found' });
    }
    if (report.user.toString() !== req.user.id) {
      return res.status(403).json({ message: 'Not authorized' });
    }

    await ciaWorkflowService.triggerPhase(id, phaseId);
    res.json({ message: `Phase ${phaseId} triggered` });
  } catch (error) {
    console.error('Trigger phase error:', error);
    res.status(500).json({ message: 'Server error while triggering phase', error: error.message });
  }
});
/**
 * Helper function to start the CIA analysis process
 * LEGACY HELPER REMOVED – workflow now handled by ciaWorkflowService
async function startCIAAnalysisProcess(reportId) {
module.exports = router;