# SkinGuard ML - Frontend

React-based web interface for skin disease analysis.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at `http://localhost:5173`

## Scripts

```bash
npm run dev      # Start dev server
npm run build    # Production build
npm run preview  # Preview production build
npm run test     # Run tests
npm run lint     # Lint code
```

## Project Structure

```
Frontend/
├── src/
│   ├── App.jsx              # Main application
│   ├── main.jsx             # Entry point
│   ├── components/
│   │   ├── ImageUpload.jsx  # Image upload
│   │   ├── SymptomInput.jsx # Symptom selection
│   │   ├── ResultDisplay.jsx # Results display
│   │   └── LoadingSpinner.jsx
│   └── services/
│       └── api.js           # API service
├── public/
├── package.json
├── vite.config.js
└── .env
```

## Components

### ImageUpload
- Drag & drop support
- File type validation (JPG, PNG)
- Image preview
- Size limit (5MB)

### SymptomInput
- Multi-select with search
- Predefined symptom categories
- Custom symptom entry
- Tag-based display

### ResultDisplay
- Disease prediction with confidence
- Severity color coding
- Recommendations sections
- Medical disclaimer

## Configuration

Create `.env` file:
```env
VITE_API_URL=http://localhost:5000/api
VITE_MAX_FILE_SIZE_MB=5
```

## API Service

```javascript
import { predictDisease, checkHealth } from './services/api';

// Predict disease
const result = await predictDisease(imageFile, symptoms);

// Check API health
const health = await checkHealth();
```

## Features

- ✅ Image upload with preview
- ✅ Symptom selection (4 categories)
- ✅ Real-time analysis
- ✅ Confidence visualization
- ✅ Severity assessment
- ✅ Personalized recommendations
- ✅ Responsive design
- ✅ Error handling
- ✅ Loading states

## Symptom Categories

1. **Skin Appearance**: redness, patches, spots, bumps, scaling
2. **Sensations**: itching, burning, pain, tenderness
3. **Texture**: dry_skin, oily_skin, rough_skin, thickened_skin
4. **Other**: oozing, crusting, swelling, bleeding

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT License
