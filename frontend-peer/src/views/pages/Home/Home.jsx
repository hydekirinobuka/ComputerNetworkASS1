import React, { useState } from 'react';
import './Home.css';
import Connection from '../../../components/Connections/Connection';
import Upload from '../../../components/Upload/upload';
import Download from '../../../components/Download/download';

const Home = ({ token }) => {

  const [isConnected, setIsConnected] = useState(false);

  const handleConnectionSuccess = () => {
    setIsConnected(true);
  };

  return (
      <div className="home-container">
        <h1 className="welcome-message">Welcome to My Group STA </h1>
        <Connection token={token} onConnect={handleConnectionSuccess} />
        {isConnected && (
          <div>
            <p className="connected-message">Connected to P2P Network</p>
            <Upload isConnected={isConnected} />
            <Download />
          </div>
        )}
      </div>
  );
};

export default Home;
