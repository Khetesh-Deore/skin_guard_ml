import React from 'react';
import '../styles/LoadingSpinner.css';

const LoadingSpinner = ({ message = 'Processing...' }) => {
  return (
    <div className="loading-container">
      <div className="spinner-ring"></div>
      <p className="loading-message">{message}</p>
    </div>
  );
};

export default LoadingSpinner;
