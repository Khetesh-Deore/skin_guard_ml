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
  
  // Disease description from API or fallback
  const diseaseDescription = prediction.description || getDiseaseDescription(disease);
  const diseaseCauses = prediction.causes || null;
  const diseaseCommonIn = prediction.common_in || prediction.commonIn || null;
  
  const severityLevel = severity.level || result.severity || 'unknown';
  const urgency = severity.urgency || 'routine';
  const severityExplanation = severity.explanation || null;

  /**
   * Fallback disease descriptions for when API doesn't provide them
   */
  function getDiseaseDescription(diseaseName) {
    const descriptions = {
      "Acne": "Acne is one of the most common skin conditions worldwide, affecting millions of people annually. It develops when hair follicles become clogged with oil (sebum) and dead skin cells, creating an environment where bacteria can thrive. This leads to various types of blemishes including whiteheads, blackheads, papules, pustules, nodules, and cysts. Acne most commonly appears on the face, forehead, chest, upper back, and shoulders where oil glands are most active.",
      "Actinic Keratosis": "Actinic keratosis (AK), also known as solar keratosis, is a precancerous skin condition resulting from cumulative sun damage over many years. These rough, scaly patches typically develop on sun-exposed areas such as the face, ears, scalp, neck, hands, and forearms. The lesions may be flat or slightly raised, ranging in color from skin-toned to reddish-brown. Actinic keratosis is medically significant because approximately 5-10% of untreated lesions can progress to squamous cell carcinoma.",
      "Benign Tumors": "Benign skin tumors are non-cancerous growths that arise from various cell types within the skin. Unlike malignant tumors, they do not invade surrounding tissues or spread to other parts of the body. Common types include lipomas (fatty tissue growths), dermatofibromas (fibrous tissue nodules), sebaceous cysts (oil gland blockages), and neurofibromas (nerve tissue growths). These tumors typically grow slowly and may remain stable for years.",
      "Bullous": "Bullous diseases encompass a group of skin disorders characterized by the formation of bullae—large, fluid-filled blisters greater than 5mm in diameter. These conditions can be autoimmune (like bullous pemphigoid and pemphigus vulgaris), inherited (epidermolysis bullosa), or acquired through infections, medications, or physical trauma. In autoimmune bullous diseases, the body's immune system mistakenly attacks proteins that hold skin layers together.",
      "Candidiasis": "Cutaneous candidiasis is a fungal infection caused by Candida species, most commonly Candida albicans. This yeast naturally exists on human skin and mucous membranes but can overgrow under certain conditions, leading to infection. Skin candidiasis typically develops in warm, moist areas such as skin folds, between fingers and toes, and around nails. The infection presents as bright red, itchy rashes with satellite pustules at the edges.",
      "Drug Eruption": "Drug eruptions are adverse skin reactions triggered by medications, representing one of the most common types of adverse drug reactions. These reactions can manifest in numerous ways, from mild maculopapular rashes to severe, life-threatening conditions like Stevens-Johnson syndrome. Symptoms typically appear within days to weeks of starting a new medication. Common culprits include antibiotics, NSAIDs, anticonvulsants, and allopurinol.",
      "Eczema": "Eczema, medically known as atopic dermatitis, is a chronic inflammatory skin condition characterized by intensely itchy, dry, and inflamed skin. It's part of the 'atopic triad' along with asthma and allergic rhinitis, suggesting a genetic predisposition to allergic conditions. Eczema typically appears in patches that may be red, scaly, cracked, or weeping. The condition follows a relapsing-remitting course with flare-ups triggered by various factors.",
      "Infestations/Bites": "Skin infestations and arthropod bites encompass conditions caused by parasites, insects, and arachnids. Scabies, caused by the Sarcoptes scabiei mite, creates intensely itchy burrows in the skin. Pediculosis (lice infestation) affects the scalp, body, or pubic area. Bed bug bites appear as grouped, itchy red welts. These conditions cause significant discomfort through itching, inflammation, and secondary infections from scratching.",
      "Lichen": "Lichen planus is an inflammatory condition affecting the skin, mucous membranes, hair, and nails. On the skin, it presents as distinctive purplish, flat-topped, polygonal papules with fine white lines on the surface called Wickham's striae. These lesions are often intensely itchy and commonly appear on the wrists, ankles, lower back, and genital areas. Oral lichen planus affects the mouth lining, causing white, lacy patterns or painful erosions.",
      "Lupus": "Cutaneous lupus erythematosus refers to skin manifestations of lupus, an autoimmune disease where the immune system attacks healthy tissue. The most recognizable form is the butterfly (malar) rash—a red, flat or raised rash across the cheeks and nose bridge. Discoid lupus causes coin-shaped, scaly plaques that can lead to scarring. Photosensitivity is a hallmark feature, with sun exposure triggering or worsening skin lesions.",
      "Moles": "Moles, medically termed melanocytic nevi, are common benign skin growths composed of clusters of melanocytes (pigment-producing cells). They appear as small, usually brown spots and can be flat or raised, round or oval. Most people develop 10-40 moles by adulthood. While the vast majority are harmless, monitoring moles for changes is important because melanoma can develop within existing moles or appear as new abnormal growths.",
      "Psoriasis": "Psoriasis is a chronic autoimmune condition causing rapid skin cell turnover—cells that normally take a month to mature do so in just days. This accelerated growth leads to thick, silvery-white scales overlying red, inflamed patches called plaques. The most common form, plaque psoriasis, typically affects the scalp, elbows, knees, and lower back. Psoriasis is associated with psoriatic arthritis in about 30% of patients.",
      "Rosacea": "Rosacea is a chronic inflammatory skin condition primarily affecting the central face—cheeks, nose, chin, and forehead. It typically begins with episodes of flushing and blushing that become more persistent over time. The condition progresses through stages: persistent redness with visible blood vessels, inflammatory papules and pustules, and in severe cases, skin thickening particularly on the nose. Triggers vary among individuals.",
      "Seborrheic Keratoses": "Seborrheic keratoses are extremely common benign skin growths that appear as waxy, stuck-on looking lesions. They range in color from light tan to brown or black and have a characteristic warty, scaly surface texture. These growths can appear anywhere on the body except palms and soles. While completely harmless and not contagious, they can be cosmetically bothersome or become irritated by clothing.",
      "Skin Cancer": "Skin cancer is the abnormal, uncontrolled growth of skin cells, most commonly caused by ultraviolet radiation damage. The three main types are basal cell carcinoma (BCC), squamous cell carcinoma (SCC), and melanoma. BCC appears as pearly bumps or flat lesions. SCC presents as firm, red nodules. Melanoma, the most dangerous form, develops from melanocytes and can spread rapidly. Early detection dramatically improves outcomes.",
      "Sun/Sunlight Damage": "Sun damage, or photoaging, encompasses the cumulative effects of ultraviolet radiation on the skin over time. Unlike chronological aging, photoaging is characterized by deep wrinkles, rough and leathery texture, mottled pigmentation, loss of skin elasticity, and visible blood vessels. The damage occurs in the dermis where UV rays break down collagen and elastin fibers. Sun damage also increases the risk of skin cancers.",
      "Tinea": "Tinea, commonly called ringworm, is a superficial fungal infection caused by dermatophytes—fungi that feed on keratin in skin, hair, and nails. Despite its name, no worm is involved; the term comes from the ring-shaped rash it often produces. Different body locations have specific names: tinea corporis (body), tinea pedis (athlete's foot), tinea cruris (jock itch), tinea capitis (scalp). It's highly contagious.",
      "Unknown/Normal": "This classification indicates that the analyzed skin appears within normal parameters or that the AI system could not confidently identify a specific condition from the image provided. Normal skin varies significantly among individuals based on factors like ethnicity, age, sun exposure history, and genetics. If you're experiencing symptoms or have concerns about your skin despite this result, we strongly recommend consulting a dermatologist.",
      "Vascular Tumors": "Vascular tumors are growths arising from blood vessels or lymphatic vessels in the skin. The most common type is infantile hemangioma, a benign tumor appearing in infancy as a bright red, raised lesion that typically grows rapidly in the first year before gradually involuting. Other types include congenital hemangiomas, pyogenic granulomas, and cherry angiomas. While most are benign, some may need intervention.",
      "Vasculitis": "Cutaneous vasculitis refers to inflammation of blood vessels in the skin, which can occur as an isolated condition or as part of systemic vasculitis affecting multiple organs. When blood vessel walls become inflamed, they may narrow, weaken, or develop clots. Skin manifestations include palpable purpura, petechiae, livedo reticularis, ulcers, and nodules. The condition can be triggered by infections, medications, or autoimmune diseases.",
      "Vitiligo": "Vitiligo is a chronic autoimmune condition where the immune system destroys melanocytes, the cells responsible for producing skin pigment. This results in well-defined, milky-white patches of depigmented skin that can appear anywhere on the body. Common sites include the face, hands, feet, arms, and genital areas. While not physically harmful or contagious, vitiligo can significantly impact psychological well-being and quality of life.",
      "Warts": "Warts are benign skin growths caused by human papillomavirus (HPV) infection of the top skin layer. Over 100 HPV types exist, with different types causing warts in different locations. Common warts appear as rough, raised bumps typically on hands. Plantar warts develop on feet soles. Flat warts are small and smooth. The virus enters through tiny breaks in the skin and can spread through direct contact."
    };
    
    return descriptions[diseaseName] || `${diseaseName} is a skin condition that requires professional evaluation for accurate diagnosis and treatment. Please consult a dermatologist for detailed information about this condition and appropriate treatment options.`;
  }

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

      {/* Disease Description Section - Below Analysis, Above Alternatives */}
      <div className="disease-info-section">
        <h4>About {disease}</h4>
        <div className="disease-description-box">
          <p className="disease-description">{diseaseDescription}</p>
          {(diseaseCauses || diseaseCommonIn) && (
            <div className="disease-details">
              {diseaseCauses && (
                <div className="disease-detail-item">
                  <span className="detail-label">🔬 Common Causes:</span>
                  <span className="detail-value">{diseaseCauses}</span>
                </div>
              )}
              {diseaseCommonIn && (
                <div className="disease-detail-item">
                  <span className="detail-label">👥 Commonly Affects:</span>
                  <span className="detail-value">{diseaseCommonIn}</span>
                </div>
              )}
            </div>
          )}
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
              <p className="section-description">{sectionDescriptions.alternatives}</p>
              <ul className="alternatives-list">
                {alternatives.map((alt, index) => (
                  <li key={index} className="alternative-item">
                    <div className="alt-header">
                      <span className="alt-disease">{alt.disease || alt.condition}</span>
                      <span className="alt-confidence">
                        {formatConfidence(alt.confidence)}%
                      </span>
                    </div>
                    <p className="alt-description">
                      {alt.description || getDiseaseDescription(alt.disease || alt.condition)}
                    </p>
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
