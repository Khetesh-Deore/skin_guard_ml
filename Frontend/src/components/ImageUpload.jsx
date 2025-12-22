import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import './ImageUpload.css';

/**
 * ImageUpload Component (Feature 9)
 * 
 * Props Interface (Feature 9.5):
 * @param {function} onImageSelect - Callback when file is selected/cleared: (file: File | null) => void
 * @param {number} maxSizeInMB - Maximum file size in MB (default: 5)
 * @param {string[]} acceptedFormats - Accepted MIME types (default: ['image/jpeg', 'image/png', 'image/jpg'])
 * @param {boolean} isUploading - External upload state to disable interactions
 */
const ImageUpload = ({ 
  onImageSelect, 
  maxSizeInMB = 5, 
  acceptedFormats = ['image/jpeg', 'image/png', 'image/jpg'], 
  isUploading = false 
}) => {
  // State Variables per Feature 9.2
  const [selectedFile, setSelectedFile] = useState(null);      // null | File
  const [previewUrl, setPreviewUrl] = useState(null);          // null | string
  const [uploadError, setUploadError] = useState(null);        // null | string
  const [isDragging, setIsDragging] = useState(false);         // boolean
  const [isProcessing, setIsProcessing] = useState(false);     // local processing state
  const [imageLoaded, setImageLoaded] = useState(false);       // preview image loaded state
  const fileInputRef = useRef(null);

  useEffect(() => {
    // Cleanup preview URL to prevent memory leaks
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const validateFile = (file) => {
    if (!file) return false;

    // Check file type
    if (!acceptedFormats.includes(file.type)) {
      setUploadError('Invalid file format. Please upload JPG or PNG.');
      // Clear previous selection on invalid file (Feature 9.4 step 4)
      clearPreviousSelection();
      return false;
    }

    // Check file size
    if (file.size > maxSizeInMB * 1024 * 1024) {
      setUploadError(`File size exceeds ${maxSizeInMB}MB limit. Your file: ${formatFileSize(file.size)}`);
      // Clear previous selection on invalid file (Feature 9.4 step 4)
      clearPreviousSelection();
      return false;
    }

    return true;
  };

  // Helper to clear selection without triggering parent callback
  const clearPreviousSelection = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setImageLoaded(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /**
   * File Selection Flow (Feature 9.4):
   * 1. User clicks "Choose File" or drags file
   * 2. Validate file type and size
   * 3. If valid: Store file, generate preview, notify parent (enables submit)
   * 4. If invalid: Show error, clear previous selection
   */
  const handleFileSelect = async (file) => {
    setUploadError(null);
    
    // Step 2: Validate file type and size
    if (validateFile(file)) {
      setIsProcessing(true);
      
      // Small delay to show processing state for better UX
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Step 3: If valid - Store file in state
      setSelectedFile(file);
      
      // Step 3: Generate preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      
      // Step 3: Notify parent (enables submit button in App.jsx)
      onImageSelect(file);
      
      setIsProcessing(false);
    }
    // Step 4 (invalid case) is handled in validateFile()
  };

  const onDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Only highlight if dragging files (not other elements)
    if (e.dataTransfer.types.includes('Files')) {
      setIsDragging(true);
    }
  };

  const onDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.dataTransfer.types.includes('Files')) {
      setIsDragging(true);
    }
  };

  const onDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Only remove highlight if leaving the drop zone entirely
    // Check if we're leaving to a child element
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX;
    const y = e.clientY;
    
    if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
      setIsDragging(false);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    // Don't process if uploading
    if (isUploading) return;
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      // Only take the first file if multiple dropped
      const file = files[0];
      
      // Quick type check before full validation
      if (!file.type.startsWith('image/')) {
        setUploadError('Please drop an image file (JPG or PNG).');
        return;
      }
      
      handleFileSelect(file);
    }
  };

  const handleInputChange = (e) => {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const clearSelection = () => {
    // Clear all state
    clearPreviousSelection();
    setUploadError(null);
    // Notify parent that file was removed (disables submit button)
    onImageSelect(null);
  };

  return (
    <div className="image-upload-container">
      <h3>Upload Skin Image</h3>
      
      {isProcessing && (
        <div className="processing-overlay">
          <div className="processing-spinner"></div>
          <p>Processing image...</p>
        </div>
      )}
      
      {!previewUrl ? (
        <div 
          className={`upload-area ${isDragging ? 'dragging' : ''} ${uploadError ? 'error' : ''} ${isUploading ? 'uploading' : ''}`}
          onDragOver={onDragOver}
          onDragEnter={onDragEnter}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => !isUploading && fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if ((e.key === 'Enter' || e.key === ' ') && !isUploading) {
              e.preventDefault();
              fileInputRef.current?.click();
            }
          }}
          aria-label="Upload image area. Click or drag and drop an image file."
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleInputChange}
            accept={acceptedFormats.join(',')}
            style={{ display: 'none' }}
            disabled={isUploading}
          />
          <div className="upload-placeholder">
            <span className="upload-icon">📷</span>
            <p>Drag & Drop your image here</p>
            <p className="upload-hint">or click to browse</p>
            <p className="file-limits">JPG, PNG (Max {maxSizeInMB}MB)</p>
          </div>
        </div>
      ) : (
        /* Feature 9.5: Image Preview Section */
        <div className="preview-area">
          <div className="image-preview-wrapper">
            {/* Thumbnail display */}
            <img 
              src={previewUrl} 
              alt="Skin condition preview" 
              className={`image-preview ${imageLoaded ? 'loaded' : ''}`}
              onLoad={() => setImageLoaded(true)}
            />
            
            {/* Success indicator when image loads */}
            {imageLoaded && !isUploading && (
              <span className="preview-success-badge" aria-label="Image loaded successfully">✓</span>
            )}
            
            {/* Remove button to clear selection */}
            {!isUploading && (
              <button 
                type="button" 
                className="remove-image-btn"
                onClick={clearSelection}
                aria-label="Remove image"
              >
                ×
              </button>
            )}
            
            {isUploading && (
              <div className="upload-progress-overlay">
                <div className="upload-spinner"></div>
              </div>
            )}
          </div>
          
          {/* File name and size display */}
          <div className="file-info">
            <div className="file-details">
              <span className="file-name" title={selectedFile.name}>{selectedFile.name}</span>
              <span className="file-size">{formatFileSize(selectedFile.size)}</span>
            </div>
            {!isUploading && (
              <button type="button" className="change-btn" onClick={clearSelection}>
                Change Image
              </button>
            )}
            {isUploading && (
              <span className="uploading-text">Uploading...</span>
            )}
          </div>
        </div>
      )}

      {uploadError && <div className="error-message">{uploadError}</div>}
    </div>
  );
};

// PropTypes for documentation and runtime type checking (Feature 9.5)
ImageUpload.propTypes = {
  onImageSelect: PropTypes.func.isRequired,
  maxSizeInMB: PropTypes.number,
  acceptedFormats: PropTypes.arrayOf(PropTypes.string),
  isUploading: PropTypes.bool
};

export default ImageUpload;
