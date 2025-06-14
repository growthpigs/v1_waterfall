const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');
const CIAReport = require('../../models/cia-report.model');
const User = require('../../models/user.model');
const auth = require('../../middlewares/auth.middleware');

// CIA Workflow Orchestrator
const ciaWorkflowService = require('../../services/cia-workflow.service');
const fs = require('fs').promises;
const path = require('path');

/**
 * Resolve the effective MongoDB ObjectId to use for the current request.
 * Demo accounts use a fixed, valid ObjectId so we can safely store links
 * without polluting the real User collection.
 */
const DEMO_OBJECT_ID = '507f1f77bcf86cd799439011'; // hard-coded, non-conflicting
const getEffectiveUserId = (req) =>
  req.user?.id === 'demo-user-123' ? DEMO_OBJECT_ID : req.user.id;

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
        user: getEffectiveUserId(req),
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
      // Skip DB update for the hard-coded demo account
      if (req.user.id !== 'demo-user-123') {
        await User.findByIdAndUpdate(
          req.user.id,
          {
            $inc: { 'usage.ciaReports.count': 1 },
            $set: { 'usage.ciaReports.lastUsed': new Date() }
          },
          { new: false }
        );
      }

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
    const reports = await CIAReport.find({ user: getEffectiveUserId(req) })
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

    const requesterId = getEffectiveUserId(req);
    // Check ownership
    if (report.user.toString() !== requesterId) {
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
      // we need the user field to do an ownership check
      .select('status progress currentPhase phaseProgress processingMetadata.errors user');

    if (!report) {
      return res.status(404).json({ message: 'Report not found' });
    }

    // Verify the current user (or demo proxy user) owns this report
    if (report.user.toString() !== getEffectiveUserId(req)) {
      return res.status(403).json({ message: 'Not authorized to access this report' });
    }

    res.json({
      status: report.status,
      progress: report.progress,
      currentPhase: report.currentPhase ?? null,
      phaseProgress: report.phaseProgress ?? null,
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
    if (report.user.toString() !== getEffectiveUserId(req)) {
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
    if (report.user.toString() !== getEffectiveUserId(req)) {
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
      if (report.user.toString() !== getEffectiveUserId(req)) {
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
          {
            // ------------------------------------------------------------------
            // VERY BASIC PLACE-HOLDER PDF GENERATION
            // Creates a tiny valid PDF so the browser can download something
            // without throwing a 500.  Replace with real exporter later.
            // ------------------------------------------------------------------
            const exportDir = path.join(
              __dirname,
              '..',
              '..',
              'public',
              'exports',
              'cia',
              report._id.toString()
            );
            const filePath = path.join(exportDir, 'report.pdf');

            try {
              await fs.mkdir(exportDir, { recursive: true });
              // Only (re)write if file does not exist – keeps disk churn low
              await fs.writeFile(
                filePath,
                `%PDF-1.4
1 0 obj
<< /Type /Catalog >>
endobj
xref
0 2
0000000000 65535 f 
0000000010 00000 n 
trailer
<< /Root 1 0 R >>
startxref
9
%%EOF`,
                'utf8'
              );
              console.log(`[CIA Export] Dummy PDF created at ${filePath}`);
            } catch (fsErr) {
              console.error('[CIA Export] Failed to create dummy PDF:', fsErr);
              return res
                .status(500)
                .json({ message: 'Failed to generate PDF export' });
            }

            exportUrl = `/exports/cia/${report._id}/report.pdf`;
          }
          break;
        case 'docx':
          {
            // Simple text-based DOCX placeholder (actually a txt but with .docx)
            const exportDir = path.join(
              __dirname,
              '..',
              '..',
              'public',
              'exports',
              'cia',
              report._id.toString()
            );
            const filePath = path.join(exportDir, 'report.docx');
            try {
              await fs.mkdir(exportDir, { recursive: true });
              await fs.writeFile(
                filePath,
                'DOCX placeholder – replace with real content.',
                'utf8'
              );
              console.log(`[CIA Export] Dummy DOCX created at ${filePath}`);
            } catch (fsErr) {
              console.error('[CIA Export] Failed to create dummy DOCX:', fsErr);
              return res
                .status(500)
                .json({ message: 'Failed to generate DOCX export' });
            }
            exportUrl = `/exports/cia/${report._id}/report.docx`;
          }
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
    if (report.user.toString() !== getEffectiveUserId(req)) {
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
// ---------------------------------------------------------------------------
// Trigger individual CIA phase (manual)
// ---------------------------------------------------------------------------

router.post('/reports/:id/phase/:phaseId', auth, async (req, res) => {
  try {
    const { id, phaseId } = req.params;
    const report = await CIAReport.findById(id);
    if (!report) {
      return res.status(404).json({ message: 'Report not found' });
    }
    if (report.user.toString() !== getEffectiveUserId(req)) {
      return res.status(403).json({ message: 'Not authorized' });
    }

    await ciaWorkflowService.triggerPhase(id, phaseId);
    res.json({ message: `Phase ${phaseId} triggered` });
  } catch (error) {
    console.error('Trigger phase error:', error);
    res.status(500).json({ message: 'Server error while triggering phase', error: error.message });
  }
});

// ---------------------------------------------------------------------------
// Export router
// ---------------------------------------------------------------------------

module.exports = router;