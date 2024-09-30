import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import './Home.css';

const Home = () => {
  // State to store the battery status
  const [batteryStatus, setBatteryStatus] = useState(null);
  const wifiStatus = 'Connected'; // Example WiFi status, you can replace this with real data as well

  useEffect(() => {
    // Establish WebSocket connection
    const socket = new WebSocket('ws://127.0.0.1:5002'); // Replace with your actual WebSocket URL

    // Handle incoming WebSocket messages
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.percentage !== undefined) {
          setBatteryStatus(data.percentage);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    // Clean up WebSocket connection on component unmount
    return () => {
      socket.close();
    };
  }, []);

  return (
    <div className="home-container">
      <Sidebar />
      <div className="home-content">
        <Header />
        <div className="home-main">
          <Routes>
            <Route
              path="/"
              element={
                <>
              
                  {/* Status Box */}
                  <div className="status-box">
                    <h3>Status Overview</h3>
                    <div className="status-item">
                      <span>Battery Status:</span>
                      <span>{batteryStatus !== null ? `${batteryStatus}%` : 'Loading...'}</span>
                    </div>
                    <div className="status-item">
                      <span>WiFi Status:</span>
                      <span>{wifiStatus}</span>
                    </div>
                  </div>
                </>
              }
            />
            {/* Weitere Routen können hier hinzugefügt werden */}
          </Routes>
        </div>
      </div>
    </div>
  );
};

export default Home;
