/**
 * Prompt Manager Service
 * 
 * Loads, parses, and manages CIA workflow prompts from markdown files.
 * Supports front-matter metadata extraction, caching, and dynamic variable replacement.
 */

const fs = require('fs').promises;
const path = require('path');
const matter = require('gray-matter');

class PromptManagerService {
  constructor() {
    this.promptsBasePath = path.join(process.cwd(), 'docs', 'cia-workflow', 'prompts');
    this.promptCache = new Map();
    this.initialized = false;
  }

  /**
   * Initialize the prompt manager by loading all prompts
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) return;
    
    try {
      await this.loadAllPrompts();
      this.initialized = true;
      console.log('[PromptManager] Successfully initialized and loaded all prompts');
    } catch (error) {
      console.error('[PromptManager] Initialization failed:', error);
      throw error;
    }
  }

  /**
   * Load all prompts from the prompts directory
   * @returns {Promise<Map>} A map of all loaded prompts
   */
  async loadAllPrompts() {
    try {
      const files = await fs.readdir(this.promptsBasePath);
      const promptFiles = files.filter(file => file.endsWith('.md'));
      
      console.log(`[PromptManager] Found ${promptFiles.length} prompt files`);
      
      for (const file of promptFiles) {
        const filePath = path.join(this.promptsBasePath, file);
        const fileContent = await fs.readFile(filePath, 'utf-8');
        
        try {
          const { promptId, phase, type, prompt, metadata } = this.parsePromptFile(fileContent, file);
          
          // Create a cache key based on phase and type
          const cacheKey = `${phase}:${type}`;
          
          this.promptCache.set(cacheKey, {
            promptId,
            phase,
            type,
            prompt,
            metadata,
            filePath
          });
          
          console.log(`[PromptManager] Loaded prompt: ${promptId} (${phase}:${type})`);
        } catch (parseError) {
          console.error(`[PromptManager] Error parsing prompt file ${file}:`, parseError);
        }
      }
      
      return this.promptCache;
    } catch (error) {
      console.error('[PromptManager] Error loading prompts:', error);
      throw new Error(`Failed to load prompts: ${error.message}`);
    }
  }

  /**
   * Parse a prompt file and extract content and metadata
   * @param {string} fileContent - The content of the prompt file
   * @param {string} fileName - The name of the prompt file
   * @returns {Object} The parsed prompt data
   */
  parsePromptFile(fileContent, fileName) {
    // Parse front-matter and content
    const { data, content } = matter(fileContent);
    
    // Extract metadata from front-matter
    const metadata = { ...data };
    
    // Determine phase and type from filename or metadata
    let phase = metadata.phase || '';
    let type = metadata.type || '';
    
    // If phase/type not in metadata, try to extract from filename
    if (!phase || !type) {
      const fileNameParts = path.basename(fileName, '.md').split('-');
      
      if (fileNameParts.length >= 2) {
        // Format is typically "{phaseId}-{slug}.md"
        phase = phase || fileNameParts[0].toLowerCase();
        
        // Type might be "system", "user", "example-response", etc.
        if (fileName.includes('system')) {
          type = type || 'system';
        } else if (fileName.includes('response') || fileName.includes('bis')) {
          type = type || 'response';
        } else {
          type = type || 'user';
        }
      }
    }
    
    // Generate a promptId from the filename
    const promptId = path.basename(fileName, '.md');
    
    return {
      promptId,
      phase,
      type,
      prompt: content.trim(),
      metadata
    };
  }

  /**
   * Get a prompt by phase and type
   * @param {string} phase - The CIA workflow phase
   * @param {string} type - The prompt type (system, user, response)
   * @returns {Object|null} The prompt data or null if not found
   */
  getPrompt(phase, type) {
    if (!this.initialized) {
      throw new Error('PromptManager not initialized. Call initialize() first.');
    }
    
    const cacheKey = `${phase}:${type}`;
    const prompt = this.promptCache.get(cacheKey);
    
    if (!prompt) {
      console.warn(`[PromptManager] Prompt not found for ${phase}:${type}`);
      return null;
    }
    
    return prompt;
  }

  /**
   * Get all prompts for a specific phase
   * @param {string} phase - The CIA workflow phase
   * @returns {Array<Object>} Array of prompts for the phase
   */
  getPhasePrompts(phase) {
    if (!this.initialized) {
      throw new Error('PromptManager not initialized. Call initialize() first.');
    }
    
    const phasePrompts = [];
    
    for (const [cacheKey, prompt] of this.promptCache.entries()) {
      if (cacheKey.startsWith(`${phase}:`)) {
        phasePrompts.push(prompt);
      }
    }
    
    return phasePrompts;
  }

  /**
   * Apply variables to a prompt template
   * @param {string} promptContent - The prompt content with variables
   * @param {Object} variables - The variables to replace
   * @returns {string} The prompt with variables replaced
   */
  applyVariables(promptContent, variables = {}) {
    let processedPrompt = promptContent;
    
    // Replace variables in format {{variableName}}
    for (const [key, value] of Object.entries(variables)) {
      const regex = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
      processedPrompt = processedPrompt.replace(regex, value);
    }
    
    return processedPrompt;
  }

  /**
   * Get a prompt with variables applied
   * @param {string} phase - The CIA workflow phase
   * @param {string} type - The prompt type
   * @param {Object} variables - Variables to replace in the prompt
   * @returns {string|null} The processed prompt or null if not found
   */
  getProcessedPrompt(phase, type, variables = {}) {
    const promptData = this.getPrompt(phase, type);
    
    if (!promptData) {
      return null;
    }
    
    return this.applyVariables(promptData.prompt, variables);
  }

  /**
   * Reload a specific prompt from disk
   * @param {string} phase - The CIA workflow phase
   * @param {string} type - The prompt type
   * @returns {Promise<Object|null>} The reloaded prompt or null if not found
   */
  async reloadPrompt(phase, type) {
    const cacheKey = `${phase}:${type}`;
    const existingPrompt = this.promptCache.get(cacheKey);
    
    if (!existingPrompt) {
      return null;
    }
    
    try {
      const fileContent = await fs.readFile(existingPrompt.filePath, 'utf-8');
      const fileName = path.basename(existingPrompt.filePath);
      const parsedPrompt = this.parsePromptFile(fileContent, fileName);
      
      this.promptCache.set(cacheKey, {
        ...parsedPrompt,
        filePath: existingPrompt.filePath
      });
      
      console.log(`[PromptManager] Reloaded prompt: ${parsedPrompt.promptId}`);
      return this.promptCache.get(cacheKey);
    } catch (error) {
      console.error(`[PromptManager] Error reloading prompt ${cacheKey}:`, error);
      return null;
    }
  }

  /**
   * Reload all prompts from disk
   * @returns {Promise<Map>} The reloaded prompt cache
   */
  async reloadAllPrompts() {
    this.promptCache.clear();
    this.initialized = false;
    await this.initialize();
    return this.promptCache;
  }

  /**
   * Get all available phases
   * @returns {Array<string>} Array of unique phase identifiers
   */
  getAvailablePhases() {
    const phases = new Set();
    
    for (const [cacheKey] of this.promptCache.entries()) {
      const phase = cacheKey.split(':')[0];
      phases.add(phase);
    }
    
    return Array.from(phases);
  }

  /**
   * Check if a prompt exists
   * @param {string} phase - The CIA workflow phase
   * @param {string} type - The prompt type
   * @returns {boolean} Whether the prompt exists
   */
  hasPrompt(phase, type) {
    const cacheKey = `${phase}:${type}`;
    return this.promptCache.has(cacheKey);
  }
}

// Export a singleton instance
module.exports = new PromptManagerService();
