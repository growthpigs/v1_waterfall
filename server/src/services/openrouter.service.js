/**
 * OpenRouter Service
 * 
 * Provides a unified interface for making AI API calls through OpenRouter
 * with proper error handling, retry logic, and model configuration.
 * This service is used by the CIA workflow for processing AI prompts.
 */

const axios = require('axios');
const { promisify } = require('util');
const sleep = promisify(setTimeout);

// Configuration constants
const DEFAULT_TIMEOUT = 60000; // 60 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 2000; // 2 seconds
const DEFAULT_MODEL = 'anthropic/claude-3-opus-20240229';

// CIA workflow-specific model configurations
const MODEL_CONFIGS = {
  'business-intelligence': {
    model: 'anthropic/claude-3-opus-20240229',
    temperature: 0.2,
    maxTokens: 4000
  },
  'seo-social-intelligence': {
    model: 'anthropic/claude-3-opus-20240229',
    temperature: 0.3,
    maxTokens: 4000
  },
  'strategic-synthesis': {
    model: 'anthropic/claude-3-opus-20240229',
    temperature: 0.4,
    maxTokens: 5000
  },
  'golden-hippo-offer': {
    model: 'anthropic/claude-3-opus-20240229',
    temperature: 0.3,
    maxTokens: 4000
  },
  'convergence-blender': {
    model: 'anthropic/claude-3-opus-20240229',
    temperature: 0.4,
    maxTokens: 5000
  },
  'master-content-bible': {
    model: 'anthropic/claude-3-opus-20240229',
    temperature: 0.2,
    maxTokens: 6000
  }
};

class OpenRouterService {
  constructor() {
    this.apiKey = process.env.OPENROUTER_API_KEY;
    this.baseUrl = process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api';
    /**
     * Service health flag.
     * If `false`, the service is effectively disabled but the
     * application can still start; callers will receive a clear
     * runtime error when they attempt to invoke the API.
     */
    this.isConfigured = Boolean(this.apiKey);

    if (!this.isConfigured) {
      // Don't throw here—let the app boot and fail lazily with a clear message.
      console.warn(
        '[OpenRouter] OPENROUTER_API_KEY is not set: OpenRouter service is DISABLED.'
      );
      return;
    }

    // Initialize axios instance with default configuration
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: DEFAULT_TIMEOUT,
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        // Required by OpenRouter
        'HTTP-Referer': process.env.FRONTEND_URL || 'http://localhost:3000',
        // Helpful for OpenRouter analytics
        'X-Title': 'Operation Waterfall - CIA Workflow'
      }
    });
  }

  /**
   * Get the configuration for a specific CIA workflow phase
   * @param {string} phase - The CIA workflow phase
   * @returns {Object} The model configuration for the phase
   */
  getPhaseConfig(phase) {
    return MODEL_CONFIGS[phase] || MODEL_CONFIGS['business-intelligence'];
  }

  /**
   * Process a prompt through OpenRouter API with retry logic
   * @param {string} prompt - The prompt text
   * @param {string} systemPrompt - The system prompt/instructions
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} The AI response
   */
  async processPrompt(prompt, systemPrompt, options = {}) {
    const {
      phase = 'business-intelligence',
      model = this.getPhaseConfig(phase).model,
      temperature = this.getPhaseConfig(phase).temperature,
      maxTokens = this.getPhaseConfig(phase).maxTokens,
      stream = false,
      jsonMode = false
    } = options;

    if (!this.isConfigured) {
      throw new Error(
        'OpenRouter service is not configured (missing OPENROUTER_API_KEY).'
      );
    }

    const payload = {
      model,
      messages: [
        {
          role: 'system',
          content: systemPrompt
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature,
      max_tokens: maxTokens,
      stream,
      response_format: jsonMode ? { type: 'json_object' } : { type: 'text' }
    };

    let retries = 0;
    while (retries <= MAX_RETRIES) {
      try {
        console.log(`[OpenRouter] Processing ${phase} prompt with model: ${model}`);
        const response = await this.client.post('/v1/chat/completions', payload);
        
        if (stream) {
          return response; // Return the stream directly
        }
        
        return {
          content: response.data.choices[0].message.content,
          usage: response.data.usage,
          model: response.data.model,
          success: true
        };
      } catch (error) {
        retries++;
        
        // Log the error details
        console.error(`[OpenRouter] Error (Attempt ${retries}/${MAX_RETRIES + 1}):`, {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data
        });
        
        // Check if we should retry based on error type
        if (this.shouldRetry(error) && retries <= MAX_RETRIES) {
          const delay = RETRY_DELAY * retries; // Exponential backoff
          console.log(`[OpenRouter] Retrying in ${delay}ms...`);
          await sleep(delay);
          continue;
        }
        
        // If we've exhausted retries or shouldn't retry, throw the error
        throw this.formatError(error);
      }
    }
  }

  /**
   * Process a prompt with streaming response
   * @param {string} prompt - The prompt text
   * @param {string} systemPrompt - The system prompt/instructions
   * @param {function} onChunk - Callback for each chunk of the response
   * @param {Object} options - Additional options
   * @returns {Promise<void>}
   */
  async processPromptStream(prompt, systemPrompt, onChunk, options = {}) {
    const streamOptions = { ...options, stream: true };
    
    try {
      const response = await this.processPrompt(prompt, systemPrompt, streamOptions);
      
      // Process the stream
      response.data.on('data', (chunk) => {
        const lines = chunk.toString().split('\n').filter(line => line.trim() !== '');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.replace(/^data: /, '');
            if (data === '[DONE]') {
              return;
            }
            
            try {
              const parsedData = JSON.parse(data);
              const content = parsedData.choices[0]?.delta?.content;
              
              if (content) {
                onChunk(content);
              }
            } catch (e) {
              console.error('[OpenRouter] Error parsing stream data:', e);
            }
          }
        }
      });
      
      return new Promise((resolve, reject) => {
        response.data.on('end', () => resolve({ success: true }));
        response.data.on('error', (err) => reject(err));
      });
    } catch (error) {
      throw this.formatError(error);
    }
  }

  /**
   * Process multiple prompts in sequence for complex CIA workflows
   * @param {Array<Object>} promptSequence - Array of prompt objects
   * @returns {Promise<Array<Object>>} Array of responses
   */
  async processPromptSequence(promptSequence) {
    const results = [];
    
    for (const promptConfig of promptSequence) {
      const { prompt, systemPrompt, phase, options = {} } = promptConfig;
      
      try {
        const result = await this.processPrompt(prompt, systemPrompt, { phase, ...options });
        results.push(result);
      } catch (error) {
        console.error(`[OpenRouter] Error in prompt sequence at phase ${phase}:`, error);
        throw error; // Stop the sequence if any prompt fails
      }
    }
    
    return results;
  }

  /**
   * Determine if we should retry based on the error
   * @param {Error} error - The error object
   * @returns {boolean} Whether to retry
   */
  shouldRetry(error) {
    // Retry on network errors
    if (!error.response) {
      return true;
    }
    
    // Retry on rate limits and server errors
    const status = error.response.status;
    return status === 429 || status === 500 || status === 502 || status === 503 || status === 504;
  }

  /**
   * Format error for consistent error handling
   * @param {Error} error - The error object
   * @returns {Error} Formatted error
   */
  formatError(error) {
    if (error.response) {
      // API responded with an error status
      const status = error.response.status;
      const data = error.response.data;
      
      let message = `OpenRouter API Error (${status}): `;
      
      if (status === 429) {
        message += 'Rate limit exceeded. Please try again later.';
      } else if (status >= 500) {
        message += 'Server error. Please try again later.';
      } else if (status === 400) {
        message += data.error?.message || 'Invalid request.';
      } else if (status === 401) {
        message += 'Authentication failed. Please check your API key.';
      } else {
        message += data.error?.message || 'Unknown error.';
      }
      
      const formattedError = new Error(message);
      formattedError.status = status;
      formattedError.data = data;
      return formattedError;
    }
    
    // Network error or other error
    return new Error(`OpenRouter Network Error: ${error.message}`);
  }
}

module.exports = new OpenRouterService();
