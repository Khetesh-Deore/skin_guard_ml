import { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import './SymptomInput.css';

/**
 * SymptomInput Component (Feature 10)
 * 
 * Responsibilities (Feature 10.1):
 * - Multi-select symptom input
 * - Predefined symptom list organized by category
 * - Custom symptom entry with validation
 * - Selected symptoms display as removable tags
 * - Clear all functionality
 */

/**
 * Feature 10.3 - Symptom List Organization
 * 
 * Categories organized for easy user selection:
 * - Skin Appearance: Visual changes to the skin
 * - Sensations: How the skin feels
 * - Texture: Changes in skin texture
 * - Other: Additional symptoms
 * 
 * Extended with disease-specific symptoms for better matching.
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
    "asymmetric_shape",
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
  "Texture": [
    "dry_skin",
    "oily_skin",
    "rough_skin",
    "thickened_skin",
    "scaly_skin",
    "crusty_patches",
    "pearly_bump",
    "hard_lump"
  ],
  "Other": [
    "oozing",
    "crusting",
    "swelling",
    "bleeding",
    "rapid_growth",
    "spreading",
    "sore_that_wont_heal",
    "ulceration"
  ]
};

const SymptomInput = ({ onSymptomsChange, maxSymptoms = 10, predefinedSymptoms = null }) => {
  /**
   * Feature 10.4 - Component State Variables
   * 
   * @state {string[]} selectedSymptoms - Array of selected symptom strings
   * @state {string} searchTerm - Current search/filter input value
   * @state {boolean} showDropdown - Whether dropdown is visible
   * @state {string|null} error - Error message or null
   * @state {Object} filteredCategories - Filtered symptom categories based on search
   * @state {number} highlightedIndex - Index of keyboard-highlighted option (-1 = none)
   */
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);           // string[]
  const [searchTerm, setSearchTerm] = useState('');                       // string
  const [showDropdown, setShowDropdown] = useState(false);                // boolean
  const [error, setError] = useState(null);                               // string | null
  
  // Use custom predefined symptoms if provided, otherwise use default categories
  const symptomSource = predefinedSymptoms 
    ? { "Symptoms": predefinedSymptoms }
    : SYMPTOM_CATEGORIES;
    
  const [filteredCategories, setFilteredCategories] = useState(symptomSource);  // Object
  const [highlightedIndex, setHighlightedIndex] = useState(-1);           // number

  // Refs for DOM access
  const wrapperRef = useRef(null);    // Container ref for click-outside detection
  const inputRef = useRef(null);      // Input ref for focus management
  const dropdownRef = useRef(null);   // Dropdown ref for scroll management

  // Get flat list of filtered symptoms for keyboard navigation
  const flatFilteredSymptoms = Object.values(filteredCategories).flat();

  useEffect(() => {
    // Notify parent component of changes
    onSymptomsChange(selectedSymptoms);
  }, [selectedSymptoms, onSymptomsChange]);

  useEffect(() => {
    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    // Filter categories based on input (Feature 10.2 - Type to filter)
    if (!searchTerm.trim()) {
      setFilteredCategories(symptomSource);
      setHighlightedIndex(-1);
      return;
    }

    const lowerInput = searchTerm.toLowerCase();
    const filtered = {};
    let hasMatches = false;

    Object.entries(symptomSource).forEach(([category, symptoms]) => {
      const matchingSymptoms = symptoms.filter(s => 
        s.toLowerCase().includes(lowerInput) ||
        s.replace(/_/g, ' ').toLowerCase().includes(lowerInput)
      );
      if (matchingSymptoms.length > 0) {
        filtered[category] = matchingSymptoms;
        hasMatches = true;
      }
    });

    setFilteredCategories(hasMatches ? filtered : {});
    setHighlightedIndex(hasMatches ? 0 : -1); // Highlight first match
  }, [searchTerm, symptomSource]);

  /**
   * Feature 10.5 - Validation Rules
   * 
   * Validates and adds a symptom to the selected list.
   * 
   * Rules:
   * - At least 0 symptoms (optional field) ✓
   * - Maximum {maxSymptoms} symptoms (prevent spam) ✓
   * - Each symptom 2-30 characters ✓
   * - No duplicate symptoms ✓
   * - Sanitize custom inputs (remove special chars) ✓
   * 
   * @param {string} symptom - The symptom to add
   */
  const handleAddSymptom = (symptom) => {
    // Rule: Sanitize custom inputs (remove special chars, keep alphanumeric, spaces, hyphens, underscores)
    const sanitizedSymptom = symptom
      .replace(/[^a-zA-Z0-9\s\-_]/g, '')
      .trim()
      .toLowerCase();

    // Empty after sanitization
    if (!sanitizedSymptom) {
      setError("Please enter a valid symptom.");
      return;
    }

    // Rule: Each symptom 2-30 characters
    if (sanitizedSymptom.length < 2) {
      setError("Symptom must be at least 2 characters.");
      return;
    }
    
    if (sanitizedSymptom.length > 30) {
      setError("Symptom must be 30 characters or less.");
      return;
    }

    // Rule: No duplicate symptoms (case-insensitive check)
    const isDuplicate = selectedSymptoms.some(
      s => s.toLowerCase() === sanitizedSymptom
    );
    if (isDuplicate) {
      setError("This symptom is already added.");
      setSearchTerm('');
      return;
    }

    // Rule: Maximum {maxSymptoms} symptoms
    if (selectedSymptoms.length >= maxSymptoms) {
      setError(`Maximum ${maxSymptoms} symptoms allowed.`);
      return;
    }

    // All validations passed - add symptom
    const updatedSymptoms = [...selectedSymptoms, sanitizedSymptom];
    setSelectedSymptoms(updatedSymptoms);
    setSearchTerm('');
    setShowDropdown(false);
    setError(null);
  };

  const handleRemoveSymptom = (symptomToRemove) => {
    const updatedSymptoms = selectedSymptoms.filter(s => s !== symptomToRemove);
    setSelectedSymptoms(updatedSymptoms);
    setError(null);
  };

  // Clear all selected symptoms (Feature 10.1)
  const handleClearAll = () => {
    setSelectedSymptoms([]);
    setError(null);
    setSearchTerm('');
    // Focus back on input after clearing
    inputRef.current?.focus();
  };

  /**
   * Feature 10.2 - Tag Input with Keyboard Navigation
   * - Arrow keys to navigate dropdown
   * - Enter to select highlighted or add custom
   * - Backspace to remove last tag
   * - Escape to close dropdown
   */
  const handleKeyDown = (e) => {
    const availableSymptoms = flatFilteredSymptoms.filter(s => !selectedSymptoms.includes(s));
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (!showDropdown) {
          setShowDropdown(true);
        } else if (availableSymptoms.length > 0) {
          setHighlightedIndex(prev => 
            prev < availableSymptoms.length - 1 ? prev + 1 : 0
          );
        }
        break;
        
      case 'ArrowUp':
        e.preventDefault();
        if (availableSymptoms.length > 0) {
          setHighlightedIndex(prev => 
            prev > 0 ? prev - 1 : availableSymptoms.length - 1
          );
        }
        break;
        
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && availableSymptoms[highlightedIndex]) {
          // Select highlighted symptom from dropdown
          handleAddSymptom(availableSymptoms[highlightedIndex]);
        } else if (searchTerm.trim()) {
          // Add custom symptom
          handleAddSymptom(searchTerm);
        }
        break;
        
      case 'Backspace':
        if (!searchTerm && selectedSymptoms.length > 0) {
          // Remove last symptom on backspace if input is empty
          handleRemoveSymptom(selectedSymptoms[selectedSymptoms.length - 1]);
        }
        break;
        
      case 'Escape':
        setShowDropdown(false);
        setHighlightedIndex(-1);
        break;
        
      case 'Tab':
        setShowDropdown(false);
        break;
        
      default:
        break;
    }
  };

  // Format symptom for display (replace underscores with spaces)
  const formatSymptom = (symptom) => {
    return symptom.replace(/_/g, ' ');
  };

  return (
    <div className="symptom-input-container" ref={wrapperRef}>
      <h3>Describe Your Symptoms</h3>
      <p className="subtitle">
        Select from the list or type your own (optional, max {maxSymptoms})
      </p>

      {/* Selected symptoms display as tags (Feature 10.1) */}
      <div className="input-area">
        <div className="tags-input-wrapper">
          {selectedSymptoms.map((symptom, index) => (
            <span key={index} className="symptom-tag">
              {formatSymptom(symptom)}
              <button 
                type="button" 
                onClick={() => handleRemoveSymptom(symptom)}
                className="remove-tag-btn"
                aria-label={`Remove ${formatSymptom(symptom)}`}
              >
                ×
              </button>
            </span>
          ))}
          
          {/* Multi-select input (Feature 10.1) */}
          <input
            ref={inputRef}
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setShowDropdown(true);
              setError(null);
            }}
            onFocus={() => setShowDropdown(true)}
            onKeyDown={handleKeyDown}
            placeholder={selectedSymptoms.length === 0 ? "Type to search or add symptoms..." : "Add more..."}
            className="symptom-text-input"
            disabled={selectedSymptoms.length >= maxSymptoms}
            aria-label="Search or add symptoms"
          />
        </div>
        
        {/* Clear all functionality (Feature 10.1) */}
        {selectedSymptoms.length > 0 && (
          <button 
            type="button" 
            onClick={handleClearAll} 
            className="clear-all-btn"
            aria-label="Clear all symptoms"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Symptom count indicator */}
      {selectedSymptoms.length > 0 && (
        <div className="symptom-count">
          {selectedSymptoms.length} of {maxSymptoms} symptoms selected
        </div>
      )}

      {error && <div className="error-message" role="alert">{error}</div>}

      {/* Predefined symptom list dropdown with autocomplete (Feature 10.2) */}
      {showDropdown && (
        <div className="symptoms-dropdown" role="listbox" ref={dropdownRef}>
          {Object.keys(filteredCategories).length > 0 ? (
            (() => {
              let globalIndex = -1;
              
              return Object.entries(filteredCategories).map(([category, symptoms]) => (
                <div key={category} className="category-group">
                  <div className="category-header">{category}</div>
                  <div className="symptoms-list">
                    {symptoms.map(symptom => {
                      const isSelected = selectedSymptoms.includes(symptom);
                      if (!isSelected) globalIndex++;
                      const isHighlighted = !isSelected && globalIndex === highlightedIndex;
                      
                      return (
                        <button
                          key={symptom}
                          type="button"
                          className={`symptom-option ${isSelected ? 'selected' : ''} ${isHighlighted ? 'highlighted' : ''}`}
                          onClick={() => handleAddSymptom(symptom)}
                          disabled={isSelected}
                          role="option"
                          aria-selected={isSelected}
                        >
                          {formatSymptom(symptom)}
                          {isSelected && <span className="check-icon">✓</span>}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ));
            })()
          ) : (
            /* Custom symptom entry (Feature 10.2) */
            <div className="no-results">
              <p>No matching symptoms found.</p>
              {searchTerm && (
                <button 
                  type="button" 
                  className="add-custom-btn"
                  onClick={() => handleAddSymptom(searchTerm)}
                >
                  Add "{searchTerm}" as custom symptom
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/**
 * Feature 10.5 - Props Interface
 * 
 * @prop {function} onSymptomsChange - Callback when symptoms change: (symptoms: string[]) => void
 * @prop {number} maxSymptoms - Maximum allowed symptoms (default: 10)
 * @prop {string[]} predefinedSymptoms - Optional custom symptom list (overrides default categories)
 */
SymptomInput.propTypes = {
  onSymptomsChange: PropTypes.func.isRequired,
  maxSymptoms: PropTypes.number,
  predefinedSymptoms: PropTypes.arrayOf(PropTypes.string)
};

SymptomInput.defaultProps = {
  maxSymptoms: 10,
  predefinedSymptoms: null
};

export default SymptomInput;
