import { useState, useRef, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import './ImageUpload.css';

const ImageUpload = ({ 
  onImageSelect, 
  maxSizeInMB = 5, 
  acceptedFormats = ['image/jpeg', 'image/png', 'image/jpg'], 
  isUploading = false 
}) => {
  const [uploadMethod, setUploadMethod] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isCameraInitializing, setIsCameraInitializing] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [capturedImagePreview, setCapturedImagePreview] = useState(null);
  const [cameraError, setCameraError] = useState(null);
  const [hasMultipleCameras, setHasMultipleCameras] = useState(false);
  const [currentFacingMode, setCurrentFacingMode] = useState('environment');
  const [activeCameraLabel, setActiveCameraLabel] = useState('');
  
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const mountedRef = useRef(true);

  const stopCameraStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
    setActiveCameraLabel('');
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      stopCameraStream();
    };
  }, [stopCameraStream]);

  const checkForMultipleCameras = useCallback(async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(d => d.kind === 'videoinput');
      const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
      if (mountedRef.current) {
        setHasMultipleCameras(videoDevices.length > 1 || isMobile);
      }
    } catch (err) {
      console.error('[Camera] Enumerate error:', err);
    }
  }, []);

  const startCamera = useCallback(async (facingMode = 'environment') => {
    if (!mountedRef.current) return;
    
    setCameraError(null);
    setIsCameraInitializing(true);
    setIsCameraActive(false);
    
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError('Camera not supported. Please use upload instead.');
      setIsCameraInitializing(false);
      return;
    }

    stopCameraStream();

    try {
      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: facingMode }, width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false
        });
      } catch {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      }

      if (!mountedRef.current) {
        stream.getTracks().forEach(t => t.stop());
        return;
      }

      streamRef.current = stream;
      
      const videoTrack = stream.getVideoTracks()[0];
      if (videoTrack) {
        const settings = videoTrack.getSettings();
        setActiveCameraLabel(settings.facingMode === 'user' ? 'Front' : 'Rear');
        setCurrentFacingMode(settings.facingMode || facingMode);
      }

      await checkForMultipleCameras();

      if (videoRef.current && mountedRef.current) {
        videoRef.current.srcObject = stream;
        
        videoRef.current.onloadedmetadata = () => {
          if (!mountedRef.current) return;
          videoRef.current.play()
            .then(() => {
              if (mountedRef.current) {
                setIsCameraActive(true);
                setIsCameraInitializing(false);
              }
            })
            .catch(() => {
              if (mountedRef.current) {
                setCameraError('Failed to start video. Please try again.');
                setIsCameraInitializing(false);
              }
            });
        };

        setTimeout(() => {
          if (mountedRef.current && !isCameraActive && videoRef.current?.srcObject) {
            videoRef.current.play().catch(() => {});
            setIsCameraActive(true);
            setIsCameraInitializing(false);
          }
        }, 3000);
      }
    } catch (err) {
      if (!mountedRef.current) return;
      
      let msg = 'Unable to access camera.';
      if (err.name === 'NotAllowedError') msg = 'Camera access denied. Please allow camera in browser settings.';
      else if (err.name === 'NotFoundError') msg = 'No camera found on this device.';
      else if (err.name === 'NotReadableError') msg = 'Camera in use by another app.';
      
      setCameraError(msg);
      setIsCameraInitializing(false);
    }
  }, [stopCameraStream, checkForMultipleCameras, isCameraActive]);

  const switchCamera = useCallback(() => {
    const newMode = currentFacingMode === 'environment' ? 'user' : 'environment';
    startCamera(newMode);
  }, [currentFacingMode, startCamera]);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const width = video.videoWidth || 640;
    const height = video.videoHeight || 480;
    
    canvas.width = width;
    canvas.height = height;
    
    const ctx = canvas.getContext('2d');
    if (currentFacingMode === 'user') {
      ctx.translate(width, 0);
      ctx.scale(-1, 1);
    }
    ctx.drawImage(video, 0, 0, width, height);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    
    canvas.toBlob((blob) => {
      if (!blob) {
        setCameraError('Failed to capture. Please try again.');
        return;
      }
      
      const file = new File([blob], `camera-capture-${Date.now()}.jpg`, { type: 'image/jpeg' });
      
      if (file.size > maxSizeInMB * 1024 * 1024) {
        setCameraError(`Image too large (${(file.size/1024/1024).toFixed(1)}MB). Max: ${maxSizeInMB}MB.`);
        return;
      }
      
      setCapturedImage(file);
      setCapturedImagePreview(URL.createObjectURL(blob));
      stopCameraStream();
    }, 'image/jpeg', 0.9);
  }, [currentFacingMode, maxSizeInMB, stopCameraStream]);

  const retakePhoto = useCallback(() => {
    if (capturedImagePreview) URL.revokeObjectURL(capturedImagePreview);
    setCapturedImage(null);
    setCapturedImagePreview(null);
    setCameraError(null);
    startCamera(currentFacingMode);
  }, [capturedImagePreview, currentFacingMode, startCamera]);

  const usePhoto = useCallback(() => {
    if (capturedImage) {
      setSelectedFile(capturedImage);
      setPreviewUrl(capturedImagePreview);
      setCapturedImage(null);
      setCapturedImagePreview(null);
      setImageLoaded(true);
      onImageSelect(capturedImage);
    }
  }, [capturedImage, capturedImagePreview, onImageSelect]);

  const cancelCapture = useCallback(() => {
    stopCameraStream();
    if (capturedImagePreview) URL.revokeObjectURL(capturedImagePreview);
    setCapturedImage(null);
    setCapturedImagePreview(null);
    setCameraError(null);
    setUploadMethod(null);
  }, [capturedImagePreview, stopCameraStream]);

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const clearPreviousSelection = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(null);
    setPreviewUrl(null);
    setImageLoaded(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const validateFile = (file) => {
    if (!file) return false;
    if (!acceptedFormats.includes(file.type)) {
      setUploadError('Invalid format. Please upload JPG or PNG.');
      clearPreviousSelection();
      return false;
    }
    if (file.size > maxSizeInMB * 1024 * 1024) {
      setUploadError(`File too large (${formatFileSize(file.size)}). Max: ${maxSizeInMB}MB.`);
      clearPreviousSelection();
      return false;
    }
    return true;
  };

  const handleFileSelect = async (file) => {
    setUploadError(null);
    if (validateFile(file)) {
      setIsProcessing(true);
      await new Promise(r => setTimeout(r, 100));
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      onImageSelect(file);
      setIsProcessing(false);
    }
  };

  const onDragOver = (e) => { e.preventDefault(); e.stopPropagation(); if (e.dataTransfer.types.includes('Files')) setIsDragging(true); };
  const onDragEnter = (e) => { e.preventDefault(); e.stopPropagation(); if (e.dataTransfer.types.includes('Files')) setIsDragging(true); };
  const onDragLeave = (e) => {
    e.preventDefault(); e.stopPropagation();
    const rect = e.currentTarget.getBoundingClientRect();
    if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) setIsDragging(false);
  };
  const onDrop = (e) => {
    e.preventDefault(); e.stopPropagation(); setIsDragging(false);
    if (isUploading) return;
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      if (!files[0].type.startsWith('image/')) { setUploadError('Please drop an image file.'); return; }
      handleFileSelect(files[0]);
    }
  };

  const handleInputChange = (e) => { if (e.target.files.length > 0) handleFileSelect(e.target.files[0]); };
  
  const clearSelection = () => {
    clearPreviousSelection();
    setUploadError(null);
    setUploadMethod(null);
    onImageSelect(null);
  };

  const selectMethod = (method) => {
    setUploadMethod(method);
    setUploadError(null);
    setCameraError(null);
    if (method === 'camera') startCamera('environment');
  };

  const changeMethod = () => {
    stopCameraStream();
    if (capturedImagePreview) URL.revokeObjectURL(capturedImagePreview);
    setCapturedImage(null);
    setCapturedImagePreview(null);
    setCameraError(null);
    setUploadError(null);
    setUploadMethod(null);
  };

  const isCameraSupported = typeof navigator !== 'undefined' && navigator.mediaDevices?.getUserMedia;

  return (
    <div className="image-upload-container">
      <h3>Upload Skin Image</h3>
      
      {isProcessing && (
        <div className="processing-overlay">
          <div className="processing-spinner"></div>
          <p>Processing image...</p>
        </div>
      )}
      
      {previewUrl ? (
        <div className="preview-area">
          <div className="image-preview-wrapper">
            <img src={previewUrl} alt="Preview" className={`image-preview ${imageLoaded ? 'loaded' : ''}`} onLoad={() => setImageLoaded(true)} />
            {imageLoaded && !isUploading && <span className="preview-success-badge">✓</span>}
            {!isUploading && <button type="button" className="remove-image-btn" onClick={clearSelection}>×</button>}
            {isUploading && <div className="upload-progress-overlay"><div className="upload-spinner"></div></div>}
          </div>
          <div className="file-info">
            <div className="file-details">
              <span className="file-name" title={selectedFile?.name}>{selectedFile?.name}</span>
              <span className="file-size">{selectedFile && formatFileSize(selectedFile.size)}</span>
            </div>
            {!isUploading ? <button type="button" className="change-btn" onClick={clearSelection}>Change Image</button> : <span className="uploading-text">Uploading...</span>}
          </div>
        </div>
      ) : (
        <>
          {!uploadMethod && (
            <div className="method-selection">
              <div className="method-card" onClick={() => selectMethod('upload')} onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && selectMethod('upload')} role="button" tabIndex={0}>
                <span className="method-icon">📁</span>
                <span className="method-title">Upload Image</span>
                <span className="method-desc">Choose from device</span>
              </div>
              {isCameraSupported && (
                <div className="method-card" onClick={() => selectMethod('camera')} onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && selectMethod('camera')} role="button" tabIndex={0}>
                  <span className="method-icon">📷</span>
                  <span className="method-title">Capture Photo</span>
                  <span className="method-desc">Use your camera</span>
                </div>
              )}
            </div>
          )}
          
          {uploadMethod === 'upload' && (
            <>
              <div className="method-header">
                <span>Upload Image</span>
                <button type="button" className="change-method-btn" onClick={changeMethod}>Change</button>
              </div>
              <div className={`upload-area ${isDragging ? 'dragging' : ''} ${uploadError ? 'error' : ''}`} onDragOver={onDragOver} onDragEnter={onDragEnter} onDragLeave={onDragLeave} onDrop={onDrop} onClick={() => !isUploading && fileInputRef.current?.click()} role="button" tabIndex={0} onKeyDown={(e) => { if ((e.key === 'Enter' || e.key === ' ') && !isUploading) { e.preventDefault(); fileInputRef.current?.click(); } }}>
                <input type="file" ref={fileInputRef} onChange={handleInputChange} accept={acceptedFormats.join(',')} style={{ display: 'none' }} disabled={isUploading} />
                <div className="upload-placeholder">
                  <span className="upload-icon">📷</span>
                  <p>Drag & Drop your image here</p>
                  <p className="upload-hint">or click to browse</p>
                  <p className="file-limits">JPG, PNG (Max {maxSizeInMB}MB)</p>
                </div>
              </div>
            </>
          )}
          
          {uploadMethod === 'camera' && (
            <>
              <div className="method-header">
                <span>Capture Photo{activeCameraLabel && !capturedImagePreview && <span className="camera-label"> ({activeCameraLabel})</span>}</span>
                <button type="button" className="change-method-btn" onClick={changeMethod}>Change</button>
              </div>
              <div className="camera-container">
                <canvas ref={canvasRef} style={{ display: 'none' }} />
                
                {isCameraInitializing && !cameraError && (
                  <div className="camera-loading">
                    <div className="camera-spinner"></div>
                    <p>Initializing camera...</p>
                    <p className="camera-hint">Please allow camera access</p>
                  </div>
                )}
                
                {cameraError && (
                  <div className="camera-error">
                    <span className="error-icon">⚠️</span>
                    <p>{cameraError}</p>
                    <div className="camera-error-actions">
                      <button type="button" onClick={() => startCamera(currentFacingMode)} className="retry-btn">🔄 Try Again</button>
                      <button type="button" onClick={() => selectMethod('upload')} className="fallback-btn">📁 Upload Instead</button>
                    </div>
                  </div>
                )}
                
                {!cameraError && !capturedImagePreview && (
                  <video ref={videoRef} className={`camera-preview ${currentFacingMode === 'user' ? 'mirror' : ''}`} autoPlay playsInline muted style={{ display: isCameraActive ? 'block' : 'none' }} />
                )}
                
                {isCameraActive && !capturedImagePreview && !cameraError && (
                  <div className="camera-controls">
                    {hasMultipleCameras && <button type="button" className="camera-btn switch-btn" onClick={switchCamera} title="Switch Camera">🔄</button>}
                    <button type="button" className="camera-btn capture-btn" onClick={capturePhoto} title="Capture"><span className="capture-ring"></span></button>
                    <button type="button" className="camera-btn cancel-btn" onClick={cancelCapture} title="Cancel">✕</button>
                  </div>
                )}
                
                {capturedImagePreview && (
                  <div className="captured-preview">
                    <img src={capturedImagePreview} alt="Captured" className="captured-image" />
                    <div className="captured-actions">
                      <button type="button" className="action-btn use-btn" onClick={usePhoto}>✓ Use This Photo</button>
                      <button type="button" className="action-btn retake-btn" onClick={retakePhoto}>🔄 Retake</button>
                      <button type="button" className="action-btn cancel-action-btn" onClick={cancelCapture}>✕ Cancel</button>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </>
      )}

      {uploadError && <div className="error-message">{uploadError}</div>}
    </div>
  );
};

ImageUpload.propTypes = {
  onImageSelect: PropTypes.func.isRequired,
  maxSizeInMB: PropTypes.number,
  acceptedFormats: PropTypes.arrayOf(PropTypes.string),
  isUploading: PropTypes.bool
};

export default ImageUpload;
