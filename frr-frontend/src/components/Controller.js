import React, { useState, useEffect, useRef } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import './Controller.css';

const Controller = () => {
  const [isControlActive, setIsControlActive] = useState(false);
  const [pressedKey, setPressedKey] = useState(null);
  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = new WebSocket('ws://192.168.178.24:5000/send-movement-input');

    socketRef.current.onopen = () => {
      console.log('WebSocket-Verbindung hergestellt');
    };

    socketRef.current.onclose = () => {
      console.log('WebSocket-Verbindung geschlossen');
    };

    return () => {
      socketRef.current.close();
    };
  }, []);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (isControlActive && socketRef.current) {
        socketRef.current.send(JSON.stringify({ type: 'keydown', key: event.key }));
        setPressedKey(event.key);
      }
    };

    const handleKeyUp = (event) => {
      if (isControlActive && socketRef.current) {
        socketRef.current.send(JSON.stringify({ type: 'keyup', key: event.key }));
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
          <div className="controller-header">
            <h2>Controller</h2>
          </div>
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
          </div>
          <div className="control-toggle">
            <button 
              onClick={toggleControl}
              className={isControlActive ? 'active' : ''}
            >
              {isControlActive ? 'Deaktivieren' : 'Aktivieren'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Controller;
