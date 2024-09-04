import React, { useState, useEffect, useRef } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import './Controller.css';

const Controller = () => {
  const [imageSrc, setImageSrc] = useState(null);
  const [isControlActive, setIsControlActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [pressedKey, setPressedKey] = useState(null);
  const [isBlocked, setIsBlocked] = useState(false); // State für den Blockierstatus

  const wsCameraRef = useRef(null);
  const wsControlRef = useRef(null);

  // Start WebSocket für die Kamera
  const startCameraWebSocket = () => {
    if (!isConnected) {
      wsCameraRef.current = new WebSocket('ws://192.168.178.24:5000');

      wsCameraRef.current.onopen = () => {
        setIsConnected(true);
        setErrorMessage(null);
      };

      wsCameraRef.current.onmessage = (event) => {
        if (event.data === "No picture") {
          setErrorMessage('No picture available.');
          setIsControlActive(false); 
        } else {
          const imageSrc = `data:image/jpeg;base64,${event.data}`;
          setImageSrc(imageSrc);
          setErrorMessage(null);
        }
      };

      wsCameraRef.current.onerror = () => {
        setErrorMessage('WebSocket error observed.');
      };

      wsCameraRef.current.onclose = () => {
        setIsConnected(false);
        setImageSrc(null);
        setErrorMessage('WebSocket connection closed.');
      };
    }
  };

  const stopCameraWebSocket = () => {
    if (wsCameraRef.current) {
      wsCameraRef.current.close();
    }
  };

  // Start WebSocket für die Steuerung
  useEffect(() => {
    wsControlRef.current = new WebSocket('ws://192.168.178.24:5001');

    wsControlRef.current.onopen = () => {
      console.log('WebSocket für die Steuerung etabliert');
    };

    wsControlRef.current.onclose = () => {
      console.log('WebSocket für die Steuerung geschlossen');
      setIsControlActive(false);
    };

    wsControlRef.current.onerror = () => {
      setIsControlActive(false);
    };

    return () => {
      if (wsControlRef.current) {
        wsControlRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (isControlActive && wsControlRef.current) {
        wsControlRef.current.send(JSON.stringify({ type: 'keydown', key: event.key }));
        setPressedKey(event.key);
      }
    };

    const handleKeyUp = (event) => {
      if (isControlActive && wsControlRef.current) {
        wsControlRef.current.send(JSON.stringify({ type: 'keyup', key: event.key }));
        setPressedKey(null);
      }
    };

    if (isControlActive) {
      window.addEventListener('keydown', handleKeyDown);
      window.addEventListener('keyup', handleKeyUp);
    } else {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      setPressedKey(null);
    }

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isControlActive]);

  const toggleControl = () => {
    setIsControlActive((prevState) => !prevState);
  };

  return (
    <div className="controller-container">
      <Sidebar />
      <div className="controller-content">
        <Header />
        <div className="controller-main">
          <h2>Controller</h2>
          <div className="controller-body">
            <div className="controller-camera-box">
              {errorMessage ? (
                <p className="error-message">{errorMessage}</p>
              ) : imageSrc ? (
                <img src={imageSrc} alt="Camera Stream" />
              ) : (
                <p>No Connection established</p>
              )}
              <div className="controller-camera-controls">
                <button onClick={startCameraWebSocket} disabled={isConnected}>
                  Start Connection
                </button>
                <button onClick={stopCameraWebSocket} disabled={!isConnected}>
                  Stop Connection
                </button>
              </div>
            </div>

            <div className="controller-arrow-box">
              <div className="arrow-key-container">
                <div className={`arrow-key ${pressedKey === 'ArrowUp' ? 'active' : ''}`}>
                  &#9650;
                </div>
                <div className="arrow-key-row">
                  <div className={`arrow-key ${pressedKey === 'ArrowLeft' ? 'active' : ''}`}>
                    &#9664;
                  </div>
                  <div className={`arrow-key ${pressedKey === 'ArrowDown' ? 'active' : ''}`}>
                    &#9660;
                  </div>
                  <div className={`arrow-key ${pressedKey === 'ArrowRight' ? 'active' : ''}`}>
                    &#9654;
                  </div>
                </div>
                <div className={`space-bar ${pressedKey === 'Shift' ? 'active' : ''}`}>
                  Shift
                </div>
                <div className="control-toggle">
                  <button 
                    onClick={toggleControl}
                    className={isControlActive ? 'active' : ''}
                  >
                    {isControlActive ? 'Deactivate' : 'Activate'}
                  </button>
                </div>
              </div>

              {/* Block Status Box unterhalb der Steuerung */}
              <div className="controller-block-status">
                <p>Robot Block Status: {isBlocked ? 'Blocked' : 'Not Blocked'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Controller;
