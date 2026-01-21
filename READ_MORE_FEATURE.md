# Read More/Less Feature

## Overview
Added collapsible "Read More/Read Less" functionality to all disease information boxes to improve readability and reduce initial content overload.

## Features

### 1. Initial Display (Collapsed State)
- Shows only **2 lines** of text initially
- Uses CSS `-webkit-line-clamp` for clean truncation
- Adds ellipsis (...) at the end of truncated text
- Smooth transition animation when expanding/collapsing

### 2. Read More Button
- Appears at the bottom of each box when content exceeds threshold
- **Main boxes threshold**: 200 characters for description/root_cause, 150 for causes/common_in
- **Alternative boxes threshold**: 200 characters
- Button text changes: "Read More ▼" / "Read Less ▲"
- Hover effect with color change and background highlight

### 3. Boxes with Read More/Less

#### Main Disease Information Section
1. **📋 Description Box** - Shows if content > 200 chars
2. **🔬 Root Cause Box** - Shows if content > 200 chars
3. **⚡ Common Causes Box** - Shows if content > 150 chars
4. **👥 Commonly Affects Box** - Shows if content > 150 chars

#### Alternative Possibilities Section
1. **Description** - Shows if content > 200 chars
2. **Root Cause** - Shows if content > 200 chars

## Implementation Details

### State Management
```javascript
// Main boxes state
const [expandedBoxes, setExpandedBoxes] = useState({
  description: false,
  rootCause: false,
  causes: false,
  commonIn: false,
});

// Alternative boxes state (dynamic per item)
const [expandedAltBoxes, setExpandedAltBoxes] = useState({});
```

### CSS Classes
- `.info-box-content.collapsed` - 2-line truncation for main boxes
- `.info-box-content.expanded` - Full content display
- `.alt-description.collapsed` - 2-line truncation for alternatives
- `.alt-root-cause.collapsed` - 2-line truncation for alternatives
- `.read-more-btn` - Main button styling
- `.read-more-btn-small` - Smaller button for alternatives

### Visual Behavior
1. **Collapsed (Default)**:
   - Max height: 3.4em (2 lines × 1.7 line-height)
   - Overflow: hidden
   - Text overflow: ellipsis
   - Display: -webkit-box with line-clamp

2. **Expanded**:
   - Max height: none
   - Display: block
   - Full content visible

3. **Transition**:
   - Smooth 0.3s ease animation
   - Button text changes instantly
   - Content expands/collapses smoothly

## User Experience Benefits

1. **Reduced Clutter**: Initial view shows concise information
2. **Better Scanning**: Users can quickly scan all sections
3. **On-Demand Details**: Full information available with one click
4. **Mobile Friendly**: Especially helpful on smaller screens
5. **Visual Feedback**: Clear button states and hover effects
6. **Smooth Animations**: Professional feel with CSS transitions

## Example Usage

### Before (Always Expanded)
```
📋 Description
[200+ words of text taking up entire screen...]
```

### After (Collapsible)
```
📋 Description
Acne is one of the most common skin conditions worldwide, 
affecting approximately 85% of people between ages 12-24...
[Read More ▼]
```

### After Clicking Read More
```
📋 Description
[Full 200+ word description displayed]
[Read Less ▲]
```

## Files Modified
- `Frontend/src/components/ResultDisplay.jsx` - Added state and toggle logic
- `Frontend/src/components/ResultDisplay.css` - Added collapsed/expanded styles

## Browser Compatibility
- Uses `-webkit-line-clamp` (supported in all modern browsers)
- Fallback: Content will show fully if line-clamp not supported
- Tested on: Chrome, Firefox, Safari, Edge
