# Disease Information Display Layout

## Updated Frontend Display Structure

The disease information is now displayed in **separate, distinct boxes** for better readability and organization.

### Main Disease Information Section

Located below the confidence visualization and above alternative possibilities, the disease information is displayed in 4 separate boxes:

#### 1. 📋 Description Box
- **Border Color**: Blue (#2196f3)
- **Content**: Full 200+ word description of the disease
- **Style**: White background with blue left border, hover effect

#### 2. 🔬 Root Cause & Pathophysiology Box
- **Border Color**: Purple (#9c27b0)
- **Content**: Detailed explanation of the underlying mechanisms and pathophysiology (200+ words)
- **Style**: White background with purple left border, hover effect

#### 3. ⚡ Common Causes Box
- **Border Color**: Orange (#ff9800)
- **Content**: Brief summary of common causes
- **Style**: White background with orange left border, hover effect

#### 4. 👥 Commonly Affects Box
- **Border Color**: Green (#4caf50)
- **Content**: Demographics and populations commonly affected
- **Style**: White background with green left border, hover effect

### Alternative Possibilities Section

Each alternative disease also displays information in organized sections:

- **📋 Description**: Full description of the alternative condition
- **🔬 Root Cause**: Root cause and pathophysiology of the alternative condition

### Visual Features

1. **Hover Effects**: Each box lifts slightly and shows enhanced shadow on hover
2. **Color Coding**: Different colored left borders for easy identification
3. **Icons**: Emoji icons for quick visual recognition
4. **Responsive**: Adapts to mobile and desktop screens
5. **Clean Layout**: Proper spacing and typography for readability

### Box Structure

```
┌─────────────────────────────────────────┐
│ 📋 Description                          │
├─────────────────────────────────────────┤
│ Full 200+ word description text...     │
│ [Justified text, easy to read]         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🔬 Root Cause & Pathophysiology         │
├─────────────────────────────────────────┤
│ Detailed explanation of mechanisms...  │
│ [Justified text, easy to read]         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ ⚡ Common Causes                         │
├─────────────────────────────────────────┤
│ Brief summary of causes                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 👥 Commonly Affects                     │
├─────────────────────────────────────────┤
│ Demographics information               │
└─────────────────────────────────────────┘
```

## Implementation Details

### Frontend Files Modified
- `Frontend/src/components/ResultDisplay.jsx` - Component structure
- `Frontend/src/components/ResultDisplay.css` - Styling

### Backend Files (Already Updated)
- `Backend/modules/disease_descriptions.py` - All 22 diseases with 200+ word descriptions and root_cause
- `Backend/routes/predict_routes.py` - API passes all fields including root_cause

### Key CSS Classes
- `.info-box` - Base box styling
- `.description-box` - Blue border
- `.root-cause-box` - Purple border
- `.causes-box` - Orange border
- `.common-in-box` - Green border
- `.info-box-header` - Header with icon and title
- `.info-box-content` - Content text styling

## Benefits

1. **Better Organization**: Each piece of information in its own clearly defined space
2. **Visual Hierarchy**: Color coding helps users quickly identify different types of information
3. **Improved Readability**: Separate boxes prevent information overload
4. **Professional Appearance**: Clean, modern design with subtle animations
5. **Accessibility**: Clear labels and good contrast ratios
6. **Responsive**: Works well on all screen sizes
