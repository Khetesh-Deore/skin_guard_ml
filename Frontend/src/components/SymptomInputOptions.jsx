/**
 * Feature 10.2: Input Methods
 * 
 * This file exports both symptom input options:
 * - Option 1: SymptomCheckboxList - Checkbox-based selection
 * - Option 2: SymptomInput - Tag input with autocomplete (Recommended)
 * 
 * Usage:
 * ```jsx
 * // Option 1: Checkbox List
 * import { SymptomCheckboxList } from './SymptomInputOptions';
 * <SymptomCheckboxList onSymptomsChange={handleSymptoms} />
 * 
 * // Option 2: Tag Input (Recommended)
 * import { SymptomInput } from './SymptomInputOptions';
 * <SymptomInput onSymptomsChange={handleSymptoms} />
 * 
 * // Or use the default (Tag Input)
 * import SymptomInputDefault from './SymptomInputOptions';
 * <SymptomInputDefault onSymptomsChange={handleSymptoms} />
 * ```
 */

// Option 1: Checkbox List
export { default as SymptomCheckboxList } from './SymptomCheckboxList';

// Option 2: Tag Input (Recommended)
export { default as SymptomInput } from './SymptomInput';

// Default export is the recommended option (Tag Input)
export { default } from './SymptomInput';

/**
 * Feature 10.2 Comparison:
 * 
 * Option 1: Checkbox List
 * ✓ Display common symptoms as checkboxes
 * ✓ User can check multiple
 * ✓ Group symptoms by category
 * ✓ Visual overview of all options
 * ✗ Takes more screen space
 * ✗ No custom symptom entry
 * 
 * Option 2: Tag Input (Recommended)
 * ✓ Dropdown with autocomplete
 * ✓ Selected symptoms appear as removable tags
 * ✓ Type to filter symptoms
 * ✓ Add custom symptoms (with validation)
 * ✓ Compact design
 * ✓ Keyboard navigation
 * ✓ Better for mobile
 */
