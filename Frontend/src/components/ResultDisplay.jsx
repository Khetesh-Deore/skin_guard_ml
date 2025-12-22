import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './ResultDisplay.css';

/**
 * Feature 12: Results Display Component
 * 
 * Responsibilities (Feature 12.1):
 * - Display prediction results clearly
 * - Show confidence visualization
 * - Display symptom analysis
 * - Show severity with color coding
 * - Display recommendations organized by section
 * - Include disclaimer prominently
 * - Provide "New Analysis" button
 */
/**
 * Props Interface (Feature 12.5):
 * {
 *   prediction: PredictionResult,
 *   onNewAnalysis: () => void,
 *   loading: boolean
 * }
 */
const ResultDisplay = ({ result, onReset, onNewAnalysis, loading = false }) => {
  // Feature 12.5: Detect mobile for collapsible sections default state
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;
  
  const [expandedSections, setExpandedSections] = useState({
    recommendations: !isMobile, // Collapsed by default on mobile
    alternatives: false,
    disclaimer: false,
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Feature 12.5: Handle responsive behavior on resize
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 768;
      // Only auto-collapse on initial mobile detection, not on every resize
      if (mobile && window.innerWidth !== window._lastWidth) {
        // Keep user's manual changes, just update for significant viewport changes
      }
      window._lastWidth = window.innerWidth;
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Handle the onNewAnalysis prop (alias for onReset for API consistency)
  const handleNewAnalysis = onNewAnalysis || onReset;

  if (!result) return null;

  // Extract data from the processed API response (Feature 11.3 format)
  const {
    prediction = {},
    symptomAnalysis = null,
    severity = {},
    recommendations = {},
    disclaimer = '',
  } = result;

  // Also support legacy format
  const disease = prediction.disease || result.condition_name || 'Unknown Condition';
  const confidence = prediction.confidence ?? result.confidence ?? 0;
  const confidenceLevel = prediction.confidenceLevel || getConfidenceLevel(confidence);
  const alternatives = prediction.alternativePossibilities || [];
  const needsReview = prediction.needsReview || false;
  const reviewReason = prediction.reviewReason || null;
  
  const severityLevel = severity.level || result.severity || 'unknown';
  const urgency = severity.urgency || 'routine';
  const severityExplanation = severity.explanation || null;

  // Helper functions
  function getConfidenceLevel(score) {
    const normalized = score <= 1 ? score * 100 : score;
    if (normalized >= 80) return 'high';
    if (normalized >= 60) return 'medium';
    return 'low';
  }

  /**
   * Feature 12.3 - Confidence Visualization
   * Get icon indicator based on confidence level
   */
  function getConfidenceIcon(level) {
    switch (level) {
      case 'high':
        return '✓';  // Checkmark for high confidence
      case 'medium':
        return '~';  // Tilde for medium confidence
      case 'low':
        return '?';  // Question mark for low confidence
      default:
        return '•';
    }
  }

  /**
   * Feature 12.3 - Get confidence description text
   */
  function getConfidenceDescription(level) {
    switch (level) {
      case 'high':
        return 'High confidence - Results are likely accurate';
      case 'medium':
        return 'Medium confidence - Consider additional evaluation';
      case 'low':
        return 'Low confidence - Professional consultation recommended';
      default:
        return '';
    }
  }

  function getSeverityColorClass(level) {
    switch (level?.toLowerCase()) {
      case 'mild':
      case 'low':
        return 'success mild';
      case 'moderate':
      case 'medium':
        return 'warning moderate';
      case 'severe':
      case 'high':
        return 'danger severe';
      case 'critical':
        return 'critical';
      default:
        return 'info unknown';
    }
  }

  /**
   * Feature 12.4 - Get severity icon based on level
   */
  function getSeverityIcon(level) {
    switch (level?.toLowerCase()) {
      case 'mild':
      case 'low':
        return '✓';  // Checkmark for mild
      case 'moderate':
      case 'medium':
        return '⚡';  // Lightning for moderate
      case 'severe':
      case 'high':
        return '⚠️';  // Warning for severe
      case 'critical':
        return '🚨';  // Alert for critical
      default:
        return 'ℹ️';  // Info for unknown
    }
  }

  /**
   * Feature 12.4 - Get urgency icon based on level
   */
  function getUrgencyIcon(urgencyLevel) {
    switch (urgencyLevel?.toLowerCase()) {
      case 'routine':
        return '📋';  // Clipboard for routine
      case 'consult_doctor':
      case 'consult':
        return '👨‍⚕️';  // Doctor for consult
      case 'soon':
      case 'seek_attention':
        return '⏰';  // Clock for soon
      case 'urgent':
      case 'immediate':
        return '🚑';  // Ambulance for urgent
      default:
        return '';
    }
  }

  function getUrgencyText(urgencyLevel) {
    switch (urgencyLevel?.toLowerCase()) {
      case 'routine':
        return 'Routine care';
      case 'consult_doctor':
      case 'consult':
        return 'Consult a doctor';
      case 'soon':
      case 'seek_attention':
        return 'Seek attention soon';
      case 'urgent':
      case 'immediate':
        return 'Immediate attention needed';
      default:
        return null;
    }
  }

  function formatConfidence(score) {
    const normalized = score <= 1 ? score * 100 : score;
    return Math.round(normalized);
  }

  // Check if we have structured recommendations
  const hasStructuredRecs = recommendations && typeof recommendations === 'object' && !Array.isArray(recommendations);
  const simpleRecs = Array.isArray(recommendations) ? recommendations : 
    (Array.isArray(result.recommendations) ? result.recommendations : []);

  return (
    <div className="result-display-container">
      {/* ============================================
          Section 1: Prediction Summary Card
          ├── Disease name (large, bold)
          ├── Confidence bar/percentage
          ├── Confidence level badge (High/Medium/Low)
          └── Alternative possibilities (collapsible)
          ============================================ */}
      
      {/* Header with confidence badge */}
      <div className="result-header">
        <h2>Analysis Result</h2>
        {/* Feature 12.3: Confidence badge with icon indicator */}
        <div className={`confidence-badge ${confidenceLevel}`}>
          <span className="confidence-icon">{getConfidenceIcon(confidenceLevel)}</span>
          {formatConfidence(confidence)}% Confidence
        </div>
      </div>

      {/* Needs Review Warning */}
      {needsReview && (
        <div className="review-warning">
          <span className="warning-icon">⚠️</span>
          <div className="warning-content">
            <strong>Expert Review Recommended</strong>
            {reviewReason && <p>{reviewReason}</p>}
          </div>
        </div>
      )}

      {/* Main Prediction Card - Disease name (large, bold) */}
      <div className="main-prediction">
        <h3>{disease}</h3>
        {result.description && (
          <p className="description">{result.description}</p>
        )}
        
        {/* Feature 12.3: Confidence Bar Visualization
            Visual Options:
            1. Progress bar (0-100%)
            2. Color coding: Green (>80%), Yellow (60-80%), Orange (<60%)
            3. Icon indicators
            4. Percentage text
        */}
        <div className="confidence-visualization">
          {/* Circular confidence indicator */}
          <div className={`confidence-circle ${confidenceLevel}`}>
            <span className="confidence-value">{formatConfidence(confidence)}%</span>
            <span className="confidence-icon-large">{getConfidenceIcon(confidenceLevel)}</span>
          </div>
          
          {/* Progress bar */}
          <div className="confidence-bar-wrapper">
            <div className="confidence-bar">
              <div 
                className={`confidence-fill ${confidenceLevel}`}
                style={{ width: `${formatConfidence(confidence)}%` }}
              >
                <span className="confidence-fill-text">
                  {formatConfidence(confidence) > 20 ? `${formatConfidence(confidence)}%` : ''}
                </span>
              </div>
            </div>
            <div className="confidence-scale">
              <span>0%</span>
              <span className="scale-marker low-marker">60%</span>
              <span className="scale-marker high-marker">80%</span>
              <span>100%</span>
            </div>
          </div>
          
          {/* Confidence description */}
          <p className={`confidence-description ${confidenceLevel}`}>
            {getConfidenceDescription(confidenceLevel)}
          </p>
        </div>
      </div>

      {/* Alternative Possibilities (collapsible) */}
      {alternatives.length > 0 && (
        <div className="accordion-section alternatives-section">
          <div 
            className={`accordion-header ${expandedSections.alternatives ? 'active' : ''}`}
            onClick={() => toggleSection('alternatives')}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && toggleSection('alternatives')}
          >
            <h4>Alternative Possibilities</h4>
            <span className="toggle-icon">{expandedSections.alternatives ? '−' : '+'}</span>
          </div>
          {expandedSections.alternatives && (
            <div className="accordion-content">
              <ul className="alternatives-list">
                {alternatives.map((alt, index) => (
                  <li key={index} className="alternative-item">
                    <span className="alt-disease">{alt.disease || alt.condition}</span>
                    <span className="alt-confidence">
                      {formatConfidence(alt.confidence)}%
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* ============================================
          Section 2: Symptom Alignment (if symptoms provided)
          ├── Match percentage
          ├── Matched symptoms list
          └── Alignment message
          ============================================ */}
      {symptomAnalysis && (
        <div className="symptom-analysis-section">
          <h4>Symptom Analysis</h4>
          <div className="symptom-match">
            {/* Match percentage */}
            <div className="match-percentage">
              <span className="percentage">{symptomAnalysis.matchPercentage}%</span>
              <span className="label">Match</span>
            </div>
            <div className="match-details">
              {/* Alignment message */}
              <p className={`alignment-badge ${symptomAnalysis.alignment}`}>
                {symptomAnalysis.alignment === 'strong' ? 'Strong alignment' :
                 symptomAnalysis.alignment === 'moderate' ? 'Moderate alignment' :
                 'Weak alignment'}
              </p>
              {symptomAnalysis.message && (
                <p className="match-message">{symptomAnalysis.message}</p>
              )}
            </div>
          </div>
          {/* Matched symptoms list */}
          {symptomAnalysis.matchedSymptoms?.length > 0 && (
            <div className="matched-symptoms">
              <span className="label">Matched symptoms:</span>
              <div className="symptom-tags">
                {symptomAnalysis.matchedSymptoms.map((symptom, i) => (
                  <span key={i} className="symptom-tag">{symptom.replace(/_/g, ' ')}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ============================================
          Section 3: Severity Assessment (Feature 12.4)
          ├── Severity level (color-coded badge)
          ├── Urgency indicator
          └── Severity explanation
          
          Visual System:
          - Mild: Blue/Green
          - Moderate: Yellow/Orange
          - Severe: Red
          - Critical: Dark Red with warning icon
          ============================================ */}
      <div className="severity-section">
        <div className="severity-main">
          <span className="label">Severity Assessment:</span>
          {/* Severity level (color-coded badge with icon) */}
          <span className={`severity-badge ${getSeverityColorClass(severityLevel)}`}>
            <span className="severity-icon">{getSeverityIcon(severityLevel)}</span>
            {severityLevel || 'Unknown'}
          </span>
        </div>
        {/* Urgency indicator with icon */}
        {getUrgencyText(urgency) && (
          <div className={`urgency-badge ${urgency}`}>
            <span className="urgency-icon">{getUrgencyIcon(urgency)}</span>
            {getUrgencyText(urgency)}
          </div>
        )}
        {/* Severity explanation */}
        {severityExplanation && (
          <p className="severity-explanation">{severityExplanation}</p>
        )}
      </div>

      {/* ============================================
          Section 4: Recommendations (Expandable Sections)
          ├── General Advice
          ├── Immediate Care Steps
          ├── Home Remedies
          ├── Precautions
          ├── Lifestyle Tips
          └── When to See a Doctor (highlighted)
          ============================================ */}
      <div className="accordion-section recommendations-section">
        <div 
          className={`accordion-header ${expandedSections.recommendations ? 'active' : ''}`}
          onClick={() => toggleSection('recommendations')}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && toggleSection('recommendations')}
        >
          <h4>Recommendations</h4>
          <span className="toggle-icon">{expandedSections.recommendations ? '−' : '+'}</span>
        </div>
        {expandedSections.recommendations && (
          <div className="accordion-content recommendations-content">
            {hasStructuredRecs ? (
              <>
                {/* General Advice */}
                {recommendations.generalAdvice && (
                  <div className="rec-group">
                    <h5>💡 General Advice</h5>
                    <p className="general-advice">{recommendations.generalAdvice}</p>
                  </div>
                )}
                
                {/* Immediate Care Steps */}
                {recommendations.immediateCare?.length > 0 && (
                  <div className="rec-group">
                    <h5>🩹 Immediate Care Steps</h5>
                    <ul className="recommendations-list">
                      {recommendations.immediateCare.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Home Remedies */}
                {recommendations.homeRemedies?.length > 0 && (
                  <div className="rec-group">
                    <h5>🏠 Home Remedies</h5>
                    <ul className="recommendations-list">
                      {recommendations.homeRemedies.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Precautions */}
                {recommendations.precautions?.length > 0 && (
                  <div className="rec-group">
                    <h5>⚠️ Precautions</h5>
                    <ul className="recommendations-list">
                      {recommendations.precautions.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Lifestyle Tips */}
                {recommendations.lifestyleTips?.length > 0 && (
                  <div className="rec-group">
                    <h5>🌿 Lifestyle Tips</h5>
                    <ul className="recommendations-list">
                      {recommendations.lifestyleTips.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* When to See a Doctor (highlighted) */}
                {recommendations.whenToSeeDoctor && (
                  <div className="rec-group when-to-see-doctor">
                    <h5>⚕️ When to See a Doctor</h5>
                    <p>{recommendations.whenToSeeDoctor}</p>
                  </div>
                )}
              </>
            ) : (
              <ul className="recommendations-list">
                {simpleRecs.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      {/* ============================================
          Section 5: Disclaimer
          └── Medical disclaimer text (always visible)
          ============================================ */}
      <div className="disclaimer-section">
        <div className="disclaimer-icon">ℹ️</div>
        <p className="disclaimer-text">
          {disclaimer || "This analysis is for informational purposes only and does not constitute a medical diagnosis. Please consult a qualified healthcare professional for accurate diagnosis and treatment."}
        </p>
      </div>

      {/* ============================================
          Actions
          └── "Analyze Another Image" button
          ============================================ */}
      <div className="action-buttons">
        <button 
          className="reset-btn" 
          onClick={handleNewAnalysis}
          disabled={loading}
          aria-label="Start a new skin analysis"
        >
          {loading ? 'Loading...' : 'Analyze Another Image'}
        </button>
      </div>
    </div>
  );
};

ResultDisplay.propTypes = {
  /** Feature 12.5 Props Interface */
  result: PropTypes.shape({
    prediction: PropTypes.object,
    symptomAnalysis: PropTypes.object,
    severity: PropTypes.object,
    recommendations: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
    disclaimer: PropTypes.string,
    // Legacy format support
    condition_name: PropTypes.string,
    confidence: PropTypes.number,
    description: PropTypes.string,
  }),
  onReset: PropTypes.func,
  onNewAnalysis: PropTypes.func, // Alias for onReset
  loading: PropTypes.bool,
};

ResultDisplay.defaultProps = {
  loading: false,
  onReset: () => {},
  onNewAnalysis: null,
};

export default ResultDisplay;
