import React, { useState, useEffect, useRef } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import './Camera.css';

const Camera = () => {
  const [imageSrc, setImageSrc] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [noPictureReceived, setNoPictureReceived] = useState(false);
  const wsRef = useRef(null); // Use useRef to store the WebSocket instance

  const resetState = () => {
    setImageSrc(null);
    setIsConnected(false);
    setErrorMessage(null);
    setNoPictureReceived(false);
  };

  const startWebSocket = () => {
    if (!isConnected) {
      wsRef.current = new WebSocket('ws://192.168.178.24:5000/receive-camera');

      wsRef.current.onopen = () => {
        console.log('WebSocket connection established');
        setIsConnected(true);
        setErrorMessage(null); // Clear any existing error message
        setNoPictureReceived(false); // Reset the "No picture" state
      };

      wsRef.current.onmessage = (event) => {
        if (event.data === "No picture") {
          console.log('No picture received, treating as connection lost.');
          setNoPictureReceived(true);
          setErrorMessage('No picture available.');
        } else {
          const reader = new FileReader();

          reader.onloadend = () => {
            setImageSrc(reader.result);
            setNoPictureReceived(false); // Reset the "No picture" state when a valid image is received
            setErrorMessage(null); // Clear any error message
          };

          reader.readAsDataURL(event.data);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error observed:', error);
        setErrorMessage('WebSocket error observed.');
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket is closed now.', event);
        resetState(); // Reset the entire state when the WebSocket is closed
      };
    } else if (noPictureReceived) {
      setErrorMessage('No picture available. Please try again later.');
    }
  };

  const stopWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close(); // Close the WebSocket connection
      resetState(); // Reset the entire state manually
    }
  };

  useEffect(() => {
    return () => {
      // Clean up the WebSocket connection when the component unmounts
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className="camera-container">
      <Sidebar />
      <div className="camera-content">
        <Header />
        <div className="camera-main">
          <Routes>
            <Route
              path="/"
              element={
                <>
                  <h2>Camera</h2>
                  <div className="camera-box">
                    {errorMessage ? (
                      <p className="error-message">{errorMessage}</p>
                    ) : imageSrc ? (
                      <img src={imageSrc} alt="Camera Stream" />
                    ) : (
                      <p>No Connection established</p>
                    )}
                  </div>
                  <div className="camera-controls">
                    <button onClick={startWebSocket} disabled={isConnected}>
                      Start Connection
                    </button>
                    <button onClick={stopWebSocket} disabled={!isConnected}>
                      Stop Connection
                    </button>
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

export default Camera;
