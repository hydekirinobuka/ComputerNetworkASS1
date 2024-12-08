import React, { useState } from 'react';
import axios from 'axios';
import './download.css';

const Download = () => {
  const [magnetLink, setMagnetLink] = useState('');
  const [message, setMessage] = useState('');

  const handleDownload = async () => {
    if (!magnetLink) {
      setMessage("Please enter a magnet link to download.");
      return;
    }

    // Get token from localStorage
    const token = localStorage.getItem('access_token');
    if (!token) {
      setMessage("You need to log in before connecting to a peer.");
      return;
    }

    try {
      const encodedMagnet = encodeURIComponent(magnetLink);
      const response = await axios.post(
        `http://127.0.0.1:5000/tracker/downloading/${encodedMagnet}`,
        {}, 
        {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          withCredentials: true
        }
      );

      if (response.status === 200) {
        const { pieces, file_name } = response.data;
        const decodedPieces = pieces.map(piece => Uint8Array.from(atob(piece), c => c.charCodeAt(0)));
        const combinedBlob = new Blob(decodedPieces);
        const downloadUrl = window.URL.createObjectURL(combinedBlob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.setAttribute('download', file_name);
        document.body.appendChild(link);
        link.click();
        link.remove();

        setMessage("File is ready to download.");
      } else {
        setMessage("Failed to download file.");
      }
    } catch (error) {
      setMessage("Failed to download file.");
    }
  };

  return (
    <div className="download-container">
      <h2>Download File</h2>
      <input
        type="text"
        placeholder="Enter magnet link"
        value={magnetLink}
        onChange={(e) => setMagnetLink(e.target.value)}
        className="download-input"
      />
      <button onClick={handleDownload} className="download-button">Download</button>
      {message && <p className="download-message">{message}</p>}
    </div>
  );
};

export default Download;
