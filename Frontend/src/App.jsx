import { useState, useEffect, useCallback } from 'react';
import ImageUpload from './components/ImageUpload';
import SymptomInput from './components/SymptomInput';
import ResultDisplay from './components/ResultDisplay';
import { predictDisease } from './services/api';

/**
 * Feature 13: Main Application Flow
 * Component: App.jsx
 * 
 * Manages the overall application state and user flow through the skin analysis process.
 */
function App() {
  /**
   * Feature 13.1 - Application State Management
   * 
   * State Variables:
   * - currentStep: 'upload' | 'analyzing' | 'results'
   * - selectedImage: File | null
   * - selectedSymptoms: string[]
   * - predictionResults: PredictionResult | null
   * - error: string | null
   * - isLoading: boolean
   */
  
  // Main flow state
  const [currentStep, setCurrentStep] = useState('upload'); // 'upload' | 'analyzing' | 'results'
  
  // User input state
  const [selectedImage, setSelectedImage] = useState(null);       // File | null
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);   // string[]
  
  // Results and processing state
  const [predictionResults, setPredictionResults] = useState(null); // PredictionResult | null
  const [error, setError] = useState(null);                         // string | null
  const [isLoading, setIsLoading] = useState(false);                // boolean
  
  // Additional UX state
  const [uploadProgress, setUploadProgress] = useState(0);          // number (0-100)
  const [analysisStage, setAnalysisStage] = useState('');           // string

  /**
   * Feature 13.4 - Loading States
   * 
   * Loading Messages (rotate during analysis):
   * - "Analyzing your image..."
   * - "Processing skin features..."
   * - "Matching symptoms..."
   * - "Generating recommendations..."
   */
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  
  const loadingMessages = [
    { text: "Diagnosis in progress...", icon: "🔍" },
    { text: "Processing skin features...", icon: "🧬" },
    { text: "Matching symptoms...", icon: "🩺" },
    { text: "Generating recommendations...", icon: "📋" }
  ];

  // Feature 13.4: Rotate loading messages during analysis
  useEffect(() => {
    let interval;
    if (currentStep === 'analyzing' && isLoading) {
      interval = setInterval(() => {
        setLoadingMessageIndex((prev) => (prev + 1) % loadingMessages.length);
      }, 2500); // Rotate every 2.5 seconds
    } else {
      setLoadingMessageIndex(0);
    }
    return () => clearInterval(interval);
  }, [currentStep, isLoading, loadingMessages.length]);

  /**
   * Feature 13.3 - Error Handling & User Feedback
   * 
   * Error Types:
   * - 'network': Network failure
   * - 'server': Server error
   * - 'invalid_image': Invalid image
   * - 'timeout': Request timeout
   * - 'validation': Validation errors
   * - 'critical': Critical errors
   */
  const [errorType, setErrorType] = useState(null);                 // string | null
  const [toast, setToast] = useState(null);                         // { message, type } | null
  const [showErrorModal, setShowErrorModal] = useState(false);      // boolean
  const [criticalError, setCriticalError] = useState(null);         // string | null

  /**
   * Feature 13.3 - Error Message Mapping
   */
  const getErrorDetails = useCallback((err) => {
    const message = err?.message?.toLowerCase() || '';
    
    // Network failure
    if (message.includes('network') || message.includes('fetch') || message.includes('connection') || err?.name === 'TypeError') {
      return {
        type: 'network',
        message: 'Unable to connect. Check your internet.',
        action: 'retry'
      };
    }
    
    // Timeout
    if (message.includes('timeout') || message.includes('timed out') || err?.name === 'AbortError') {
      return {
        type: 'timeout',
        message: 'Analysis took too long. Please try again.',
        action: 'retry'
      };
    }
    
    // Invalid image
    if (message.includes('image') || message.includes('format') || message.includes('invalid file')) {
      return {
        type: 'invalid_image',
        message: 'Image could not be processed. Try another.',
        action: 'upload'
      };
    }
    
    // Server error (5xx)
    if (message.includes('server') || message.includes('500') || message.includes('502') || message.includes('503')) {
      return {
        type: 'server',
        message: 'Server error occurred. Please try again.',
        action: 'retry'
      };
    }
    
    // Default error
    return {
      type: 'unknown',
      message: err?.message || 'An unexpected error occurred. Please try again.',
      action: 'retry'
    };
  }, []);

  /**
   * Feature 13.3 - Toast Notification Handler
   */
  const showToast = useCallback((message, type = 'error') => {
    setToast({ message, type });
    // Auto-dismiss after 5 seconds
    setTimeout(() => setToast(null), 5000);
  }, []);

  /**
   * Feature 13.3 - Show Critical Error Modal
   */
  const showCriticalErrorModal = useCallback((message) => {
    setCriticalError(message);
    setShowErrorModal(true);
  }, []);

  /**
   * Feature 13.3 - Dismiss Error Modal
   */
  const dismissErrorModal = useCallback(() => {
    setShowErrorModal(false);
    setCriticalError(null);
  }, []);

  /**
   * Feature 13.1 - State Management Helper Functions
   */
  
  // Reset all state to initial values
  const resetAppState = useCallback(() => {
    setCurrentStep('upload');
    setSelectedImage(null);
    setSelectedSymptoms([]);
    setPredictionResults(null);
    setError(null);
    setErrorType(null);
    setIsLoading(false);
    setUploadProgress(0);
    setAnalysisStage('');
    setLoadingMessageIndex(0);
    setToast(null);
    setShowErrorModal(false);
    setCriticalError(null);
  }, []);

  // Handle image selection
  const handleImageSelect = useCallback((file) => {
    setSelectedImage(file);
    setError(null); // Clear any previous errors
  }, []);

  // Handle symptom changes
  const handleSymptomsChange = useCallback((symptoms) => {
    setSelectedSymptoms(symptoms);
  }, []);

  // Set error state and return to upload step
  const handleError = useCallback((err) => {
    const errorDetails = getErrorDetails(err);
    
    setError(errorDetails.message);
    setErrorType(errorDetails.type);
    setIsLoading(false);
    setCurrentStep('upload');
    setUploadProgress(0);
    setAnalysisStage('');
    
    // Show appropriate feedback based on error type
    if (errorDetails.type === 'network' || errorDetails.type === 'timeout') {
      // Toast for temporary/network errors
      showToast(errorDetails.message, 'error');
    }
    
    // Critical errors get a modal
    if (errorDetails.type === 'critical') {
      showCriticalErrorModal(errorDetails.message);
    }
  }, [getErrorDetails, showToast, showCriticalErrorModal]);

  /**
   * Feature 13.3 - Retry Analysis
   */
  const handleRetry = useCallback(() => {
    setError(null);
    setErrorType(null);
    setToast(null);
    // Will be called via handleRetryAnalysis after handleAnalyze is defined
  }, []);

  /**
   * Feature 13.2 - User Flow State Machine
   * 
   * State: 'upload'
   * ├── Show ImageUpload component
   * ├── Show SymptomInput component
   * ├── Show "Analyze" button (disabled until image selected)
   * └── On submit → transition to 'analyzing'
   * 
   * State: 'analyzing'
   * ├── Show loading spinner
   * ├── Show progress message
   * ├── Call API
   * ├── On success → transition to 'results'
   * └── On error → show error, back to 'upload'
   * 
   * State: 'results'
   * ├── Show ResultDisplay component
   * ├── Show "New Analysis" button
   * └── On new analysis → clear data, back to 'upload'
   */

  // Check if analysis can be started (used in 'upload' state)
  const canStartAnalysis = useCallback(() => {
    return selectedImage && !isLoading;
  }, [selectedImage, isLoading]);

  /**
   * Feature 13.1 - State Validation and Cleanup Effects
   */
  
  // Validate state consistency
  useEffect(() => {
    // If we're in results step but have no results, go back to upload
    if (currentStep === 'results' && !predictionResults) {
      setCurrentStep('upload');
    }
    
    // If we're analyzing but not loading, something went wrong
    if (currentStep === 'analyzing' && !isLoading) {
      setCurrentStep('upload');
    }
  }, [currentStep, predictionResults, isLoading]);

  // Log state changes in development
  useEffect(() => {
    if (import.meta.env.DEV) {
      console.log('[App State]', {
        currentStep,
        hasImage: !!selectedImage,
        symptomsCount: selectedSymptoms.length,
        hasResults: !!predictionResults,
        isLoading,
        error,
      });
    }
  }, [currentStep, selectedImage, selectedSymptoms, predictionResults, isLoading, error]);

  /**
   * Feature 13.1 - Main Analysis Function
   * Feature 13.3 - Enhanced with error handling
   */
  const handleAnalyze = async () => {
    // Validation
    if (!canStartAnalysis()) {
      setError('Please select an image first.');
      setErrorType('validation');
      return;
    }

    // Start analysis
    setIsLoading(true);
    setError(null);
    setErrorType(null);
    setCurrentStep('analyzing');
    setUploadProgress(0);
    setAnalysisStage('Uploading image...');

    try {
      // Call API with progress tracking
      const result = await predictDisease(
        selectedImage, 
        selectedSymptoms,
        (progress) => {
          setUploadProgress(progress);
          if (progress < 50) {
            setAnalysisStage('Uploading image...');
          } else if (progress < 80) {
            setAnalysisStage('Processing with AI model...');
          } else {
            setAnalysisStage('Generating recommendations...');
          }
        }
      );
      
      // Update progress stages
      setAnalysisStage('Processing complete!');
      setUploadProgress(100);
      
      // Set results and move to results step
      setPredictionResults(result);
      setCurrentStep('results');
      
    } catch (err) {
      // Feature 13.3: Enhanced error handling
      handleError(err);
      
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Feature 13.3 - Retry handler (needs to be after handleAnalyze definition)
   */
  const handleRetryAnalysis = () => {
    setError(null);
    setErrorType(null);
    setToast(null);
    // Re-trigger analysis
    if (selectedImage) {
      handleAnalyze();
    }
  };

  /**
   * Feature 13.1 - Reset Function
   * Resets the application to initial state for new analysis
   */
  const handleReset = () => {
    resetAppState();
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>SkinGuard ML</h1>
        <p>AI-Powered Skin Condition Analysis</p>
        {/* Feature 13.1: Step indicator */}
        <div className="step-indicator">
          <span className={`step ${currentStep === 'upload' ? 'active' : ''}`}>1. Upload</span>
          <span className={`step ${currentStep === 'analyzing' ? 'active' : ''}`}>2. Analyze</span>
          <span className={`step ${currentStep === 'results' ? 'active' : ''}`}>3. Results</span>
        </div>
      </header>

      <main className="app-main">
        {/* ================================================
            Feature 13.2: State 'upload'
            ├── Show ImageUpload component
            ├── Show SymptomInput component
            ├── Show "Analyze" button (disabled until image selected)
            └── On submit → transition to 'analyzing'
            ================================================ */}
        {currentStep === 'upload' && (
          <div className="input-section fade-in">
            <ImageUpload 
              onImageSelect={handleImageSelect}
              disabled={isLoading}
            />
            
            <div className="spacer"></div>
            
            <SymptomInput 
              onSymptomsChange={handleSymptomsChange}
              disabled={isLoading}
            />

            <div className="analyze-action">
              <button 
                className="analyze-btn"
                onClick={handleAnalyze}
                disabled={!canStartAnalysis()}
                aria-label={`Analyze skin condition${selectedImage ? '' : ' (select image first)'}`}
              >
                {isLoading ? 'Starting...' : 'Analyze Condition'}
              </button>
              
              {/* Feature 13.3: Inline error message for validation errors */}
              {error && (
                <div className={`error-message error-${errorType || 'unknown'}`} role="alert">
                  <span className="error-icon">
                    {errorType === 'network' ? '🌐' : 
                     errorType === 'timeout' ? '⏱️' : 
                     errorType === 'invalid_image' ? '🖼️' : 
                     errorType === 'server' ? '🖥️' : '⚠️'}
                  </span>
                  <div className="error-content">
                    <p className="error-text">{error}</p>
                    {/* Feature 13.3: Action buttons based on error type */}
                    <div className="error-actions">
                      {(errorType === 'network' || errorType === 'server' || errorType === 'timeout') && (
                        <button 
                          className="retry-btn"
                          onClick={handleRetryAnalysis}
                          disabled={!selectedImage}
                        >
                          🔄 Retry
                        </button>
                      )}
                      {errorType === 'invalid_image' && (
                        <button 
                          className="upload-btn-small"
                          onClick={() => { setError(null); setErrorType(null); }}
                        >
                          📤 Try Another Image
                        </button>
                      )}
                    </div>
                  </div>
                  <button 
                    className="error-dismiss"
                    onClick={() => { setError(null); setErrorType(null); }}
                    aria-label="Dismiss error"
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ================================================
            Feature 13.2: State 'analyzing'
            ├── Show loading spinner
            ├── Show progress message
            ├── Call API (handled in handleAnalyze)
            ├── On success → transition to 'results'
            └── On error → show error, back to 'upload'
            ================================================ */}
        {currentStep === 'analyzing' && (
          <div className="analyzing-section fade-in">
            {/* Feature 13.4: Enhanced Loading Visual */}
            <div className="loader-container">
              <div className="loader"></div>
              <div className="loader-pulse"></div>
            </div>
            
            {/* Feature 13.4: Rotating Loading Messages */}
            <div className="loading-message">
              <span className="loading-icon">{loadingMessages[loadingMessageIndex].icon}</span>
              <h3 className="loading-text">{loadingMessages[loadingMessageIndex].text}</h3>
            </div>
            
            {/* Progress indicator */}
            <div className="progress-section">
              {uploadProgress > 0 && (
                <div className="progress-container">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <span className="progress-text">{uploadProgress}%</span>
                </div>
              )}
              
              {/* Feature 13.4: Stage dots indicator */}
              <div className="stage-dots">
                {loadingMessages.map((_, index) => (
                  <span 
                    key={index} 
                    className={`stage-dot ${index === loadingMessageIndex ? 'active' : ''} ${index < loadingMessageIndex ? 'completed' : ''}`}
                  />
                ))}
              </div>
            </div>
            
            {/* Feature 13.4: Time notice */}
            <p className="analysis-note">
              <span className="note-icon">⏱️</span>
              This may take 10-15 seconds
            </p>
          </div>
        )}

        {/* ================================================
            Feature 13.2: State 'results'
            ├── Show ResultDisplay component
            ├── Show "New Analysis" button (inside ResultDisplay)
            └── On new analysis → clear data, back to 'upload'
            ================================================ */}
        {currentStep === 'results' && predictionResults && (
          <div className="result-section fade-in">
            <ResultDisplay 
              result={predictionResults} 
              onReset={handleReset}
              onNewAnalysis={handleReset}
              loading={isLoading}
            />
          </div>
        )}
      </main>

      <footer className="app-footer">
  <p>© {new Date().getFullYear()} SkinGuard . For research purposes only.</p>
</footer>


      {/* ================================================
          Feature 13.3: Toast Notification
          For temporary errors (network, timeout)
          ================================================ */}
      {toast && (
        <div className={`toast toast-${toast.type}`} role="alert" aria-live="polite">
          <span className="toast-icon">
            {toast.type === 'error' ? '❌' : toast.type === 'success' ? '✅' : 'ℹ️'}
          </span>
          <span className="toast-message">{toast.message}</span>
          <button 
            className="toast-dismiss"
            onClick={() => setToast(null)}
            aria-label="Dismiss notification"
          >
            ✕
          </button>
        </div>
      )}

      {/* ================================================
          Feature 13.3: Critical Error Modal
          For critical/unrecoverable errors
          ================================================ */}
      {showErrorModal && (
        <div className="modal-overlay" onClick={dismissErrorModal}>
          <div className="error-modal" onClick={(e) => e.stopPropagation()} role="alertdialog" aria-modal="true">
            <div className="modal-header">
              <span className="modal-icon">🚨</span>
              <h3>Critical Error</h3>
            </div>
            <div className="modal-body">
              <p>{criticalError || 'A critical error has occurred. Please refresh the page and try again.'}</p>
            </div>
            <div className="modal-actions">
              <button className="modal-btn secondary" onClick={dismissErrorModal}>
                Dismiss
              </button>
              <button className="modal-btn primary" onClick={() => { dismissErrorModal(); resetAppState(); }}>
                Start Over
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .app-container {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          background-color: #f5f7fa;
          font-family: 'Segoe UI', sans-serif;
        }

        .app-header {
          background: linear-gradient(135deg, #1976d2, #1565c0);
          color: white;
          padding: 20px;
          text-align: center;
          box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }

        .app-header h1 { margin: 0; font-size: 2rem; }
        .app-header p { margin: 5px 0 0; opacity: 0.9; }

        /* Feature 13.1: Step Indicator */
        .step-indicator {
          display: flex;
          justify-content: center;
          gap: 8px;
          margin-top: 16px;
        }

        .step {
          padding: 6px 16px;
          border-radius: 20px;
          font-size: 0.85rem;
          background: rgba(255,255,255,0.2);
          opacity: 0.7;
          transition: all 0.3s ease;
        }

        .step.active {
          background: rgba(255,255,255,0.95);
          color: #1976d2;
          opacity: 1;
          font-weight: 600;
        }

        .app-main {
          flex: 1;
          padding: 40px 20px;
          max-width: 800px;
          margin: 0 auto;
          width: 100%;
          box-sizing: border-box;
        }

        .spacer { height: 30px; }

        .analyze-action {
          margin-top: 40px;
          text-align: center;
        }

        .analyze-btn {
          background: linear-gradient(135deg, #4caf50, #43a047);
          color: white;
          border: none;
          padding: 16px 48px;
          border-radius: 30px;
          font-size: 1.2rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        }

        .analyze-btn:hover:not(:disabled) {
          background: linear-gradient(135deg, #43a047, #388e3c);
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
        }

        .analyze-btn:disabled {
          background: #bdbdbd;
          cursor: not-allowed;
          box-shadow: none;
          transform: none;
        }

        /* Feature 13.3: Enhanced Error Message */
        .error-message {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          margin-top: 16px;
          padding: 16px 20px;
          background: #ffebee;
          border: 1px solid #ffcdd2;
          border-radius: 8px;
          max-width: 450px;
          margin-left: auto;
          margin-right: auto;
          position: relative;
          text-align: left;
        }

        .error-content {
          flex: 1;
        }

        .error-actions {
          display: flex;
          gap: 8px;
          margin-top: 12px;
        }

        .retry-btn, .upload-btn-small {
          padding: 8px 16px;
          border-radius: 6px;
          font-size: 0.85rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          border: none;
        }

        .retry-btn {
          background: #1976d2;
          color: white;
        }

        .retry-btn:hover:not(:disabled) {
          background: #1565c0;
        }

        .retry-btn:disabled {
          background: #bdbdbd;
          cursor: not-allowed;
        }

        .upload-btn-small {
          background: #f5f5f5;
          color: #333;
          border: 1px solid #ddd;
        }

        .upload-btn-small:hover {
          background: #e0e0e0;
        }

        .error-dismiss {
          position: absolute;
          top: 8px;
          right: 8px;
          background: none;
          border: none;
          font-size: 1rem;
          cursor: pointer;
          color: #999;
          padding: 4px;
          line-height: 1;
        }

        .error-dismiss:hover {
          color: #666;
        }

        /* Error type specific styling */
        .error-network { border-left: 4px solid #ff9800; }
        .error-timeout { border-left: 4px solid #ff5722; }
        .error-invalid_image { border-left: 4px solid #9c27b0; }
        .error-server { border-left: 4px solid #f44336; }

        .error-icon { font-size: 1.2rem; flex-shrink: 0; }
        .error-text { margin: 0; color: #c62828; }

        /* Feature 13.3: Toast Notification */
        .toast {
          position: fixed;
          bottom: 24px;
          right: 24px;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 14px 20px;
          border-radius: 8px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.15);
          z-index: 1000;
          animation: slideInRight 0.3s ease-out;
          max-width: 400px;
        }

        .toast-error {
          background: #ffebee;
          border: 1px solid #ffcdd2;
          color: #c62828;
        }

        .toast-success {
          background: #e8f5e9;
          border: 1px solid #c8e6c9;
          color: #2e7d32;
        }

        .toast-info {
          background: #e3f2fd;
          border: 1px solid #bbdefb;
          color: #1565c0;
        }

        .toast-icon { font-size: 1.2rem; }
        .toast-message { flex: 1; font-size: 0.9rem; }

        .toast-dismiss {
          background: none;
          border: none;
          font-size: 1rem;
          cursor: pointer;
          color: inherit;
          opacity: 0.7;
          padding: 4px;
        }

        .toast-dismiss:hover { opacity: 1; }

        @keyframes slideInRight {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }

        /* Feature 13.3: Error Modal */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1001;
          animation: fadeIn 0.2s ease-out;
        }

        .error-modal {
          background: white;
          border-radius: 12px;
          padding: 24px;
          max-width: 420px;
          width: 90%;
          box-shadow: 0 8px 32px rgba(0,0,0,0.2);
          animation: scaleIn 0.2s ease-out;
        }

        @keyframes scaleIn {
          from {
            transform: scale(0.9);
            opacity: 0;
          }
          to {
            transform: scale(1);
            opacity: 1;
          }
        }

        .modal-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
        }

        .modal-icon { font-size: 2rem; }

        .modal-header h3 {
          margin: 0;
          color: #c62828;
          font-size: 1.3rem;
        }

        .modal-body {
          margin-bottom: 24px;
        }

        .modal-body p {
          margin: 0;
          color: #555;
          line-height: 1.6;
        }

        .modal-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
        }

        .modal-btn {
          padding: 10px 20px;
          border-radius: 6px;
          font-size: 0.95rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          border: none;
        }

        .modal-btn.primary {
          background: #1976d2;
          color: white;
        }

        .modal-btn.primary:hover {
          background: #1565c0;
        }

        .modal-btn.secondary {
          background: #f5f5f5;
          color: #333;
          border: 1px solid #ddd;
        }

        .modal-btn.secondary:hover {
          background: #e0e0e0;
        }

        /* ================================================
           Feature 13.4: Enhanced Loading States
           ================================================ */
        
        /* Analyzing Section */
        .analyzing-section {
          text-align: center;
          padding: 60px 40px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }

        /* Loader Container with pulse effect */
        .loader-container {
          position: relative;
          width: 80px;
          height: 80px;
          margin: 0 auto 24px;
        }

        .loader {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          border: 4px solid #e3f2fd;
          border-top: 4px solid #1976d2;
          border-radius: 50%;
          width: 60px;
          height: 60px;
          animation: spin 1s linear infinite;
        }

        .loader-pulse {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 80px;
          height: 80px;
          border-radius: 50%;
          background: rgba(25, 118, 210, 0.1);
          animation: pulse 2s ease-in-out infinite;
        }

        @keyframes spin {
          0% { transform: translate(-50%, -50%) rotate(0deg); }
          100% { transform: translate(-50%, -50%) rotate(360deg); }
        }

        @keyframes pulse {
          0%, 100% { 
            transform: translate(-50%, -50%) scale(1);
            opacity: 0.5;
          }
          50% { 
            transform: translate(-50%, -50%) scale(1.2);
            opacity: 0.2;
          }
        }

        /* Loading Message with icon */
        .loading-message {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          margin-bottom: 24px;
        }

        .loading-icon {
          font-size: 1.8rem;
          animation: bounce 1s ease-in-out infinite;
        }

        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-5px); }
        }

        .loading-text {
          margin: 0;
          color: #333;
          font-size: 1.3rem;
          font-weight: 600;
          animation: fadeInOut 2.5s ease-in-out;
        }

        @keyframes fadeInOut {
          0% { opacity: 0; transform: translateY(10px); }
          20% { opacity: 1; transform: translateY(0); }
          80% { opacity: 1; transform: translateY(0); }
          100% { opacity: 0.8; }
        }

        /* Progress Section */
        .progress-section {
          margin: 24px 0;
        }

        /* Stage dots indicator */
        .stage-dots {
          display: flex;
          justify-content: center;
          gap: 12px;
          margin-top: 16px;
        }

        .stage-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: #e0e0e0;
          transition: all 0.3s ease;
        }

        .stage-dot.active {
          background: #1976d2;
          transform: scale(1.3);
          box-shadow: 0 0 8px rgba(25, 118, 210, 0.5);
        }

        .stage-dot.completed {
          background: #4caf50;
        }

        .analysis-note {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          color: #888;
          font-size: 0.9rem;
          margin-top: 20px;
          padding: 10px 20px;
          background: #f5f5f5;
          border-radius: 20px;
          display: inline-flex;
        }

        .note-icon {
          font-size: 1rem;
        }

        .progress-container {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          margin: 20px auto;
          max-width: 300px;
        }

        .progress-bar {
          flex: 1;
          height: 8px;
          background-color: #e0e0e0;
          border-radius: 4px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #1976d2, #42a5f5, #1976d2);
          background-size: 200% 100%;
          border-radius: 4px;
          transition: width 0.3s ease;
          animation: shimmer 2s linear infinite;
        }

        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }

        .progress-text {
          font-size: 0.9rem;
          font-weight: 600;
          color: #666;
          min-width: 40px;
        }

        .app-footer {
          text-align: center;
          padding: 20px;
          color: #666;
          font-size: 0.9rem;
          border-top: 1px solid #e0e0e0;
          background: white;
        }

        .fade-in {
          animation: fadeIn 0.5s ease-out;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        /* Responsive */
        @media (max-width: 768px) {
          .app-header { padding: 16px; }
          .app-header h1 { font-size: 1.6rem; }
          
          .step-indicator { 
            flex-wrap: wrap;
            gap: 6px;
          }
          
          .step {
            padding: 4px 12px;
            font-size: 0.75rem;
          }

          .app-main { padding: 24px 16px; }
          
          .analyze-btn {
            padding: 14px 36px;
            font-size: 1.1rem;
          }

          .analyzing-section { padding: 40px 20px; }

          /* Feature 13.4: Responsive loading */
          .loader-container {
            width: 70px;
            height: 70px;
          }

          .loader {
            width: 50px;
            height: 50px;
          }

          .loader-pulse {
            width: 70px;
            height: 70px;
          }

          .loading-icon {
            font-size: 1.5rem;
          }

          .loading-text {
            font-size: 1.1rem;
          }

          .stage-dots {
            gap: 10px;
          }

          .stage-dot {
            width: 8px;
            height: 8px;
          }

          /* Feature 13.3: Responsive toast */
          .toast {
            left: 16px;
            right: 16px;
            bottom: 16px;
            max-width: none;
          }

          /* Feature 13.3: Responsive modal */
          .error-modal {
            margin: 16px;
            padding: 20px;
          }

          .modal-actions {
            flex-direction: column;
          }

          .modal-btn {
            width: 100%;
          }
        }

        @media (max-width: 480px) {
          .app-header h1 { font-size: 1.4rem; }
          
          .analyze-btn {
            width: 100%;
            max-width: 280px;
          }

          /* Feature 13.3: Responsive error message */
          .error-message {
            flex-direction: column;
            text-align: center;
            padding: 14px;
          }

          .error-actions {
            justify-content: center;
            flex-wrap: wrap;
          }

          .error-dismiss {
            position: static;
            align-self: flex-end;
            margin-top: -8px;
          }
        }
      `}</style>
    </div>
  );
}

export default App;
