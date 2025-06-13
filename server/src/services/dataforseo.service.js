/**
 * DataForSEO Service
 * 
 * Provides integration with DataForSEO API for keyword research,
 * competitor analysis, and SERP data. This service is used by the
 * CIA workflow for Phase 2 (SEO & Social Intelligence).
 */

const axios = require('axios');
const { promisify } = require('util');
const sleep = promisify(setTimeout);

// Configuration constants
const DEFAULT_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 2000; // 2 seconds
const DEFAULT_LIMIT = 10; // Default number of results to return

class DataForSEOService {
  constructor() {
    this.login = process.env.DATAFORSEO_LOGIN;
    this.password = process.env.DATAFORSEO_PASSWORD;
    this.baseUrl = process.env.DATAFORSEO_BASE_URL || 'https://api.dataforseo.com';
    this.useLiveData = process.env.DATAFORSEO_USE_LIVE_DATA === 'true';
    
    if (!this.login || !this.password) {
      console.warn('[DataForSEO] API credentials not configured. Some features will be unavailable.');
    }
    
    // Initialize axios instance with default configuration
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: DEFAULT_TIMEOUT,
      auth: {
        username: this.login,
        password: this.password
      },
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  /**
   * Check if the service is properly configured
   * @returns {boolean} Whether the service is configured
   */
  isConfigured() {
    return Boolean(this.login && this.password);
  }

  /**
   * Make a request to the DataForSEO API with retry logic
   * @param {string} method - HTTP method (GET, POST, etc.)
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request data (for POST requests)
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} API response
   */
  async makeRequest(method, endpoint, data = null, options = {}) {
    if (!this.isConfigured()) {
      throw new Error('DataForSEO API not configured. Please set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in environment variables.');
    }
    
    let retries = 0;
    while (retries <= MAX_RETRIES) {
      try {
        const requestOptions = {
          method,
          url: endpoint,
          ...options
        };
        
        if (data && (method.toUpperCase() === 'POST' || method.toUpperCase() === 'PUT')) {
          requestOptions.data = data;
        }
        
        console.log(`[DataForSEO] ${method} request to ${endpoint}`);
        const response = await this.client(requestOptions);
        
        // Check if the response indicates an error
        if (response.data && response.data.status_code >= 400) {
          throw new Error(`DataForSEO API error: ${response.data.status_message || 'Unknown error'}`);
        }
        
        return response.data;
      } catch (error) {
        retries++;
        
        // Log the error details
        console.error(`[DataForSEO] Error (Attempt ${retries}/${MAX_RETRIES + 1}):`, {
          message: error.message,
          status: error.response?.status,
          data: error.response?.data
        });
        
        // Check if we should retry based on error type
        if (this.shouldRetry(error) && retries <= MAX_RETRIES) {
          const delay = RETRY_DELAY * retries; // Exponential backoff
          console.log(`[DataForSEO] Retrying in ${delay}ms...`);
          await sleep(delay);
          continue;
        }
        
        // If we've exhausted retries or shouldn't retry, throw the error
        throw this.formatError(error);
      }
    }
  }

  /**
   * Get keyword data for a company/website
   * @param {string} companyName - The company name
   * @param {string} websiteUrl - The website URL
   * @param {string} industry - The industry
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Keyword data
   */
  async getKeywordData(companyName, websiteUrl, industry, options = {}) {
    try {
      // Extract domain from website URL
      const domain = this.extractDomain(websiteUrl);
      
      // Get keyword data from multiple endpoints
      const [keywordSuggestions, organicResults, competitorData] = await Promise.all([
        this.getKeywordSuggestions(companyName, industry, options),
        this.getOrganicResults(domain, options),
        this.getCompetitorData(domain, options)
      ]);
      
      // Combine all data into a single result
      return {
        domain,
        keywordSuggestions,
        organicResults,
        competitorData,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('[DataForSEO] Error getting keyword data:', error);
      
      // If API is not available, return mock data for development
      if (!this.useLiveData) {
        console.log('[DataForSEO] Using mock data instead');
        return this.getMockKeywordData(companyName, websiteUrl, industry);
      }
      
      throw error;
    }
  }

  /**
   * Get keyword suggestions for a seed keyword or company name
   * @param {string} seed - Seed keyword or company name
   * @param {string} industry - Industry for context
   * @param {Object} options - Additional options
   * @returns {Promise<Array>} Keyword suggestions
   */
  async getKeywordSuggestions(seed, industry, options = {}) {
    const { limit = DEFAULT_LIMIT, language = 'en', location = 'United States' } = options;
    
    try {
      // Use the keywords data endpoint
      const data = {
        keywords: [seed, industry],
        language_code: language,
        location_code: this.getLocationCode(location),
        limit
      };
      
      const response = await this.makeRequest(
        'POST',
        '/v3/keywords_data/google/keywords_for_keywords',
        [data]
      );
      
      if (!response.tasks || !response.tasks[0] || !response.tasks[0].result) {
        return [];
      }
      
      // Process and return the keyword suggestions
      return response.tasks[0].result.map(item => ({
        keyword: item.keyword,
        searchVolume: item.search_volume || 0,
        cpc: item.cpc || 0,
        competition: item.competition || 0,
        difficulty: item.keyword_difficulty || 0
      }));
    } catch (error) {
      console.error('[DataForSEO] Error getting keyword suggestions:', error);
      return [];
    }
  }

  /**
   * Get organic search results for a domain
   * @param {string} domain - The domain to analyze
   * @param {Object} options - Additional options
   * @returns {Promise<Array>} Organic search results
   */
  async getOrganicResults(domain, options = {}) {
    const { limit = DEFAULT_LIMIT, language = 'en', location = 'United States' } = options;
    
    try {
      // Use the domain analytics endpoint
      const data = {
        target: domain,
        language_code: language,
        location_code: this.getLocationCode(location),
        limit
      };
      
      const response = await this.makeRequest(
        'POST',
        '/v3/domain_analytics/google/organic_searches',
        [data]
      );
      
      if (!response.tasks || !response.tasks[0] || !response.tasks[0].result) {
        return [];
      }
      
      // Process and return the organic results
      return response.tasks[0].result.map(item => ({
        keyword: item.keyword,
        position: item.position || 0,
        url: item.url || '',
        searchVolume: item.search_volume || 0,
        traffic: item.estimated_visits || 0
      }));
    } catch (error) {
      console.error('[DataForSEO] Error getting organic results:', error);
      return [];
    }
  }

  /**
   * Get competitor data for a domain
   * @param {string} domain - The domain to analyze
   * @param {Object} options - Additional options
   * @returns {Promise<Array>} Competitor data
   */
  async getCompetitorData(domain, options = {}) {
    const { limit = DEFAULT_LIMIT, language = 'en', location = 'United States' } = options;
    
    try {
      // Use the domain vs domain endpoint
      const data = {
        target: domain,
        language_code: language,
        location_code: this.getLocationCode(location),
        limit
      };
      
      const response = await this.makeRequest(
        'POST',
        '/v3/domain_analytics/google/domain_vs_domain',
        [data]
      );
      
      if (!response.tasks || !response.tasks[0] || !response.tasks[0].result) {
        return [];
      }
      
      // Process and return the competitor data
      return response.tasks[0].result.map(item => ({
        domain: item.domain,
        intersections: item.intersections || 0,
        relevanceScore: item.relevance_score || 0,
        commonKeywords: item.common_keywords || []
      }));
    } catch (error) {
      console.error('[DataForSEO] Error getting competitor data:', error);
      return [];
    }
  }

  /**
   * Get SERP data for a keyword
   * @param {string} keyword - The keyword to analyze
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} SERP data
   */
  async getSERPData(keyword, options = {}) {
    const { language = 'en', location = 'United States', device = 'desktop' } = options;
    
    try {
      // Use the SERP endpoint
      const data = {
        keyword,
        language_code: language,
        location_code: this.getLocationCode(location),
        device: device
      };
      
      const response = await this.makeRequest(
        'POST',
        '/v3/serp/google/organic/live',
        [data]
      );
      
      if (!response.tasks || !response.tasks[0] || !response.tasks[0].result) {
        return { items: [] };
      }
      
      // Process and return the SERP data
      return {
        keyword,
        searchVolume: response.tasks[0].result[0]?.search_volume || 0,
        items: response.tasks[0].result[0]?.items?.map(item => ({
          type: item.type,
          rank: item.rank_absolute || 0,
          title: item.title || '',
          url: item.url || '',
          description: item.description || '',
          domain: this.extractDomain(item.url || '')
        })) || []
      };
    } catch (error) {
      console.error('[DataForSEO] Error getting SERP data:', error);
      return { items: [] };
    }
  }

  /**
   * Get content analysis for a URL
   * @param {string} url - The URL to analyze
   * @returns {Promise<Object>} Content analysis data
   */
  async getContentAnalysis(url) {
    try {
      // Use the content analysis endpoint
      const data = {
        url,
        check_spell: true,
        check_grammar: true
      };
      
      const response = await this.makeRequest(
        'POST',
        '/v3/content_analysis/analyze',
        [data]
      );
      
      if (!response.tasks || !response.tasks[0] || !response.tasks[0].result) {
        return {};
      }
      
      // Return the content analysis data
      return response.tasks[0].result[0] || {};
    } catch (error) {
      console.error('[DataForSEO] Error getting content analysis:', error);
      return {};
    }
  }

  /**
   * Get backlink data for a domain
   * @param {string} domain - The domain to analyze
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Backlink data
   */
  async getBacklinkData(domain, options = {}) {
    const { limit = DEFAULT_LIMIT } = options;
    
    try {
      // Use the backlinks endpoint
      const data = {
        target: domain,
        limit
      };
      
      const response = await this.makeRequest(
        'POST',
        '/v3/backlinks/domain_pages',
        [data]
      );
      
      if (!response.tasks || !response.tasks[0] || !response.tasks[0].result) {
        return { items: [] };
      }
      
      // Return the backlink data
      return {
        domain,
        totalBacklinks: response.tasks[0].result[0]?.total_count || 0,
        items: response.tasks[0].result[0]?.items || []
      };
    } catch (error) {
      console.error('[DataForSEO] Error getting backlink data:', error);
      return { items: [] };
    }
  }

  /**
   * Get comprehensive SEO analysis for a website
   * @param {string} websiteUrl - The website URL
   * @param {string} companyName - The company name
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} SEO analysis data
   */
  async getComprehensiveSEOAnalysis(websiteUrl, companyName, options = {}) {
    try {
      const domain = this.extractDomain(websiteUrl);
      
      // Run multiple analyses in parallel
      const [
        keywordData,
        backlinkData,
        contentAnalysis,
        competitorSEOData
      ] = await Promise.all([
        this.getKeywordData(companyName, websiteUrl, options.industry || ''),
        this.getBacklinkData(domain),
        this.getContentAnalysis(websiteUrl),
        this.getCompetitorSEOComparison(domain, options)
      ]);
      
      // Combine all data into a comprehensive analysis
      return {
        domain,
        websiteUrl,
        companyName,
        keywordData,
        backlinkData,
        contentAnalysis,
        competitorSEOData,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('[DataForSEO] Error getting comprehensive SEO analysis:', error);
      
      // If API is not available, return mock data for development
      if (!this.useLiveData) {
        console.log('[DataForSEO] Using mock data instead');
        return this.getMockSEOAnalysis(websiteUrl, companyName);
      }
      
      throw error;
    }
  }

  /**
   * Get competitor SEO comparison
   * @param {string} domain - The domain to analyze
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Competitor SEO comparison data
   */
  async getCompetitorSEOComparison(domain, options = {}) {
    try {
      // Get competitor domains
      const competitorData = await this.getCompetitorData(domain, options);
      const competitorDomains = competitorData.slice(0, 3).map(item => item.domain);
      
      // Get keyword data for each competitor
      const competitorKeywordData = await Promise.all(
        competitorDomains.map(async (competitorDomain) => {
          const data = await this.getOrganicResults(competitorDomain, { limit: 5 });
          return {
            domain: competitorDomain,
            keywords: data
          };
        })
      );
      
      return {
        mainDomain: domain,
        competitors: competitorKeywordData
      };
    } catch (error) {
      console.error('[DataForSEO] Error getting competitor SEO comparison:', error);
      return { competitors: [] };
    }
  }

  /**
   * Get location code for a location name
   * @param {string} location - Location name
   * @returns {number} Location code
   */
  getLocationCode(location) {
    // Common location codes
    const locationCodes = {
      'United States': 2840,
      'United Kingdom': 2826,
      'Canada': 2124,
      'Australia': 2036,
      'Germany': 2276,
      'France': 2250,
      'Spain': 2724,
      'Italy': 2380,
      'Netherlands': 2528,
      'Brazil': 2076,
      'Japan': 2392,
      'India': 2356
    };
    
    return locationCodes[location] || 2840; // Default to US
  }

  /**
   * Extract domain from a URL
   * @param {string} url - The URL
   * @returns {string} The domain
   */
  extractDomain(url) {
    try {
      // Remove protocol and get domain
      let domain = url.replace(/^https?:\/\//, '');
      domain = domain.split('/')[0];
      domain = domain.split('?')[0];
      
      // Remove www. if present
      if (domain.startsWith('www.')) {
        domain = domain.substring(4);
      }
      
      return domain;
    } catch (error) {
      console.error('[DataForSEO] Error extracting domain:', error);
      return url;
    }
  }

  /**
   * Get mock keyword data for development/testing
   * @param {string} companyName - The company name
   * @param {string} websiteUrl - The website URL
   * @param {string} industry - The industry
   * @returns {Object} Mock keyword data
   */
  getMockKeywordData(companyName, websiteUrl, industry) {
    const domain = this.extractDomain(websiteUrl);
    
    return {
      domain,
      keywordSuggestions: [
        { keyword: `${companyName.toLowerCase()} services`, searchVolume: 1200, cpc: 1.5, competition: 0.7, difficulty: 45 },
        { keyword: `${industry.toLowerCase()} solutions`, searchVolume: 2500, cpc: 2.1, competition: 0.8, difficulty: 60 },
        { keyword: `best ${industry.toLowerCase()} company`, searchVolume: 1800, cpc: 3.2, competition: 0.9, difficulty: 75 },
        { keyword: `${companyName.toLowerCase()} pricing`, searchVolume: 800, cpc: 1.0, competition: 0.5, difficulty: 30 },
        { keyword: `${industry.toLowerCase()} trends`, searchVolume: 3200, cpc: 1.8, competition: 0.6, difficulty: 55 }
      ],
      organicResults: [
        { keyword: `${companyName.toLowerCase()}`, position: 1, url: websiteUrl, searchVolume: 2200, traffic: 1500 },
        { keyword: `${companyName.toLowerCase()} reviews`, position: 3, url: `${websiteUrl}/reviews`, searchVolume: 450, traffic: 280 },
        { keyword: `${industry.toLowerCase()} services`, position: 8, url: `${websiteUrl}/services`, searchVolume: 1800, traffic: 120 }
      ],
      competitorData: [
        { domain: `competitor1.com`, intersections: 45, relevanceScore: 0.85, commonKeywords: [`${industry.toLowerCase()} services`, `${industry.toLowerCase()} solutions`] },
        { domain: `competitor2.com`, intersections: 38, relevanceScore: 0.78, commonKeywords: [`${industry.toLowerCase()} pricing`, `${industry.toLowerCase()} company`] },
        { domain: `competitor3.com`, intersections: 29, relevanceScore: 0.65, commonKeywords: [`${industry.toLowerCase()} trends`, `${industry.toLowerCase()} news`] }
      ],
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Get mock SEO analysis data for development/testing
   * @param {string} websiteUrl - The website URL
   * @param {string} companyName - The company name
   * @returns {Object} Mock SEO analysis data
   */
  getMockSEOAnalysis(websiteUrl, companyName) {
    const domain = this.extractDomain(websiteUrl);
    
    return {
      domain,
      websiteUrl,
      companyName,
      keywordData: this.getMockKeywordData(companyName, websiteUrl, 'Digital Marketing'),
      backlinkData: {
        domain,
        totalBacklinks: 1250,
        items: [
          { url: 'https://referrer1.com/article', dofollow: true, page_trust_score: 85 },
          { url: 'https://referrer2.com/review', dofollow: false, page_trust_score: 72 },
          { url: 'https://referrer3.com/directory', dofollow: true, page_trust_score: 65 }
        ]
      },
      contentAnalysis: {
        content_quality: {
          spelling_errors: 3,
          grammar_errors: 5,
          word_count: 1850,
          readability_score: 68
        },
        meta_info: {
          title: `${companyName} - Leading Provider of Digital Marketing Solutions`,
          description: `${companyName} offers cutting-edge digital marketing services to help businesses grow their online presence and increase revenue.`,
          has_meta_description: true,
          has_title: true,
          title_length: 65,
          description_length: 120
        },
        page_structure: {
          has_h1: true,
          has_h2: true,
          has_h3: true,
          has_images: true,
          images_with_alt: 8,
          images_without_alt: 2
        }
      },
      competitorSEOData: {
        mainDomain: domain,
        competitors: [
          {
            domain: 'competitor1.com',
            keywords: [
              { keyword: 'digital marketing services', position: 3, searchVolume: 2200, traffic: 850 },
              { keyword: 'seo company', position: 5, searchVolume: 1800, traffic: 520 }
            ]
          },
          {
            domain: 'competitor2.com',
            keywords: [
              { keyword: 'content marketing agency', position: 2, searchVolume: 1400, traffic: 780 },
              { keyword: 'social media marketing', position: 4, searchVolume: 3200, traffic: 950 }
            ]
          }
        ]
      },
      timestamp: new Date().toISOString()
    };
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
      
      let message = `DataForSEO API Error (${status}): `;
      
      if (status === 429) {
        message += 'Rate limit exceeded. Please try again later.';
      } else if (status >= 500) {
        message += 'Server error. Please try again later.';
      } else if (status === 400) {
        message += data.message || 'Invalid request.';
      } else if (status === 401) {
        message += 'Authentication failed. Please check your API credentials.';
      } else {
        message += data.message || 'Unknown error.';
      }
      
      const formattedError = new Error(message);
      formattedError.status = status;
      formattedError.data = data;
      return formattedError;
    }
    
    // Network error or other error
    return new Error(`DataForSEO Network Error: ${error.message}`);
  }
}

module.exports = new DataForSEOService();
