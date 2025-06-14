/**
 * CIA Workflow Service
 * 
 * Orchestrates the 6-phase CIA workflow process:
 * 1. Business Intelligence
 * 2. SEO & Social Intelligence
 * 3. Strategic Synthesis
 * 4. Golden Hippo Offer
 * 5. Convergence Blender
 * 6. Master Content Bible
 * 
 * This service coordinates between phases, handles data handoffs,
 * manages AI prompt processing, and integrates with external services.
 */

const CIAReport = require('../models/cia-report.model');
const promptManager = require('./prompt-manager.service');
const openRouterService = require('./openrouter.service');
const dataForSEOService = require('./dataforseo.service');
const { promisify } = require('util');
const sleep = promisify(setTimeout);

// CIA Workflow Phase Constants
const PHASES = {
  BUSINESS_INTELLIGENCE: 'business-intelligence',
  SEO_SOCIAL_INTELLIGENCE: 'seo-social-intelligence',
  STRATEGIC_SYNTHESIS: 'strategic-synthesis',
  GOLDEN_HIPPO_OFFER: 'golden-hippo-offer',
  CONVERGENCE_BLENDER: 'convergence-blender',
  MASTER_CONTENT_BIBLE: 'master-content-bible'
};

// Phase to Status Mapping
const PHASE_STATUS_MAP = {
  [PHASES.BUSINESS_INTELLIGENCE]: 'website_analysis',
  [PHASES.SEO_SOCIAL_INTELLIGENCE]: 'seo_analysis',
  [PHASES.STRATEGIC_SYNTHESIS]: 'market_research',
  [PHASES.GOLDEN_HIPPO_OFFER]: 'social_proof_analysis',
  [PHASES.CONVERGENCE_BLENDER]: 'generating_content_bible',
  [PHASES.MASTER_CONTENT_BIBLE]: 'completed'
};

// Phase Progress Percentage Mapping
const PHASE_PROGRESS_MAP = {
  [PHASES.BUSINESS_INTELLIGENCE]: 20,
  [PHASES.SEO_SOCIAL_INTELLIGENCE]: 40,
  [PHASES.STRATEGIC_SYNTHESIS]: 60,
  [PHASES.GOLDEN_HIPPO_OFFER]: 70,
  [PHASES.CONVERGENCE_BLENDER]: 90,
  [PHASES.MASTER_CONTENT_BIBLE]: 100
};

// Phase Dependencies (which phases must be completed before this one)
const PHASE_DEPENDENCIES = {
  [PHASES.BUSINESS_INTELLIGENCE]: [],
  [PHASES.SEO_SOCIAL_INTELLIGENCE]: [PHASES.BUSINESS_INTELLIGENCE],
  [PHASES.STRATEGIC_SYNTHESIS]: [PHASES.BUSINESS_INTELLIGENCE, PHASES.SEO_SOCIAL_INTELLIGENCE],
  [PHASES.GOLDEN_HIPPO_OFFER]: [PHASES.STRATEGIC_SYNTHESIS],
  [PHASES.CONVERGENCE_BLENDER]: [PHASES.GOLDEN_HIPPO_OFFER],
  [PHASES.MASTER_CONTENT_BIBLE]: [PHASES.CONVERGENCE_BLENDER]
};

// Phase Output Field Names (where to store each phase's output in the report)
const PHASE_OUTPUT_FIELDS = {
  // These keys must match the actual schema fields in cia-report.model.js
  [PHASES.BUSINESS_INTELLIGENCE]: 'websiteAnalysis',
  [PHASES.SEO_SOCIAL_INTELLIGENCE]: 'seoIntelligence',
  [PHASES.STRATEGIC_SYNTHESIS]: 'marketResearch',
  [PHASES.GOLDEN_HIPPO_OFFER]: 'socialProofAnalysis',
  [PHASES.CONVERGENCE_BLENDER]: 'competitorAnalysis',
  [PHASES.MASTER_CONTENT_BIBLE]: 'masterContentBible'
};

class CIAWorkflowService {
  constructor() {
    // Initialize prompt manager when service is created
    this.initializePromptManager();
  }

  /**
   * Initialize the prompt manager
   */
  async initializePromptManager() {
    try {
      await promptManager.initialize();
      console.log('[CIAWorkflow] Prompt manager initialized successfully');
    } catch (error) {
      console.error('[CIAWorkflow] Failed to initialize prompt manager:', error);
      // Continue without failing - we'll check for prompts before using them
    }
  }

  /**
   * Start or resume a CIA workflow for a report
   * @param {string} reportId - The ID of the report to process
   * @returns {Promise<Object>} The updated report
   */
  async startWorkflow(reportId) {
    try {
      // Get the report
      const report = await CIAReport.findById(reportId);
      
      if (!report) {
        throw new Error(`Report with ID ${reportId} not found`);
      }
      
      console.log(`[CIAWorkflow] Starting workflow for report ${reportId} (${report.name})`);
      
      // Determine which phase to start from based on current status
      const currentPhase = this.determineCurrentPhase(report);
      
      // Process all phases starting from the current one
      await this.processPhaseSequence(report, currentPhase);
      
      return await CIAReport.findById(reportId);
    } catch (error) {
      console.error(`[CIAWorkflow] Error in workflow for report ${reportId}:`, error);
      
      // Try to update report status if possible
      try {
        const report = await CIAReport.findById(reportId);
        if (report) {
          await report.addError('workflow', error.message);
          await report.updateStatus('failed');
        }
      } catch (updateError) {
        console.error(`[CIAWorkflow] Failed to update error status for report ${reportId}:`, updateError);
      }
      
      throw error;
    }
  }

  /**
   * Determine the current phase based on report status
   * @param {Object} report - The CIA report
   * @returns {string} The current phase ID
   */
  determineCurrentPhase(report) {
    // If the report is new or just initiated, start from the beginning
    if (report.status === 'initiated' || !report.status) {
      return PHASES.BUSINESS_INTELLIGENCE;
    }
    
    // If the report is completed or failed, don't process any phases
    if (report.status === 'completed' || report.status === 'failed') {
      return null;
    }
    
    // Map the report status back to a phase
    for (const [phase, status] of Object.entries(PHASE_STATUS_MAP)) {
      if (status === report.status) {
        return phase;
      }
    }
    
    // Default to starting from the beginning if we can't determine the phase
    return PHASES.BUSINESS_INTELLIGENCE;
  }

  /**
   * Process a sequence of phases starting from the specified phase
   * @param {Object} report - The CIA report
   * @param {string} startPhase - The phase to start from
   * @returns {Promise<void>}
   */
  async processPhaseSequence(report, startPhase) {
    if (!startPhase) {
      console.log(`[CIAWorkflow] No phases to process for report ${report._id}`);
      return;
    }
    
    // Get all phases in order
    const allPhases = Object.values(PHASES);
    const startIndex = allPhases.indexOf(startPhase);
    
    if (startIndex === -1) {
      throw new Error(`Invalid start phase: ${startPhase}`);
    }
    
    // Process each phase in sequence
    for (let i = startIndex; i < allPhases.length; i++) {
      const phase = allPhases[i];
      
      // Update report status for this phase
      // 1-based phase number for client display (0 = idle)
      const phaseNumber = i + 1;

      await report.updateStatus(
        PHASE_STATUS_MAP[phase],   // overall workflow status
        PHASE_PROGRESS_MAP[phase], // coarse overall progress %
        phaseNumber,               // currentPhase for fine-grained tracking
        0                          // reset per-phase progress to 0 at start
      );

      // ------------------------------------------------------------
      // Refresh the report from the database so that each subsequent
      // phase operates on the *latest* data, including the output
      // and completed flags that may have been written by the
      // previous phase inside this same loop.  Without this refresh
      // the in-memory `report` object can become stale, causing the
      // dependency checker to incorrectly think required phases have
      // not completed.
      // ------------------------------------------------------------
      report = await CIAReport.findById(report._id);
      if (!report) {
        throw new Error(
          `Report ${report._id} could not be re-loaded during workflow processing`
        );
      }
      
      // Process the phase
      try {
        await this.processPhase(report, phase);

        // ------------------------------------------------------------------
        // Mark the *current* phase as fully completed (fine-grained tracker)
        // before we move on.  This keeps the frontend phase bars in sync
        // with the back-end even when the overall coarse progress (20, 40…)
        // is unchanged.
        // ------------------------------------------------------------------
        await report.updateStatus(
          PHASE_STATUS_MAP[phase],    // keep same coarse status
          PHASE_PROGRESS_MAP[phase],  // keep same overall %
          phaseNumber,                // still this phase
          100                         // phaseProgress now complete
        );
        
        // Short delay between phases to prevent rate limiting
        await sleep(1000);
      } catch (error) {
        console.error(`[CIAWorkflow] Error in phase ${phase} for report ${report._id}:`, error);
        await report.addError(phase, error.message);
        await report.updateStatus('failed');
        throw error; // Stop the sequence if any phase fails
      }
    }
    
    // Mark as completed when all phases are done
    // Ensure the final phase is reflected as fully complete (phase 6 @ 100 %)
    await report.updateStatus(
      'completed',                     // overall status
      100,                             // overall progress %
      Object.values(PHASES).length,    // currentPhase = last phase (6)
      100                              // phaseProgress = 100 %
    );
    console.log(`[CIAWorkflow] Workflow completed for report ${report._id}`);
  }

  /**
   * Process a single phase of the CIA workflow
   * @param {Object} report - The CIA report
   * @param {string} phase - The phase to process
   * @returns {Promise<Object>} The phase output
   */
  async processPhase(report, phase) {
    console.log(`[CIAWorkflow] Processing phase ${phase} for report ${report._id}`);
    
    // Check dependencies
    await this.checkPhaseDependencies(report, phase);
    
    // Prepare phase inputs
    const phaseInputs = await this.preparePhaseInputs(report, phase);
    
    // Process the phase based on its type
    let phaseOutput;
    
    switch (phase) {
      case PHASES.BUSINESS_INTELLIGENCE:
        phaseOutput = await this.processBusinessIntelligence(report, phaseInputs);
        break;
      case PHASES.SEO_SOCIAL_INTELLIGENCE:
        phaseOutput = await this.processSEOSocialIntelligence(report, phaseInputs);
        break;
      case PHASES.STRATEGIC_SYNTHESIS:
        phaseOutput = await this.processStrategicSynthesis(report, phaseInputs);
        break;
      case PHASES.GOLDEN_HIPPO_OFFER:
        phaseOutput = await this.processGoldenHippoOffer(report, phaseInputs);
        break;
      case PHASES.CONVERGENCE_BLENDER:
        phaseOutput = await this.processConvergenceBlender(report, phaseInputs);
        break;
      case PHASES.MASTER_CONTENT_BIBLE:
        phaseOutput = await this.processMasterContentBible(report, phaseInputs);
        break;
      default:
        throw new Error(`Unknown phase: ${phase}`);
    }
    
    // Validate phase output
    this.validatePhaseOutput(phase, phaseOutput);
    
    // Save phase output to the report
    await this.savePhaseOutput(report, phase, phaseOutput);
    
    return phaseOutput;
  }

  /**
   * Check if all dependencies for a phase are satisfied
   * @param {Object} report - The CIA report
   * @param {string} phase - The phase to check dependencies for
   * @throws {Error} If dependencies are not satisfied
   */
  async checkPhaseDependencies(report, phase) {
    const dependencies = PHASE_DEPENDENCIES[phase];
    
    if (!dependencies || dependencies.length === 0) {
      return; // No dependencies to check
    }
    
    for (const dependency of dependencies) {
      const outputField = PHASE_OUTPUT_FIELDS[dependency];

      // Ensure the dependency phase has produced an output and is marked complete.
      // Optional-chaining avoids TypeErrors when the field is undefined.
      if (!report[outputField]?.completed) {
        throw new Error(
          `Dependency not satisfied: ${dependency} must be completed before ${phase}`
        );
      }
    }
  }

  /**
   * Prepare inputs for a specific phase
   * @param {Object} report - The CIA report
   * @param {string} phase - The phase to prepare inputs for
   * @returns {Object} The phase inputs
   */
  async preparePhaseInputs(report, phase) {
    // Common inputs for all phases
    const commonInputs = {
      reportId: report._id,
      companyName: report.initialData.companyName,
      websiteUrl: report.initialData.websiteUrl,
      industry: report.initialData.industry,
      targetAudience: report.initialData.targetAudience,
      businessGoals: report.initialData.businessGoals,
      contentGoals: report.initialData.contentGoals,
      brandVoice: report.initialData.brandVoice
    };
    
    // Phase-specific inputs
    const phaseInputs = { ...commonInputs };
    
    // Add outputs from previous phases as inputs to this phase
    switch (phase) {
      case PHASES.SEO_SOCIAL_INTELLIGENCE:
        if (report.websiteAnalysis) {
          phaseInputs.businessIntelligence = report.websiteAnalysis;
        }
        break;
        
      case PHASES.STRATEGIC_SYNTHESIS:
        if (report.websiteAnalysis) {
          phaseInputs.businessIntelligence = report.websiteAnalysis;
        }
        if (report.seoIntelligence) {
          phaseInputs.seoSocialIntelligence = report.seoIntelligence;
        }
        break;
        
      case PHASES.GOLDEN_HIPPO_OFFER:
        if (report.marketResearch) {
          phaseInputs.strategicSynthesis = report.marketResearch;
        }
        break;
        
      case PHASES.CONVERGENCE_BLENDER:
        if (report.socialProofAnalysis) {
          phaseInputs.goldenHippoOffer = report.socialProofAnalysis;
        }
        break;
        
      case PHASES.MASTER_CONTENT_BIBLE:
        // Master Content Bible needs all previous outputs
        if (report.websiteAnalysis) {
          phaseInputs.businessIntelligence = report.websiteAnalysis;
        }
        if (report.seoIntelligence) {
          phaseInputs.seoSocialIntelligence = report.seoIntelligence;
        }
        if (report.marketResearch) {
          phaseInputs.strategicSynthesis = report.marketResearch;
        }
        if (report.socialProofAnalysis) {
          phaseInputs.goldenHippoOffer = report.socialProofAnalysis;
        }
        if (report.competitorAnalysis) {
          phaseInputs.convergenceBlender = report.competitorAnalysis;
        }
        break;
    }
    
    return phaseInputs;
  }

  /**
   * Process the Business Intelligence phase
   * @param {Object} report - The CIA report
   * @param {Object} inputs - The phase inputs
   * @returns {Promise<Object>} The phase output
   */
  async processBusinessIntelligence(report, inputs) {
    console.log(`[CIAWorkflow] Processing Business Intelligence for ${report._id}`);
    
    try {
      // Step 1: Prepare the system prompt
      const systemPrompt = promptManager.getProcessedPrompt(
        PHASES.BUSINESS_INTELLIGENCE,
        'system',
        inputs
      );
      
      if (!systemPrompt) {
        throw new Error('Business Intelligence system prompt not found');
      }
      
      // Step 2: Prepare the user prompt with company details
      const userPromptTemplate = promptManager.getProcessedPrompt(
        PHASES.BUSINESS_INTELLIGENCE,
        'user',
        inputs
      );
      
      if (!userPromptTemplate) {
        throw new Error('Business Intelligence user prompt not found');
      }
      
      // Create the actual user prompt with company details
      const userPrompt = this.applyInputsToPrompt(userPromptTemplate, inputs);
      
      // Step 3: Process the prompt with OpenRouter
      const aiResponse = await openRouterService.processPrompt(
        userPrompt,
        systemPrompt,
        {
          phase: PHASES.BUSINESS_INTELLIGENCE,
          jsonMode: true
        }
      );
      
      if (!aiResponse || !aiResponse.content) {
        throw new Error('Failed to get Business Intelligence analysis from AI');
      }
      
      // Step 4: Parse and validate the AI response
      let businessIntelligence;
      try {
        businessIntelligence = JSON.parse(aiResponse.content);
      } catch (error) {
        console.error('[CIAWorkflow] Error parsing Business Intelligence response:', error);
        throw new Error('Invalid JSON response from Business Intelligence analysis');
      }
      
      // Step 5: Add metadata and return
      return {
        completed: true,
        analysis: businessIntelligence,
        websiteAnalysis: {
          url: inputs.websiteUrl,
          completed: true,
          timestamp: new Date()
        },
        competitorAnalysis: {
          completed: true,
          timestamp: new Date()
        },
        aiMetadata: {
          model: aiResponse.model,
          tokensUsed: aiResponse.usage?.total_tokens || 0,
          processingTime: Date.now() - report.processingMetadata.startTime
        }
      };
    } catch (error) {
      console.error('[CIAWorkflow] Business Intelligence error:', error);
      throw error;
    }
  }

  /**
   * Process the SEO & Social Intelligence phase
   * @param {Object} report - The CIA report
   * @param {Object} inputs - The phase inputs
   * @returns {Promise<Object>} The phase output
   */
  async processSEOSocialIntelligence(report, inputs) {
    console.log(`[CIAWorkflow] Processing SEO & Social Intelligence for ${report._id}`);
    
    try {
      // Step 1: Get SEO data from DataForSEO if available
      let seoData = {};
      try {
        if (dataForSEOService) {
          seoData = await dataForSEOService.getKeywordData(
            inputs.companyName,
            inputs.websiteUrl,
            inputs.industry
          );
          
          // Increment the API call counter
          await CIAReport.findByIdAndUpdate(report._id, {
            $inc: { 'processingMetadata.apiCalls.dataForSEO': 1 }
          });
        }
      } catch (seoError) {
        console.warn('[CIAWorkflow] DataForSEO error, continuing with AI only:', seoError);
        // Continue without SEO data - the AI will make recommendations based on other inputs
      }
      
      // Step 2: Prepare the system prompt
      const systemPrompt = promptManager.getProcessedPrompt(
        PHASES.SEO_SOCIAL_INTELLIGENCE,
        'system',
        inputs
      );
      
      if (!systemPrompt) {
        throw new Error('SEO & Social Intelligence system prompt not found');
      }
      
      // Step 3: Prepare the user prompt with inputs and SEO data
      const userPromptTemplate = promptManager.getProcessedPrompt(
        PHASES.SEO_SOCIAL_INTELLIGENCE,
        'user',
        inputs
      );
      
      if (!userPromptTemplate) {
        throw new Error('SEO & Social Intelligence user prompt not found');
      }
      
      // Create the actual user prompt with inputs and SEO data
      const userPrompt = this.applyInputsToPrompt(userPromptTemplate, {
        ...inputs,
        seoData: JSON.stringify(seoData, null, 2)
      });
      
      // Step 4: Process the prompt with OpenRouter
      const aiResponse = await openRouterService.processPrompt(
        userPrompt,
        systemPrompt,
        {
          phase: PHASES.SEO_SOCIAL_INTELLIGENCE,
          jsonMode: true
        }
      );
      
      if (!aiResponse || !aiResponse.content) {
        throw new Error('Failed to get SEO & Social Intelligence analysis from AI');
      }
      
      // Step 5: Parse and validate the AI response
      let seoSocialIntelligence;
      try {
        seoSocialIntelligence = JSON.parse(aiResponse.content);
      } catch (error) {
        console.error('[CIAWorkflow] Error parsing SEO & Social Intelligence response:', error);
        throw new Error('Invalid JSON response from SEO & Social Intelligence analysis');
      }
      
      // Step 6: Add metadata and return
      return {
        completed: true,
        analysis: seoSocialIntelligence,
        seoAnalysis: {
          completed: true,
          keywords: seoSocialIntelligence.keywordStrategy || {},
          timestamp: new Date()
        },
        socialAnalysis: {
          completed: true,
          platforms: seoSocialIntelligence.socialMediaStrategy || {},
          timestamp: new Date()
        },
        dataForSEOResults: seoData,
        aiMetadata: {
          model: aiResponse.model,
          tokensUsed: aiResponse.usage?.total_tokens || 0,
          processingTime: Date.now() - report.processingMetadata.startTime
        }
      };
    } catch (error) {
      console.error('[CIAWorkflow] SEO & Social Intelligence error:', error);
      throw error;
    }
  }

  /**
   * Process the Strategic Synthesis phase
   * @param {Object} report - The CIA report
   * @param {Object} inputs - The phase inputs
   * @returns {Promise<Object>} The phase output
   */
  async processStrategicSynthesis(report, inputs) {
    console.log(`[CIAWorkflow] Processing Strategic Synthesis for ${report._id}`);
    
    try {
      // Step 1: Prepare the system prompt
      const systemPrompt = promptManager.getProcessedPrompt(
        PHASES.STRATEGIC_SYNTHESIS,
        'system',
        inputs
      );
      
      if (!systemPrompt) {
        throw new Error('Strategic Synthesis system prompt not found');
      }
      
      // Step 2: Prepare the user prompt with previous analysis results
      const userPromptTemplate = promptManager.getProcessedPrompt(
        PHASES.STRATEGIC_SYNTHESIS,
        'user',
        inputs
      );
      
      if (!userPromptTemplate) {
        throw new Error('Strategic Synthesis user prompt not found');
      }
      
      // Create the actual user prompt with previous analysis results
      const userPrompt = this.applyInputsToPrompt(userPromptTemplate, {
        ...inputs,
        businessIntelligenceResults: JSON.stringify(inputs.businessIntelligence?.analysis || {}, null, 2),
        seoSocialIntelligenceResults: JSON.stringify(inputs.seoSocialIntelligence?.analysis || {}, null, 2)
      });
      
      // Step 3: Process the prompt with OpenRouter
      const aiResponse = await openRouterService.processPrompt(
        userPrompt,
        systemPrompt,
        {
          phase: PHASES.STRATEGIC_SYNTHESIS,
          jsonMode: true
        }
      );
      
      if (!aiResponse || !aiResponse.content) {
        throw new Error('Failed to get Strategic Synthesis analysis from AI');
      }
      
      // Step 4: Parse and validate the AI response
      let strategicSynthesis;
      try {
        strategicSynthesis = JSON.parse(aiResponse.content);
      } catch (error) {
        console.error('[CIAWorkflow] Error parsing Strategic Synthesis response:', error);
        throw new Error('Invalid JSON response from Strategic Synthesis analysis');
      }
      
      // Step 5: Add metadata and return
      return {
        completed: true,
        analysis: strategicSynthesis,
        marketResearch: {
          completed: true,
          insights: strategicSynthesis.marketInsights || {},
          timestamp: new Date()
        },
        aiMetadata: {
          model: aiResponse.model,
          tokensUsed: aiResponse.usage?.total_tokens || 0,
          processingTime: Date.now() - report.processingMetadata.startTime
        }
      };
    } catch (error) {
      console.error('[CIAWorkflow] Strategic Synthesis error:', error);
      throw error;
    }
  }

  /**
   * Process the Golden Hippo Offer phase
   * @param {Object} report - The CIA report
   * @param {Object} inputs - The phase inputs
   * @returns {Promise<Object>} The phase output
   */
  async processGoldenHippoOffer(report, inputs) {
    console.log(`[CIAWorkflow] Processing Golden Hippo Offer for ${report._id}`);
    
    try {
      // Step 1: Prepare the system prompt
      const systemPrompt = promptManager.getProcessedPrompt(
        PHASES.GOLDEN_HIPPO_OFFER,
        'system',
        inputs
      );
      
      if (!systemPrompt) {
        throw new Error('Golden Hippo Offer system prompt not found');
      }
      
      // Step 2: Prepare the user prompt with strategic synthesis results
      const userPromptTemplate = promptManager.getProcessedPrompt(
        PHASES.GOLDEN_HIPPO_OFFER,
        'user',
        inputs
      );
      
      if (!userPromptTemplate) {
        throw new Error('Golden Hippo Offer user prompt not found');
      }
      
      // Create the actual user prompt with strategic synthesis results
      const userPrompt = this.applyInputsToPrompt(userPromptTemplate, {
        ...inputs,
        strategicSynthesisResults: JSON.stringify(inputs.strategicSynthesis?.analysis || {}, null, 2)
      });
      
      // Step 3: Process the prompt with OpenRouter
      const aiResponse = await openRouterService.processPrompt(
        userPrompt,
        systemPrompt,
        {
          phase: PHASES.GOLDEN_HIPPO_OFFER,
          jsonMode: true
        }
      );
      
      if (!aiResponse || !aiResponse.content) {
        throw new Error('Failed to get Golden Hippo Offer analysis from AI');
      }
      
      // Step 4: Parse and validate the AI response
      let goldenHippoOffer;
      try {
        goldenHippoOffer = JSON.parse(aiResponse.content);
      } catch (error) {
        console.error('[CIAWorkflow] Error parsing Golden Hippo Offer response:', error);
        throw new Error('Invalid JSON response from Golden Hippo Offer analysis');
      }
      
      // Step 5: Add metadata and return
      return {
        completed: true,
        analysis: goldenHippoOffer,
        offerStrategy: {
          completed: true,
          offers: goldenHippoOffer.offers || [],
          pricingStrategy: goldenHippoOffer.pricingStrategy || {},
          valueProposition: goldenHippoOffer.valueProposition || {},
          timestamp: new Date()
        },
        ninetyDayPlan: {
          completed: true,
          milestones: goldenHippoOffer.ninetyDayPlan || [],
          timestamp: new Date()
        },
        aiMetadata: {
          model: aiResponse.model,
          tokensUsed: aiResponse.usage?.total_tokens || 0,
          processingTime: Date.now() - report.processingMetadata.startTime
        }
      };
    } catch (error) {
      console.error('[CIAWorkflow] Golden Hippo Offer error:', error);
      throw error;
    }
  }

  /**
   * Process the Convergence Blender phase
   * @param {Object} report - The CIA report
   * @param {Object} inputs - The phase inputs
   * @returns {Promise<Object>} The phase output
   */
  async processConvergenceBlender(report, inputs) {
    console.log(`[CIAWorkflow] Processing Convergence Blender for ${report._id}`);
    
    try {
      // Step 1: Prepare the system prompt
      const systemPrompt = promptManager.getProcessedPrompt(
        PHASES.CONVERGENCE_BLENDER,
        'system',
        inputs
      );
      
      if (!systemPrompt) {
        throw new Error('Convergence Blender system prompt not found');
      }
      
      // Step 2: Prepare the user prompt with golden hippo offer results
      const userPromptTemplate = promptManager.getProcessedPrompt(
        PHASES.CONVERGENCE_BLENDER,
        'user',
        inputs
      );
      
      if (!userPromptTemplate) {
        throw new Error('Convergence Blender user prompt not found');
      }
      
      // Create the actual user prompt with golden hippo offer results
      const userPrompt = this.applyInputsToPrompt(userPromptTemplate, {
        ...inputs,
        goldenHippoOfferResults: JSON.stringify(inputs.goldenHippoOffer?.analysis || {}, null, 2)
      });
      
      // Step 3: Process the prompt with OpenRouter
      const aiResponse = await openRouterService.processPrompt(
        userPrompt,
        systemPrompt,
        {
          phase: PHASES.CONVERGENCE_BLENDER,
          jsonMode: true
        }
      );
      
      if (!aiResponse || !aiResponse.content) {
        throw new Error('Failed to get Convergence Blender analysis from AI');
      }
      
      // Step 4: Parse and validate the AI response
      let convergenceBlender;
      try {
        convergenceBlender = JSON.parse(aiResponse.content);
      } catch (error) {
        console.error('[CIAWorkflow] Error parsing Convergence Blender response:', error);
        throw new Error('Invalid JSON response from Convergence Blender analysis');
      }
      
      // Step 5: Add metadata and return
      return {
        completed: true,
        analysis: convergenceBlender,
        contentSilos: {
          completed: true,
          silos: convergenceBlender.contentSilos || [],
          weeklyPlan: convergenceBlender.weeklyPlan || {},
          timestamp: new Date()
        },
        contentTypes: {
          completed: true,
          recommendations: convergenceBlender.contentTypes || {},
          timestamp: new Date()
        },
        aiMetadata: {
          model: aiResponse.model,
          tokensUsed: aiResponse.usage?.total_tokens || 0,
          processingTime: Date.now() - report.processingMetadata.startTime
        }
      };
    } catch (error) {
      console.error('[CIAWorkflow] Convergence Blender error:', error);
      throw error;
    }
  }

  /**
   * Process the Master Content Bible phase
   * @param {Object} report - The CIA report
   * @param {Object} inputs - The phase inputs
   * @returns {Promise<Object>} The phase output
   */
  async processMasterContentBible(report, inputs) {
    console.log(`[CIAWorkflow] Processing Master Content Bible for ${report._id}`);
    
    try {
      // Step 1: Prepare the system prompt
      const systemPrompt = promptManager.getProcessedPrompt(
        PHASES.MASTER_CONTENT_BIBLE,
        'system',
        inputs
      );
      
      if (!systemPrompt) {
        throw new Error('Master Content Bible system prompt not found');
      }
      
      // Step 2: Prepare the user prompt with all previous results
      const userPromptTemplate = promptManager.getProcessedPrompt(
        PHASES.MASTER_CONTENT_BIBLE,
        'user',
        inputs
      );
      
      if (!userPromptTemplate) {
        throw new Error('Master Content Bible user prompt not found');
      }
      
      // Create the actual user prompt with all previous results
      const userPrompt = this.applyInputsToPrompt(userPromptTemplate, {
        ...inputs,
        businessIntelligenceResults: JSON.stringify(inputs.businessIntelligence?.analysis || {}, null, 2),
        seoSocialIntelligenceResults: JSON.stringify(inputs.seoSocialIntelligence?.analysis || {}, null, 2),
        strategicSynthesisResults: JSON.stringify(inputs.strategicSynthesis?.analysis || {}, null, 2),
        goldenHippoOfferResults: JSON.stringify(inputs.goldenHippoOffer?.analysis || {}, null, 2),
        convergenceBlenderResults: JSON.stringify(inputs.convergenceBlender?.analysis || {}, null, 2)
      });
      
      // Step 3: Process the prompt with OpenRouter
      const aiResponse = await openRouterService.processPrompt(
        userPrompt,
        systemPrompt,
        {
          phase: PHASES.MASTER_CONTENT_BIBLE,
          jsonMode: true
        }
      );
      
      if (!aiResponse || !aiResponse.content) {
        throw new Error('Failed to get Master Content Bible from AI');
      }
      
      // Step 4: Parse and validate the AI response
      let masterContentBible;
      try {
        masterContentBible = JSON.parse(aiResponse.content);
      } catch (error) {
        console.error('[CIAWorkflow] Error parsing Master Content Bible response:', error);
        throw new Error('Invalid JSON response from Master Content Bible generation');
      }
      
      // Step 5: Add metadata and return
      return {
        completed: true,
        analysis: masterContentBible,
        brandNarrative: masterContentBible.brandNarrative || {},
        contentStrategy: masterContentBible.contentStrategy || {},
        keywordStrategy: masterContentBible.keywordStrategy || {},
        contentRecommendations: masterContentBible.contentRecommendations || {},
        contentFormulas: masterContentBible.contentFormulas || {},
        brandGuidelines: masterContentBible.brandGuidelines || {},
        competitiveInsights: masterContentBible.competitiveInsights || {},
        timestamp: new Date(),
        aiMetadata: {
          model: aiResponse.model,
          tokensUsed: aiResponse.usage?.total_tokens || 0,
          processingTime: Date.now() - report.processingMetadata.startTime
        }
      };
    } catch (error) {
      console.error('[CIAWorkflow] Master Content Bible error:', error);
      throw error;
    }
  }

  /**
   * Apply input variables to a prompt template
   * @param {string} promptTemplate - The prompt template with variables
   * @param {Object} inputs - The input variables
   * @returns {string} The processed prompt
   */
  applyInputsToPrompt(promptTemplate, inputs) {
    let processedPrompt = promptTemplate;
    
    // Replace variables in format {{variableName}}
    for (const [key, value] of Object.entries(inputs)) {
      if (value !== undefined && value !== null) {
        let stringValue;
        
        if (typeof value === 'object') {
          stringValue = JSON.stringify(value, null, 2);
        } else {
          stringValue = String(value);
        }
        
        const regex = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
        processedPrompt = processedPrompt.replace(regex, stringValue);
      }
    }
    
    return processedPrompt;
  }

  /**
   * Validate the output of a phase
   * @param {string} phase - The phase ID
   * @param {Object} output - The phase output
   * @throws {Error} If validation fails
   */
  validatePhaseOutput(phase, output) {
    if (!output || typeof output !== 'object') {
      throw new Error(`Invalid output for phase ${phase}: output must be an object`);
    }
    
    if (!output.completed) {
      throw new Error(`Invalid output for phase ${phase}: missing 'completed' flag`);
    }
    
    if (!output.analysis || typeof output.analysis !== 'object') {
      throw new Error(`Invalid output for phase ${phase}: missing or invalid 'analysis' object`);
    }
    
    // Phase-specific validations could be added here
  }

  /**
   * Save phase output to the report
   * @param {Object} report - The CIA report
   * @param {string} phase - The phase ID
   * @param {Object} output - The phase output
   * @returns {Promise<Object>} The updated report
   */
  async savePhaseOutput(report, phase, output) {
    const outputField = PHASE_OUTPUT_FIELDS[phase];
    
    if (!outputField) {
      throw new Error(`Unknown output field for phase ${phase}`);
    }
    
    // Update the report with the phase output
    const updateData = {
      [outputField]: output
    };
    
    // Update processing metadata
    updateData['processingMetadata.endTime'] = new Date();
    updateData['processingMetadata.totalDuration'] = 
      (new Date() - report.processingMetadata.startTime) / 1000;
    
    // Save the updated report
    return await CIAReport.findByIdAndUpdate(
      report._id,
      { $set: updateData },
      { new: true }
    );
  }

  /**
   * Manually trigger a specific phase for a report
   * @param {string} reportId - The ID of the report
   * @param {string} phase - The phase to trigger
   * @returns {Promise<Object>} The updated report
   */
  async triggerPhase(reportId, phase) {
    try {
      // Get the report
      const report = await CIAReport.findById(reportId);
      
      if (!report) {
        throw new Error(`Report with ID ${reportId} not found`);
      }
      
      // Check if the phase is valid
      if (!Object.values(PHASES).includes(phase)) {
        throw new Error(`Invalid phase: ${phase}`);
      }
      
      // Update report status for this phase
      // 1-based index of the selected phase for finer-grained tracking
      const phaseNumber =
        Object.values(PHASES).indexOf(phase) + 1;

      await report.updateStatus(
        PHASE_STATUS_MAP[phase],    // coarse workflow status
        PHASE_PROGRESS_MAP[phase],  // overall progress %
        phaseNumber,                // currentPhase indicator
        0                            // reset per-phase progress
      );
      
      // Process just this phase
      await this.processPhase(report, phase);

      // Mark the individual phase as fully completed (phaseProgress = 100)
      await report.updateStatus(
        PHASE_STATUS_MAP[phase],    // keep same coarse status
        PHASE_PROGRESS_MAP[phase],  // keep same overall %
        phaseNumber,                // still this phase
        100                          // phase completed
      );
      
      return await CIAReport.findById(reportId);
    } catch (error) {
      console.error(`[CIAWorkflow] Error triggering phase ${phase} for report ${reportId}:`, error);
      
      // Try to update report status if possible
      try {
        const report = await CIAReport.findById(reportId);
        if (report) {
          await report.addError(phase, error.message);
          await report.updateStatus('failed');
        }
      } catch (updateError) {
        console.error(`[CIAWorkflow] Failed to update error status for report ${reportId}:`, updateError);
      }
      
      throw error;
    }
  }

  /**
   * Get the available phases and their dependencies
   * @returns {Object} Phase information
   */
  getPhaseInfo() {
    return {
      phases: Object.values(PHASES),
      dependencies: PHASE_DEPENDENCIES,
      progressMap: PHASE_PROGRESS_MAP,
      statusMap: PHASE_STATUS_MAP
    };
  }
}

// Export a singleton instance
module.exports = new CIAWorkflowService();
