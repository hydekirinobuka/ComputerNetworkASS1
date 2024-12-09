import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Connection.css';

const Connection = ({ onConnect, token }) => {
  const [status, setStatus] = useState('Disconnected');
  const [isLoading, setIsLoading] = useState(false);

  // Check if token is valid whenever the component renders or token changes
  useEffect(() => {
    if (!token) {
      setStatus("Please login to make connection");
      console.warn("No token available. User must log in.");
    }
  }, [token]);

  const handleConnect = async () => {
    if (!token) {
      setStatus("Please log in to initiate the connection.");
      return;
    }

    setIsLoading(true);
    try {
      // Fetch peer info
      const peerInfoResponse = await axios.get(`http://127.0.0.1:5000/peer/info`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      const { ip_address, port } = peerInfoResponse.data;

      // Start the peer connection
      const startPeerResponse = await axios.post(
        `http://127.0.0.1:5000/peer/start_peer`,
        { ip_address, port },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setStatus(`Connected successfully: ${startPeerResponse.data.status}`);
      console.log("Connection successful:", startPeerResponse.data);

      if (onConnect) onConnect();
    } catch (error) {
      console.error("Error during connection:", error);
      setStatus(error.response?.data?.error || "Failed to connect to the P2P network.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="connection-container">
      <button
        className="connection-button"
        onClick={handleConnect}
        disabled={isLoading}
      >
        {isLoading ? "Connecting..." : "Connect to P2P Network"}
      </button>
      {status && <p className="connection-status">{status}</p>}
    </div>
  );
};

export default Connection;
