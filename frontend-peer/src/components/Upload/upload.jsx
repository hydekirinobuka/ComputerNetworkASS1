import React, { useState } from 'react';
import axios from 'axios';
import './upload.css';

const Upload = ({ isConnected }) => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isUploaded, setIsUploaded] = useState(false); 
  const [isError, setIsError] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage(''); 
  };

  const handleUpload = async () => {
    if (!isConnected) {
      setMessage("You need to be connected to upload files.");
      setIsError(true);
      return;
    }

    if (!file) {
      setMessage("Please select a file to upload.");
      setIsError(true);
      return;
    }

    // Get token from localStorage
    const token = localStorage.getItem('access_token');
    if (!token) {
      setMessage("You need to log in before uploading.");
      setIsError(true);
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:5000/tracker/uploading', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true,
      });

      setMessage(response.data.message || "File uploaded successfully.");
      setIsUploaded(true);
      setIsError(false);
    } catch (error) {
      setMessage(error.response?.data?.error || "Failed to upload file.");
      setIsError(true);
    }
  };

  const handleRedirect = () => {
    window.open('http://localhost:3001', '_blank'); // Redirect to frontend-tracker
  };

  return (
    <div className="upload-container">
      <h2>Upload File</h2>
      <input id="up" type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} className="upload-button">Upload</button>
      {message && (
        <p className={`upload-message ${isError ? 'error-message' : 'success-message'}`}>
          {message}
        </p>
      )}
      {isUploaded && (
        <div>
          <p className="uploadOK">You have uploaded the file successfully, you can find the magnetlink via tracker</p>
        </div>
      )}
      <div className="Magnet">
        <p>Get MagnetLink Below</p>
        <button onClick={handleRedirect} className="redirect-button">
          Go to Frontend-Tracker
        </button>
      </div>
    </div>
  );
};

export default Upload;
