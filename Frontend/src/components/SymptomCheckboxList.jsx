import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './SymptomCheckboxList.css';

/**
 * SymptomCheckboxList Component (Feature 10.2 - Option 1)
 * 
 * Alternative input method using checkboxes:
 * - Display common symptoms as checkboxes
 * - User can check multiple
 * - Group symptoms by category (skin appearance, sensation, etc.)
 */

/**
 * Symptom categories organized by type
 */
const SYMPTOM_CATEGORIES = {
  "Skin Appearance": [
    "redness",
    "patches",
    "spots",
    "bumps",
    "scaling",
    "discoloration",
    "lesion",
    "mole_change",
    "irregular_border",
    "color_variation"
  ],
  "Sensations": [
    "itching",
    "burning",
    "pain",
    "tenderness",
    "numbness",
    "tingling"
  ],
  "Texture Changes": [
    "dry_skin",
    "rough_skin",
    "scaly_skin",
    "thickened_skin",
    "crusty_patches"
  ],
  "Wound & Bleeding": [
    "bleeding",
    "oozing",
    "crusting",
    "sore_that_wont_heal",
    "ulceration"
  ],
  "Size & Growth": [
    "rapid_growth",
    "increasing_size",
    "large_area",
    "spreading"
  ]
};

const SymptomCheckboxList = ({ 
  onSymptomsChange, 
  maxSymptoms = 10,
  initialSymptoms = [],
  collapsible = true 
}) => {
  const [selectedSymptoms, setSelectedSymptoms] = useState(initialSymptoms);
  const [expandedCategories, setExpandedCategories] = useState(
    collapsible ? {} : Object.keys(SYMPTOM_CATEGORIES).reduce((acc, cat) => ({ ...acc, [cat]: true }), {})
  );
  const [error, setError] = useState(null);

  // Notify parent of changes
  useEffect(() => {
    onSymptomsChange(selectedSymptoms);
  }, [selectedSymptoms, onSymptomsChange]);

  // Handle checkbox change
  const handleCheckboxChange = (symptom, isChecked) => {
    setError(null);
    
    if (isChecked) {
      // Adding symptom
      if (selectedSymptoms.length >= maxSymptoms) {
        setError(`Maximum ${maxSymptoms} symptoms allowed.`);
        return;
      }
      setSelectedSymptoms(prev => [...prev, symptom]);
    } else {
      // Removing symptom
      setSelectedSymptoms(prev => prev.filter(s => s !== symptom));
    }
  };

  // Toggle category expansion
  const toggleCategory = (category) => {
    if (!collapsible) return;
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  // Clear all selections
  const handleClearAll = () => {
    setSelectedSymptoms([]);
    setError(null);
  };

  // Expand all categories
  const handleExpandAll = () => {
    const allExpanded = Object.keys(SYMPTOM_CATEGORIES).reduce(
      (acc, cat) => ({ ...acc, [cat]: true }), {}
    );
    setExpandedCategories(allExpanded);
  };

  // Collapse all categories
  const handleCollapseAll = () => {
    setExpandedCategories({});
  };

  // Format symptom for display
  const formatSymptom = (symptom) => {
    return symptom.replace(/_/g, ' ');
  };

  // Check if all categories are expanded
  const allExpanded = Object.keys(SYMPTOM_CATEGORIES).every(
    cat => expandedCategories[cat]
  );

  return (
    <div className="symptom-checkbox-container">
      <div className="checkbox-header">
        <h3>Select Your Symptoms</h3>
        <p className="subtitle">
          Check all symptoms that apply (max {maxSymptoms})
        </p>
      </div>

      {/* Controls */}
      <div className="checkbox-controls">
        <span className="selected-count">
          {selectedSymptoms.length} of {maxSymptoms} selected
        </span>
        
        <div className="control-buttons">
          {collapsible && (
            <button 
              type="button"
              onClick={allExpanded ? handleCollapseAll : handleExpandAll}
              className="expand-btn"
            >
              {allExpanded ? 'Collapse All' : 'Expand All'}
            </button>
          )}
          
          {selectedSymptoms.length > 0 && (
            <button 
              type="button"
              onClick={handleClearAll}
              className="clear-btn"
            >
              Clear All
            </button>
          )}
        </div>
      </div>

      {error && <div className="error-message" role="alert">{error}</div>}

      {/* Category groups with checkboxes */}
      <div className="categories-container">
        {Object.entries(SYMPTOM_CATEGORIES).map(([category, symptoms]) => (
          <div key={category} className="category-section">
            <button
              type="button"
              className={`category-toggle ${expandedCategories[category] ? 'expanded' : ''}`}
              onClick={() => toggleCategory(category)}
              aria-expanded={expandedCategories[category]}
            >
              <span className="category-name">{category}</span>
              <span className="category-count">
                ({symptoms.filter(s => selectedSymptoms.includes(s)).length}/{symptoms.length})
              </span>
              {collapsible && (
                <span className="toggle-icon">
                  {expandedCategories[category] ? '▼' : '▶'}
                </span>
              )}
            </button>

            {(expandedCategories[category] || !collapsible) && (
              <div className="symptoms-grid">
                {symptoms.map(symptom => {
                  const isChecked = selectedSymptoms.includes(symptom);
                  const isDisabled = !isChecked && selectedSymptoms.length >= maxSymptoms;
                  
                  return (
                    <label 
                      key={symptom} 
                      className={`symptom-checkbox ${isChecked ? 'checked' : ''} ${isDisabled ? 'disabled' : ''}`}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        disabled={isDisabled}
                        onChange={(e) => handleCheckboxChange(symptom, e.target.checked)}
                      />
                      <span className="checkbox-custom"></span>
                      <span className="symptom-label">{formatSymptom(symptom)}</span>
                    </label>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Selected symptoms summary */}
      {selectedSymptoms.length > 0 && (
        <div className="selected-summary">
          <h4>Selected Symptoms:</h4>
          <div className="selected-tags">
            {selectedSymptoms.map(symptom => (
              <span key={symptom} className="selected-tag">
                {formatSymptom(symptom)}
                <button
                  type="button"
                  onClick={() => handleCheckboxChange(symptom, false)}
                  className="remove-tag"
                  aria-label={`Remove ${formatSymptom(symptom)}`}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

SymptomCheckboxList.propTypes = {
  onSymptomsChange: PropTypes.func.isRequired,
  maxSymptoms: PropTypes.number,
  initialSymptoms: PropTypes.arrayOf(PropTypes.string),
  collapsible: PropTypes.bool
};

SymptomCheckboxList.defaultProps = {
  maxSymptoms: 10,
  initialSymptoms: [],
  collapsible: true
};

export default SymptomCheckboxList;
