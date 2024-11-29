import React, { useState } from 'react';
import axios from 'axios';
import './upload.css';
import { useNavigate } from 'react-router-dom';

axios.defaults.withCredentials = true;

const getCookieValue = (name) => {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
};

const Upload = ({ isConnected }) => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isUploaded, setIsUploaded] = useState(false); // Track upload success status
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!isConnected) {
      setMessage("You need to be connected to upload files.");
      return;
    }

    if (!file) {
      setMessage("Please select a file to upload.");
      return;
    }

    const peerId = getCookieValue("peer_id");
    if (!peerId) {
      setMessage("Bạn cần phải đăng nhập trước khi upload.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('peer_id', peerId); 

    try {
      const response = await axios.post('http://127.0.0.1:5000/tracker/uploading', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true,
      });

      setMessage(response.data.message || "File uploaded successfully.");
      setIsUploaded(true);
    } catch (error) {
      setMessage(error.response?.data?.error || "Failed to upload file.");
    }
  };
  const handleRedirect = () => {
    window.location.href = 'http://localhost:3001'; // Redirect to frontend-tracker
  };
  return (
    <div className="upload-container">
      <h2>Upload File</h2>
      <input id="up" type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} className="upload-button">Upload</button>
      {message && <p className="upload-message">{message}</p>}
      {isUploaded && (
        <div>
          <p>Upload successful!</p>
          <button onClick={handleRedirect} className="redirect-button">
            Go to Frontend-Tracker
          </button>
        </div>
      )}
    </div>
  );
};

export default Upload;
