const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');
const auth = require('../../middlewares/auth.middleware');
const User = require('../../models/user.model');
const config = require('../../config');
const axios = require('axios');
const NodeCache = require('node-cache');

// Cache for DataForSEO responses (TTL: 24 hours)
const dataForSEOCache = new NodeCache({ stdTTL: 86400, checkperiod: 3600 });

// DataForSEO API client
const createDataForSEOClient = (user = null) => {
  // Use user-specific credentials if provided, otherwise use system defaults
  const login = user?.integrations?.dataForSEO?.login || config.dataForSEO.login;
  const password = user?.integrations?.dataForSEO?.password || config.dataForSEO.password;
  const baseUrl = config.dataForSEO.baseUrl;

  if (!login || !password) {
    throw new Error('DataForSEO credentials not configured');
  }

  return axios.create({
    baseURL: baseUrl,
    auth: {
      username: login,
      password: password
    },
    headers: {
      'Content-Type': 'application/json'
    }
  });
};

// Helper to determine if live data should be used
const shouldUseLiveData = (user, requestedLive = false) => {
  // Check if user has premium access for live data
  if (user && user.canAccess('dataForSEOLive')) {
    return requestedLive || user.integrations?.dataForSEO?.useLiveData || false;
  }
  
  // Non-premium users always use non-live data
  return false;
};

/**
 * @route   GET api/dataforseo/status
 * @desc    Check DataForSEO API connection status
 * @access  Private
 */
router.get('/status', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    const client = createDataForSEOClient(user);
    
    // Simple account status check
    const response = await client.get('/v3/merchant/api_status');
    
    res.json({
      status: 'connected',
      apiStatus: response.data,
      useLiveData: shouldUseLiveData(user),
      userCredentials: !!user.integrations?.dataForSEO?.login
    });
  } catch (error) {
    console.error('DataForSEO API status check error:', error);
    res.status(error.response?.status || 500).json({
      status: 'error',
      message: error.response?.data?.message || 'Failed to connect to DataForSEO API',
      error: error.message
    });
  }
});

/**
 * @route   POST api/dataforseo/keywords/research
 * @desc    Perform keyword research
 * @access  Private
 */
router.post(
  '/keywords/research',
  [
    auth,
    check('keyword', 'Keyword is required').notEmpty(),
    check('location', 'Location code must be a number').optional().isInt(),
    check('language', 'Language code must be a number').optional().isInt(),
    check('limit', 'Limit must be a number between 10 and 1000').optional().isInt({ min: 10, max: 1000 }),
    check('useLiveData', 'useLiveData must be a boolean').optional().isBoolean()
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { keyword, location = 2840, language = 0, limit = 100, useLiveData = false } = req.body;
      
      const user = await User.findById(req.user.id);
      const client = createDataForSEOClient(user);
      const useRealTimeData = shouldUseLiveData(user, useLiveData);
      
      // Generate cache key
      const cacheKey = `keyword_research_${keyword}_${location}_${language}_${limit}`;
      
      // Check cache first if not using live data
      if (!useRealTimeData && dataForSEOCache.has(cacheKey)) {
        return res.json({
          source: 'cache',
          data: dataForSEOCache.get(cacheKey)
        });
      }
      
      // Prepare request payload
      const payload = [{
        keyword,
        location_code: location,
        language_code: language,
        limit
      }];
      
      // Make API request
      const endpoint = useRealTimeData 
        ? '/v3/keywords_data/google/search_volume/live' 
        : '/v3/keywords_data/google/search_volume/task_post';
      
      const response = await client.post(endpoint, payload);
      
      // Handle task-based (non-live) response
      if (!useRealTimeData && response.data?.tasks?.[0]?.id) {
        const taskId = response.data.tasks[0].id;
        
        // Wait a moment for the task to complete
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Get task result
        const taskResult = await client.get(`/v3/keywords_data/google/search_volume/task_get/${taskId}`);
        
        if (taskResult.data?.tasks?.[0]?.result) {
          // Cache the result
          dataForSEOCache.set(cacheKey, taskResult.data.tasks[0].result);
          
          return res.json({
            source: 'api',
            data: taskResult.data.tasks[0].result
          });
        } else {
          return res.json({
            source: 'api',
            status: 'pending',
            taskId,
            message: 'Task is still processing. Try again later.'
          });
        }
      }
      
      // Handle live data response
      if (useRealTimeData && response.data?.tasks?.[0]?.result) {
        return res.json({
          source: 'api_live',
          data: response.data.tasks[0].result
        });
      }
      
      // Generic response if we can't parse the specific format
      res.json({
        source: 'api',
        data: response.data
      });
      
      // Update user usage statistics
      await User.findByIdAndUpdate(req.user.id, {
        $inc: { 'usage.apiCalls.dataForSEO': 1 }
      });
    } catch (error) {
      console.error('DataForSEO keyword research error:', error);
      res.status(error.response?.status || 500).json({
        status: 'error',
        message: error.response?.data?.message || 'Failed to perform keyword research',
        error: error.message
      });
    }
  }
);

/**
 * @route   POST api/dataforseo/keywords/suggestions
 * @desc    Get keyword suggestions
 * @access  Private
 */
router.post(
  '/keywords/suggestions',
  [
    auth,
    check('keyword', 'Keyword is required').notEmpty(),
    check('location', 'Location code must be a number').optional().isInt(),
    check('language', 'Language code must be a number').optional().isInt(),
    check('limit', 'Limit must be a number between 10 and 1000').optional().isInt({ min: 10, max: 1000 }),
    check('useLiveData', 'useLiveData must be a boolean').optional().isBoolean()
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { keyword, location = 2840, language = 0, limit = 100, useLiveData = false } = req.body;
      
      const user = await User.findById(req.user.id);
      const client = createDataForSEOClient(user);
      const useRealTimeData = shouldUseLiveData(user, useLiveData);
      
      // Generate cache key
      const cacheKey = `keyword_suggestions_${keyword}_${location}_${language}_${limit}`;
      
      // Check cache first if not using live data
      if (!useRealTimeData && dataForSEOCache.has(cacheKey)) {
        return res.json({
          source: 'cache',
          data: dataForSEOCache.get(cacheKey)
        });
      }
      
      // Prepare request payload
      const payload = [{
        keyword,
        location_code: location,
        language_code: language,
        limit
      }];
      
      // Make API request
      const endpoint = useRealTimeData 
        ? '/v3/keywords_data/google/keywords_for_keywords/live' 
        : '/v3/keywords_data/google/keywords_for_keywords/task_post';
      
      const response = await client.post(endpoint, payload);
      
      // Handle task-based (non-live) response
      if (!useRealTimeData && response.data?.tasks?.[0]?.id) {
        const taskId = response.data.tasks[0].id;
        
        // Wait a moment for the task to complete
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Get task result
        const taskResult = await client.get(`/v3/keywords_data/google/keywords_for_keywords/task_get/${taskId}`);
        
        if (taskResult.data?.tasks?.[0]?.result) {
          // Cache the result
          dataForSEOCache.set(cacheKey, taskResult.data.tasks[0].result);
          
          return res.json({
            source: 'api',
            data: taskResult.data.tasks[0].result
          });
        } else {
          return res.json({
            source: 'api',
            status: 'pending',
            taskId,
            message: 'Task is still processing. Try again later.'
          });
        }
      }
      
      // Handle live data response
      if (useRealTimeData && response.data?.tasks?.[0]?.result) {
        return res.json({
          source: 'api_live',
          data: response.data.tasks[0].result
        });
      }
      
      // Generic response if we can't parse the specific format
      res.json({
        source: 'api',
        data: response.data
      });
      
      // Update user usage statistics
      await User.findByIdAndUpdate(req.user.id, {
        $inc: { 'usage.apiCalls.dataForSEO': 1 }
      });
    } catch (error) {
      console.error('DataForSEO keyword suggestions error:', error);
      res.status(error.response?.status || 500).json({
        status: 'error',
        message: error.response?.data?.message || 'Failed to get keyword suggestions',
        error: error.message
      });
    }
  }
);

/**
 * @route   POST api/dataforseo/serp/analysis
 * @desc    Analyze SERP for a keyword
 * @access  Private
 */
router.post(
  '/serp/analysis',
  [
    auth,
    check('keyword', 'Keyword is required').notEmpty(),
    check('location', 'Location code must be a number').optional().isInt(),
    check('language', 'Language code must be a number').optional().isInt(),
    check('useLiveData', 'useLiveData must be a boolean').optional().isBoolean()
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { keyword, location = 2840, language = 0, useLiveData = false } = req.body;
      
      const user = await User.findById(req.user.id);
      const client = createDataForSEOClient(user);
      const useRealTimeData = shouldUseLiveData(user, useLiveData);
      
      // Generate cache key
      const cacheKey = `serp_analysis_${keyword}_${location}_${language}`;
      
      // Check cache first if not using live data
      if (!useRealTimeData && dataForSEOCache.has(cacheKey)) {
        return res.json({
          source: 'cache',
          data: dataForSEOCache.get(cacheKey)
        });
      }
      
      // Prepare request payload
      const payload = [{
        keyword,
        location_code: location,
        language_code: language,
        depth: 100
      }];
      
      // Make API request
      const endpoint = useRealTimeData 
        ? '/v3/serp/google/organic/live/regular' 
        : '/v3/serp/google/organic/task_post';
      
      const response = await client.post(endpoint, payload);
      
      // Handle task-based (non-live) response
      if (!useRealTimeData && response.data?.tasks?.[0]?.id) {
        const taskId = response.data.tasks[0].id;
        
        // Wait a moment for the task to complete
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Get task result
        const taskResult = await client.get(`/v3/serp/google/organic/task_get/${taskId}`);
        
        if (taskResult.data?.tasks?.[0]?.result) {
          // Cache the result
          dataForSEOCache.set(cacheKey, taskResult.data.tasks[0].result);
          
          return res.json({
            source: 'api',
            data: taskResult.data.tasks[0].result
          });
        } else {
          return res.json({
            source: 'api',
            status: 'pending',
            taskId,
            message: 'Task is still processing. Try again later.'
          });
        }
      }
      
      // Handle live data response
      if (useRealTimeData && response.data?.tasks?.[0]?.result) {
        return res.json({
          source: 'api_live',
          data: response.data.tasks[0].result
        });
      }
      
      // Generic response if we can't parse the specific format
      res.json({
        source: 'api',
        data: response.data
      });
      
      // Update user usage statistics
      await User.findByIdAndUpdate(req.user.id, {
        $inc: { 'usage.apiCalls.dataForSEO': 1 }
      });
    } catch (error) {
      console.error('DataForSEO SERP analysis error:', error);
      res.status(error.response?.status || 500).json({
        status: 'error',
        message: error.response?.data?.message || 'Failed to analyze SERP',
        error: error.message
      });
    }
  }
);

/**
 * @route   POST api/dataforseo/competitors/analysis
 * @desc    Analyze competitors for a domain
 * @access  Private
 */
router.post(
  '/competitors/analysis',
  [
    auth,
    check('domain', 'Domain is required').notEmpty(),
    check('location', 'Location code must be a number').optional().isInt(),
    check('language', 'Language code must be a number').optional().isInt(),
    check('limit', 'Limit must be a number between 10 and 1000').optional().isInt({ min: 10, max: 1000 }),
    check('useLiveData', 'useLiveData must be a boolean').optional().isBoolean()
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { domain, location = 2840, language = 0, limit = 100, useLiveData = false } = req.body;
      
      const user = await User.findById(req.user.id);
      const client = createDataForSEOClient(user);
      const useRealTimeData = shouldUseLiveData(user, useLiveData);
      
      // Generate cache key
      const cacheKey = `competitors_analysis_${domain}_${location}_${language}_${limit}`;
      
      // Check cache first if not using live data
      if (!useRealTimeData && dataForSEOCache.has(cacheKey)) {
        return res.json({
          source: 'cache',
          data: dataForSEOCache.get(cacheKey)
        });
      }
      
      // Prepare request payload
      const payload = [{
        target: domain,
        location_code: location,
        language_code: language,
        limit
      }];
      
      // Make API request
      const endpoint = useRealTimeData 
        ? '/v3/dataforseo_labs/google/domain_competitors/live' 
        : '/v3/dataforseo_labs/google/domain_competitors/task_post';
      
      const response = await client.post(endpoint, payload);
      
      // Handle task-based (non-live) response
      if (!useRealTimeData && response.data?.tasks?.[0]?.id) {
        const taskId = response.data.tasks[0].id;
        
        // Wait a moment for the task to complete
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Get task result
        const taskResult = await client.get(`/v3/dataforseo_labs/google/domain_competitors/task_get/${taskId}`);
        
        if (taskResult.data?.tasks?.[0]?.result) {
          // Cache the result
          dataForSEOCache.set(cacheKey, taskResult.data.tasks[0].result);
          
          return res.json({
            source: 'api',
            data: taskResult.data.tasks[0].result
          });
        } else {
          return res.json({
            source: 'api',
            status: 'pending',
            taskId,
            message: 'Task is still processing. Try again later.'
          });
        }
      }
      
      // Handle live data response
      if (useRealTimeData && response.data?.tasks?.[0]?.result) {
        return res.json({
          source: 'api_live',
          data: response.data.tasks[0].result
        });
      }
      
      // Generic response if we can't parse the specific format
      res.json({
        source: 'api',
        data: response.data
      });
      
      // Update user usage statistics
      await User.findByIdAndUpdate(req.user.id, {
        $inc: { 'usage.apiCalls.dataForSEO': 1 }
      });
    } catch (error) {
      console.error('DataForSEO competitors analysis error:', error);
      res.status(error.response?.status || 500).json({
        status: 'error',
        message: error.response?.data?.message || 'Failed to analyze competitors',
        error: error.message
      });
    }
  }
);

/**
 * @route   POST api/dataforseo/domain/overview
 * @desc    Get domain overview
 * @access  Private
 */
router.post(
  '/domain/overview',
  [
    auth,
    check('domain', 'Domain is required').notEmpty(),
    check('useLiveData', 'useLiveData must be a boolean').optional().isBoolean()
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { domain, useLiveData = false } = req.body;
      
      const user = await User.findById(req.user.id);
      const client = createDataForSEOClient(user);
      const useRealTimeData = shouldUseLiveData(user, useLiveData);
      
      // Generate cache key
      const cacheKey = `domain_overview_${domain}`;
      
      // Check cache first if not using live data
      if (!useRealTimeData && dataForSEOCache.has(cacheKey)) {
        return res.json({
          source: 'cache',
          data: dataForSEOCache.get(cacheKey)
        });
      }
      
      // Prepare request payload
      const payload = [{
        target: domain,
        limit: 100
      }];
      
      // Make API request
      const endpoint = useRealTimeData 
        ? '/v3/dataforseo_labs/google/domain_rank_overview/live' 
        : '/v3/dataforseo_labs/google/domain_rank_overview/task_post';
      
      const response = await client.post(endpoint, payload);
      
      // Handle task-based (non-live) response
      if (!useRealTimeData && response.data?.tasks?.[0]?.id) {
        const taskId = response.data.tasks[0].id;
        
        // Wait a moment for the task to complete
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Get task result
        const taskResult = await client.get(`/v3/dataforseo_labs/google/domain_rank_overview/task_get/${taskId}`);
        
        if (taskResult.data?.tasks?.[0]?.result) {
          // Cache the result
          dataForSEOCache.set(cacheKey, taskResult.data.tasks[0].result);
          
          return res.json({
            source: 'api',
            data: taskResult.data.tasks[0].result
          });
        } else {
          return res.json({
            source: 'api',
            status: 'pending',
            taskId,
            message: 'Task is still processing. Try again later.'
          });
        }
      }
      
      // Handle live data response
      if (useRealTimeData && response.data?.tasks?.[0]?.result) {
        return res.json({
          source: 'api_live',
          data: response.data.tasks[0].result
        });
      }
      
      // Generic response if we can't parse the specific format
      res.json({
        source: 'api',
        data: response.data
      });
      
      // Update user usage statistics
      await User.findByIdAndUpdate(req.user.id, {
        $inc: { 'usage.apiCalls.dataForSEO': 1 }
      });
    } catch (error) {
      console.error('DataForSEO domain overview error:', error);
      res.status(error.response?.status || 500).json({
        status: 'error',
        message: error.response?.data?.message || 'Failed to get domain overview',
        error: error.message
      });
    }
  }
);

/**
 * @route   POST api/dataforseo/website/audit
 * @desc    Perform website audit
 * @access  Private
 */
router.post(
  '/website/audit',
  [
    auth,
    check('url', 'URL is required').isURL(),
    check('useLiveData', 'useLiveData must be a boolean').optional().isBoolean()
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { url, useLiveData = false } = req.body;
      
      const user = await User.findById(req.user.id);
      const client = createDataForSEOClient(user);
      const useRealTimeData = shouldUseLiveData(user, useLiveData);
      
      // Generate cache key
      const cacheKey = `website_audit_${url}`;
      
      // Check cache first if not using live data
      if (!useRealTimeData && dataForSEOCache.has(cacheKey)) {
        return res.json({
          source: 'cache',
          data: dataForSEOCache.get(cacheKey)
        });
      }
      
      // Prepare request payload
      const payload = [{
        target: url,
        max_crawl_pages: 100
      }];
      
      // Make API request
      const endpoint = '/v3/on_page/task_post';
      
      const response = await client.post(endpoint, payload);
      
      if (response.data?.tasks?.[0]?.id) {
        const taskId = response.data.tasks[0].id;
        
        // For on-page audit, we need to wait longer
        await new Promise(resolve => setTimeout(resolve, 10000));
        
        // Get task result
        const taskResult = await client.get(`/v3/on_page/summary/${taskId}`);
        
        if (taskResult.data?.tasks?.[0]?.result) {
          // Cache the result
          dataForSEOCache.set(cacheKey, taskResult.data.tasks[0].result);
          
          return res.json({
            source: 'api',
            data: taskResult.data.tasks[0].result,
            taskId // Include taskId for fetching more detailed results later
          });
        } else {
          return res.json({
            source: 'api',
            status: 'pending',
            taskId,
            message: 'Task is still processing. Try again later.'
          });
        }
      }
      
      // Generic response if we can't parse the specific format
      res.json({
        source: 'api',
        data: response.data
      });
      
      // Update user usage statistics
      await User.findByIdAndUpdate(req.user.id, {
        $inc: { 'usage.apiCalls.dataForSEO': 1 }
      });
    } catch (error) {
      console.error('DataForSEO website audit error:', error);
      res.status(error.response?.status || 500).json({
        status: 'error',
        message: error.response?.data?.message || 'Failed to perform website audit',
        error: error.message
      });
    }
  }
);

/**
 * @route   POST api/dataforseo/backlinks/overview
 * @desc    Get backlinks overview for a domain
 * @access  Private
 */
router.post(
  '/backlinks/overview',
  [
    auth,
    check('target', 'Target domain or URL is required').notEmpty(),
    check('useLiveData', 'useLiveData must be a boolean').optional().isBoolean()
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { target, useLiveData = false } = req.body;
      
      const user = await User.findById(req.user.id);
      const client = createDataForSEOClient(user);
      const useRealTimeData = shouldUseLiveData(user, useLiveData);
      
      // Generate cache key
      const cacheKey = `backlinks_overview_${target}`;
      
      // Check cache first if not using live data
      if (!useRealTimeData && dataForSEOCache.has(cacheKey)) {
        return res.json({
          source: 'cache',
          data: dataForSEOCache.get(cacheKey)
        });
      }
      
      // Prepare request payload
      const payload = [{
        target,
        limit: 100
      }];
      
      // Make API request
      const endpoint = useRealTimeData 
        ? '/v3/backlinks/summary/live' 
        : '/v3/backlinks/summary/task_post';
      
      const response = await client.post(endpoint, payload);
      
      // Handle task-based (non-live) response
      if (!useRealTimeData && response.data?.tasks?.[0]?.id) {
        const taskId = response.data.tasks[0].id;
        
        // Wait a moment for the task to complete
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Get task result
        const taskResult = await client.get(`/v3/backlinks/summary/task_get/${taskId}`);
        
        if (taskResult.data?.tasks?.[0]?.result) {
          // Cache the result
          dataForSEOCache.set(cacheKey, taskResult.data.tasks[0].result);
          
          return res.json({
            source: 'api',
            data: taskResult.data.tasks[0].result
          });
        } else {
          return res.json({
            source: 'api',
            status: 'pending',
            taskId,
            message: 'Task is still processing. Try again later.'
          });
        }
      }
      
      // Handle live data response
      if (useRealTimeData && response.data?.tasks?.[0]?.result) {
        return res.json({
          source: 'api_live',
          data: response.data.tasks[0].result
        });
      }
      
      // Generic response if we can't parse the specific format
      res.json({
        source: 'api',
        data: response.data
      });
      
      // Update user usage statistics
      await User.findByIdAndUpdate(req.user.id, {
        $inc: { 'usage.apiCalls.dataForSEO': 1 }
      });
    } catch (error) {
      console.error('DataForSEO backlinks overview error:', error);
      res.status(error.response?.status || 500).json({
        status: 'error',
        message: error.response?.data?.message || 'Failed to get backlinks overview',
        error: error.message
      });
    }
  }
);

/**
 * @route   POST api/dataforseo/keyword-gap
 * @desc    Analyze keyword gap between domains
 * @access  Private
 */
router.post(
  '/keyword-gap',
  [
    auth,
    check('target', 'Target domain is required').notEmpty(),
    check('competitors', 'Competitors must be an array of domains').isArray().notEmpty(),
    check('location', 'Location code must be a number').optional().isInt(),
    check('language', 'Language code must be a number').optional().isInt(),
    check('limit', 'Limit must be a number between 10 and 1000').optional().isInt({ min: 10, max: 1000 }),
    check('useLiveData', 'useLiveData must be a boolean').optional().isBoolean()
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { target, competitors, location = 2840, language = 0, limit = 100, useLiveData = false } = req.body;
      
      const user = await User.findById(req.user.id);
      const client = createDataForSEOClient(user);
      const useRealTimeData = shouldUseLiveData(user, useLiveData);
      
      // Limit number of competitors
      if (competitors.length > 5) {
        return res.status(400).json({
          message: 'Maximum 5 competitors allowed'
        });
      }
      
      // Generate cache key
      const competitorsString = competitors.sort().join('_');
      const cacheKey = `keyword_gap_${target}_${competitorsString}_${location}_${language}_${limit}`;
      
      // Check cache first if not using live data
      if (!useRealTimeData && dataForSEOCache.has(cacheKey)) {
        return res.json({
          source: 'cache',
          data: dataForSEOCache.get(cacheKey)
        });
      }
      
      // Prepare request payload
      const payload = [{
        target,
        competitors,
        location_code: location,
        language_code: language,
        limit
      }];
      
      // Make API request
      const endpoint = useRealTimeData 
        ? '/v3/dataforseo_labs/google/domain_vs_domain/live' 
        : '/v3/dataforseo_labs/google/domain_vs_domain/task_post';
      
      const response = await client.post(endpoint, payload);
      
      // Handle task-based (non-live) response
      if (!useRealTimeData && response.data?.tasks?.[0]?.id) {
        const taskId = response.data.tasks[0].id;
        
        // Wait a moment for the task to complete
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Get task result
        const taskResult = await client.get(`/v3/dataforseo_labs/google/domain_vs_domain/task_get/${taskId}`);
        
        if (taskResult.data?.tasks?.[0]?.result) {
          // Cache the result
          dataForSEOCache.set(cacheKey, taskResult.data.tasks[0].result);
          
          return res.json({
            source: 'api',
            data: taskResult.data.tasks[0].result
          });
        } else {
          return res.json({
            source: 'api',
            status: 'pending',
            taskId,
            message: 'Task is still processing. Try again later.'
          });
        }
      }
      
      // Handle live data response
      if (useRealTimeData && response.data?.tasks?.[0]?.result) {
        return res.json({
          source: 'api_live',
          data: response.data.tasks[0].result
        });
      }
      
      // Generic response if we can't parse the specific format
      res.json({
        source: 'api',
        data: response.data
      });
      
      // Update user usage statistics
      await User.findByIdAndUpdate(req.user.id, {
        $inc: { 'usage.apiCalls.dataForSEO': 1 }
      });
    } catch (error) {
      console.error('DataForSEO keyword gap analysis error:', error);
      res.status(error.response?.status || 500).json({
        status: 'error',
        message: error.response?.data?.message || 'Failed to analyze keyword gap',
        error: error.message
      });
    }
  }
);

/**
 * @route   GET api/dataforseo/locations
 * @desc    Get available locations
 * @access  Private
 */
router.get('/locations', auth, async (req, res) => {
  try {
    const cacheKey = 'dataforseo_locations';
    
    // Check cache first
    if (dataForSEOCache.has(cacheKey)) {
      return res.json({
        source: 'cache',
        data: dataForSEOCache.get(cacheKey)
      });
    }
    
    const user = await User.findById(req.user.id);
    const client = createDataForSEOClient(user);
    
    // Make API request
    const response = await client.get('/v3/keywords_data/google/locations');
    
    if (response.data?.tasks?.[0]?.result) {
      // Cache the result
      dataForSEOCache.set(cacheKey, response.data.tasks[0].result);
      
      return res.json({
        source: 'api',
        data: response.data.tasks[0].result
      });
    }
    
    // Generic response if we can't parse the specific format
    res.json({
      source: 'api',
      data: response.data
    });
  } catch (error) {
    console.error('DataForSEO locations error:', error);
    res.status(error.response?.status || 500).json({
      status: 'error',
      message: error.response?.data?.message || 'Failed to get locations',
      error: error.message
    });
  }
});

/**
 * @route   GET api/dataforseo/languages
 * @desc    Get available languages
 * @access  Private
 */
router.get('/languages', auth, async (req, res) => {
  try {
    const cacheKey = 'dataforseo_languages';
    
    // Check cache first
    if (dataForSEOCache.has(cacheKey)) {
      return res.json({
        source: 'cache',
        data: dataForSEOCache.get(cacheKey)
      });
    }
    
    const user = await User.findById(req.user.id);
    const client = createDataForSEOClient(user);
    
    // Make API request
    const response = await client.get('/v3/keywords_data/google/languages');
    
    if (response.data?.tasks?.[0]?.result) {
      // Cache the result
      dataForSEOCache.set(cacheKey, response.data.tasks[0].result);
      
      return res.json({
        source: 'api',
        data: response.data.tasks[0].result
      });
    }
    
    // Generic response if we can't parse the specific format
    res.json({
      source: 'api',
      data: response.data
    });
  } catch (error) {
    console.error('DataForSEO languages error:', error);
    res.status(error.response?.status || 500).json({
      status: 'error',
      message: error.response?.data?.message || 'Failed to get languages',
      error: error.message
    });
  }
});

module.exports = router;
