import axios from 'axios';

/**
 * Feature 11: API Service Layer
 * Module: services/api.js
 * 
 * Purpose (Feature 11.1):
 * - Centralize all API calls
 * - Handle request/response formatting
 * - Manage errors consistently
 * - Add request interceptors if needed
 */

// ============================================
// Feature 11.1 - API Client Configuration
// ============================================

/**
 * Configuration from environment variables
 * @see Frontend/.env for configuration
 */
const CONFIG = {
  // Base URL from environment variable
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  
  // Timeout settings (30s for ML model processing)
  timeout: 30000,
  
  // File size limit (in MB)
  maxFileSizeMB: parseInt(import.meta.env.VITE_MAX_FILE_SIZE_MB) || 5,
  
  // Retry settings
  maxRetries: 2,
  retryDelay: 1000,
};

/**
 * API Client Setup with axios
 * - Base URL from environment
 * - Default headers
 * - Timeout settings
 */
const apiClient = axios.create({
  baseURL: CONFIG.baseURL,
  timeout: CONFIG.timeout,
  headers: {
    'Accept': 'application/json',
  },
});

// ============================================
// Request Interceptor
// ============================================
apiClient.interceptors.request.use(
  (config) => {
    // Add timestamp for debugging
    config.metadata = { startTime: new Date() };
    
    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    }
    
    // Future: Add auth tokens here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ============================================
// Response Interceptor
// ============================================
apiClient.interceptors.response.use(
  (response) => {
    // Calculate request duration
    if (response.config.metadata) {
      const duration = new Date() - response.config.metadata.startTime;
      if (import.meta.env.DEV) {
        console.log(`[API] Response received in ${duration}ms`);
      }
    }
    return response;
  },
  (error) => {
    // Log errors in development
    if (import.meta.env.DEV) {
      console.error('[API] Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// ============================================
// Error Handling (Feature 11.1)
// ============================================

/**
 * Format error messages for user display
 * Handles different error types consistently
 * 
 * @param {Error} error - Axios error object
 * @returns {string} - User-friendly error message
 */
const formatError = (error) => {
  // Server responded with error status
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    // Handle specific status codes
    switch (status) {
      case 400:
        // Validation errors
        return data.error || data.message || 'Invalid request. Please check your inputs.';
      
      case 401:
        return 'Authentication required. Please log in.';
      
      case 403:
        return 'Access denied. You do not have permission.';
      
      case 404:
        return 'Resource not found. Please try again.';
      
      case 413:
        return `File is too large. Maximum size is ${CONFIG.maxFileSizeMB}MB.`;
      
      case 429:
        return 'Too many requests. Please wait a moment and try again.';
      
      case 500:
      case 502:
      case 503:
        return 'Server error. Please try again later.';
      
      default:
        return data.error || data.message || `Error: ${status} ${error.response.statusText}`;
    }
  }
  
  // Request made but no response (network error)
  if (error.request) {
    return 'Cannot connect to server. Please check your internet connection.';
  }
  
  // Timeout error
  if (error.code === 'ECONNABORTED') {
    return 'Request timed out. The analysis is taking longer than expected.';
  }
  
  // Request setup error
  return error.message || 'An unexpected error occurred.';
};

/**
 * Retry a failed request with exponential backoff
 * 
 * @param {Function} requestFn - The request function to retry
 * @param {number} maxRetries - Maximum retry attempts
 * @returns {Promise} - The request result
 */
const retryRequest = async (requestFn, maxRetries = CONFIG.maxRetries) => {
  let lastError;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      
      // Don't retry on client errors (4xx) except 429
      if (error.response && error.response.status >= 400 && error.response.status < 500 && error.response.status !== 429) {
        throw error;
      }
      
      // Wait before retrying (exponential backoff)
      if (attempt < maxRetries) {
        const delay = CONFIG.retryDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError;
};

/**
 * Validate response structure
 * 
 * @param {Object} response - API response data
 * @param {string[]} requiredFields - Required field names
 * @returns {boolean} - Whether response is valid
 */
const validateResponse = (response, requiredFields = []) => {
  if (!response || typeof response !== 'object') {
    return false;
  }
  return requiredFields.every(field => field in response);
};

// ============================================
// Feature 11.3 - Response Processing
// ============================================

/**
 * Process prediction response from the API
 * 
 * Process:
 * 1. Check response.success flag (or presence of data)
 * 2. If success:
 *    - Extract prediction data
 *    - Extract recommendations
 *    - Return formatted data
 * 3. If error:
 *    - Extract error message
 *    - Throw formatted error
 *    - Let caller handle display
 * 
 * @param {Object} rawResponse - Raw API response
 * @returns {Object} - Formatted prediction result
 * @throws {Error} - If response indicates failure
 */
const processPredictionResponse = (rawResponse) => {
  // Step 1: Check response.success flag or error presence
  if (!rawResponse) {
    throw new Error('Empty response received from server.');
  }
  
  // Check for explicit error
  if (rawResponse.success === false || rawResponse.error) {
    // Step 3: Extract error message and throw
    const errorMessage = rawResponse.error?.message 
      || rawResponse.error 
      || rawResponse.message 
      || 'Analysis failed. Please try again.';
    throw new Error(errorMessage);
  }
  
  // Step 2: Success - Extract and format data
  const formattedResult = {
    // Prediction data
    prediction: extractPredictionData(rawResponse),
    
    // Symptom analysis (if available)
    symptomAnalysis: extractSymptomAnalysis(rawResponse),
    
    // Severity assessment (if available)
    severity: extractSeverityData(rawResponse),
    
    // Recommendations
    recommendations: extractRecommendations(rawResponse),
    
    // Disclaimer
    disclaimer: rawResponse.disclaimer || getDefaultDisclaimer(),
    
    // Raw data for debugging
    _raw: import.meta.env.DEV ? rawResponse : undefined,
  };
  
  return formattedResult;
};

/**
 * Extract prediction data from response
 * @param {Object} response - API response
 * @returns {Object} - Formatted prediction
 */
const extractPredictionData = (response) => {
  // Handle different response formats
  const prediction = response.prediction || response;
  
  return {
    disease: prediction.disease 
      || prediction.condition_name 
      || prediction.predicted_disease 
      || 'Unknown',
    confidence: prediction.confidence ?? prediction.confidence_score ?? 0,
    confidenceLevel: prediction.confidence_level 
      || getConfidenceLevel(prediction.confidence ?? prediction.confidence_score ?? 0),
    alternativePossibilities: prediction.alternative_possibilities 
      || prediction.top_predictions 
      || [],
    needsReview: prediction.needs_review ?? false,
    reviewReason: prediction.review_reason || null,
  };
};

/**
 * Extract symptom analysis from response
 * @param {Object} response - API response
 * @returns {Object|null} - Symptom analysis or null
 */
const extractSymptomAnalysis = (response) => {
  const analysis = response.symptom_analysis || response.symptomAnalysis;
  
  if (!analysis) return null;
  
  return {
    matchPercentage: analysis.match_percentage ?? analysis.matchPercentage ?? 0,
    alignment: analysis.alignment || 'unknown',
    matchedSymptoms: analysis.matched_symptoms || analysis.matchedSymptoms || [],
    message: analysis.message || null,
  };
};

/**
 * Extract severity data from response
 * @param {Object} response - API response
 * @returns {Object} - Severity assessment
 */
const extractSeverityData = (response) => {
  const severity = response.severity || {};
  
  return {
    level: severity.level || response.severity_level || 'unknown',
    urgency: severity.urgency || response.urgency || 'routine',
    explanation: severity.explanation || null,
  };
};

/**
 * Extract recommendations from response
 * @param {Object} response - API response
 * @returns {Object} - Recommendations
 */
const extractRecommendations = (response) => {
  const recs = response.recommendations || {};
  
  // Handle array format (simple list)
  if (Array.isArray(recs)) {
    return {
      generalAdvice: null,
      immediateCare: recs,
      homeRemedies: [],
      precautions: [],
      lifestyleTips: [],
      whenToSeeDoctor: null,
    };
  }
  
  // Handle object format (structured)
  return {
    generalAdvice: recs.general_advice || recs.generalAdvice || null,
    immediateCare: recs.immediate_care || recs.immediateCare || [],
    homeRemedies: recs.home_remedies || recs.homeRemedies || [],
    precautions: recs.precautions || [],
    lifestyleTips: recs.lifestyle_tips || recs.lifestyleTips || [],
    whenToSeeDoctor: recs.when_to_see_doctor || recs.whenToSeeDoctor || null,
  };
};

/**
 * Get confidence level string from score
 * @param {number} score - Confidence score (0-100 or 0-1)
 * @returns {string} - "high", "medium", or "low"
 */
const getConfidenceLevel = (score) => {
  // Normalize to 0-100 if needed
  const normalizedScore = score <= 1 ? score * 100 : score;
  
  if (normalizedScore >= 80) return 'high';
  if (normalizedScore >= 60) return 'medium';
  return 'low';
};

/**
 * Get default medical disclaimer
 * @returns {string} - Disclaimer text
 */
const getDefaultDisclaimer = () => {
  return 'This analysis is for informational purposes only and does not constitute a medical diagnosis. ' +
    'Please consult a qualified healthcare professional for accurate diagnosis and treatment. ' +
    'Do not delay seeking medical advice based on this analysis.';
};

// ============================================
// Feature 11.2 - Prediction API Call
// ============================================

/**
 * Predicts disease based on image and symptoms
 * 
 * Function: predictDisease(imageFile, symptoms)
 * 
 * Steps:
 * 1. Create FormData object
 * 2. Append image file
 * 3. Append symptoms (comma-separated string)
 * 4. Set Content-Type to multipart/form-data
 * 5. POST to /api/predict
 * 6. Handle response
 * 7. Handle errors
 * 
 * Error Handling:
 * - Network errors (no internet)
 * - Server errors (500)
 * - Validation errors (400)
 * - Timeout errors
 * - Parse response properly
 * 
 * @param {File} imageFile - The image file to analyze
 * @param {string[]} symptoms - List of selected symptoms
 * @param {function} onProgress - Callback for upload progress: (percent: number) => void
 * @returns {Promise<Object>} - The analysis result
 * @throws {Error} - Formatted error message for display
 */
export const predictDisease = async (imageFile, symptoms = [], onProgress = null) => {
  // Validate input
  if (!imageFile) {
    throw new Error('No image file provided.');
  }
  
  if (!(imageFile instanceof File)) {
    throw new Error('Invalid image file.');
  }

  try {
    // Step 1: Create FormData object
    const formData = new FormData();
    
    // Step 2: Append image file
    formData.append('image', imageFile);
    
    // Step 3: Append symptoms (comma-separated string)
    if (symptoms && Array.isArray(symptoms) && symptoms.length > 0) {
      formData.append('symptoms', symptoms.join(','));
    }

    // Step 4 & 5: POST to /api/predict with multipart/form-data
    const response = await apiClient.post('/predict', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      // Track upload progress
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });

    // Step 6: Handle response - Process using Feature 11.3
    const data = response.data;
    
    // Validate response has expected structure
    if (!data) {
      throw new Error('Empty response from server.');
    }
    
    // Check for error in response body
    if (data.error) {
      throw new Error(data.error);
    }
    
    // Process and format the response (Feature 11.3)
    return processPredictionResponse(data);
    
  } catch (error) {
    // Step 7: Handle errors
    
    // If it's already a formatted error, re-throw
    if (error.message && !error.response && !error.request) {
      throw error;
    }
    
    // Network errors (no internet)
    if (error.request && !error.response) {
      throw new Error('Cannot connect to server. Please check your internet connection.');
    }
    
    // Timeout errors
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. The analysis is taking longer than expected. Please try again.');
    }
    
    // Server errors (500)
    if (error.response && error.response.status >= 500) {
      throw new Error('Server error occurred. Please try again later.');
    }
    
    // Validation errors (400)
    if (error.response && error.response.status === 400) {
      const errorMsg = error.response.data?.error || error.response.data?.message;
      throw new Error(errorMsg || 'Invalid request. Please check your image and try again.');
    }
    
    // Other errors - use formatError for consistent messaging
    throw new Error(formatError(error));
  }
};

// ============================================
// Feature 11.4 - Helper Functions & API Endpoints
// ============================================

/**
 * Feature 11.4 Helper Functions:
 * - formatError(error) → user-friendly message ✓ (defined above)
 * - uploadWithProgress(file, onProgress) → track upload % ✓
 * - validateResponse(response) → check structure ✓ (defined above)
 * - retryRequest(request, maxRetries) → retry on failure ✓ (defined above)
 */

/**
 * Checks the health status of the backend
 * @returns {Promise<Object>} - Health status { status, model_loaded, num_classes }
 */
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    throw new Error(formatError(error));
  }
};

/**
 * Get list of supported diseases
 * @returns {Promise<Object>} - { diseases: string[], count: number }
 */
export const getSupportedDiseases = async () => {
  try {
    const response = await apiClient.get('/diseases');
    return response.data;
  } catch (error) {
    throw new Error(formatError(error));
  }
};

/**
 * Get list of available symptoms
 * @returns {Promise<Object>} - { symptoms: string[], count: number }
 */
export const getAvailableSymptoms = async () => {
  try {
    const response = await apiClient.get('/symptoms');
    return response.data;
  } catch (error) {
    throw new Error(formatError(error));
  }
};

/**
 * Upload image with progress tracking (Feature 11.4)
 * Tracks upload percentage and calls onProgress callback
 * 
 * @param {File} file - File to upload
 * @param {function} onProgress - Progress callback: (percent: number) => void
 * @returns {Promise<Object>} - Upload/prediction result
 * 
 * @example
 * const result = await uploadWithProgress(file, (percent) => {
 *   console.log(`Upload: ${percent}%`);
 * });
 */
export const uploadWithProgress = async (file, onProgress) => {
  return predictDisease(file, [], onProgress);
};

/**
 * Predict with automatic retry on failure
 * Uses retryRequest helper for exponential backoff
 * 
 * @param {File} imageFile - Image to analyze
 * @param {string[]} symptoms - Symptoms list
 * @param {function} onProgress - Progress callback
 * @param {number} maxRetries - Max retry attempts (default: 2)
 * @returns {Promise<Object>} - Prediction result
 */
export const predictWithRetry = async (imageFile, symptoms = [], onProgress = null, maxRetries = CONFIG.maxRetries) => {
  return retryRequest(
    () => predictDisease(imageFile, symptoms, onProgress),
    maxRetries
  );
};

// ============================================
// API Service Interface (Feature 11.4)
// ============================================

/**
 * Exported API service object
 * 
 * API Service Interface:
 * - predictDisease: (file, symptoms) => Promise<PredictionResult>
 * - getSupportedDiseases: () => Promise<string[]>
 * - getAvailableSymptoms: () => Promise<string[]>
 * - checkHealth: () => Promise<boolean>
 * 
 * Additional:
 * - uploadWithProgress: (file, onProgress) => Promise<Object>
 * - predictWithRetry: (file, symptoms, onProgress, maxRetries) => Promise<Object>
 * 
 * Utilities:
 * - utils.formatError: (error) => string
 * - utils.retryRequest: (requestFn, maxRetries) => Promise
 * - utils.validateResponse: (response, requiredFields) => boolean
 * - utils.processPredictionResponse: (rawResponse) => Object
 * - utils.getConfidenceLevel: (score) => string
 * - utils.getDefaultDisclaimer: () => string
 */
const api = {
  // Main API methods
  predictDisease,
  predictWithRetry,
  checkHealth,
  getSupportedDiseases,
  getAvailableSymptoms,
  uploadWithProgress,
  
  // Expose utilities for advanced usage
  utils: {
    formatError,
    retryRequest,
    validateResponse,
    processPredictionResponse,
    getConfidenceLevel,
    getDefaultDisclaimer,
  },
  
  // Expose config for reference
  config: CONFIG,
};

export default api;
