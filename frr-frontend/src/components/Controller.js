import React, { useState, useEffect, useRef } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import './Controller.css';

const Controller = () => {
  const [isControlActive, setIsControlActive] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    // WebSocket-Verbindung herstellen, wenn die Komponente montiert wird
    socketRef.current = new WebSocket('ws://192.168.178.24:5000/send-movement-input');

    socketRef.current.onopen = () => {
      console.log('WebSocket-Verbindung hergestellt');
    };

    socketRef.current.onclose = () => {
      console.log('WebSocket-Verbindung geschlossen');
    };

    return () => {
      // WebSocket-Verbindung schließen, wenn die Komponente unmontiert wird
      socketRef.current.close();
    };
  }, []);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (isControlActive && socketRef.current) {
        socketRef.current.send(JSON.stringify({ type: 'keydown', key: event.key }));
      }
    };

    const handleKeyUp = (event) => {
      if (isControlActive && socketRef.current) {
        socketRef.current.send(JSON.stringify({ type: 'keyup', key: event.key }));
      }
    };

    if (isControlActive) {
      window.addEventListener('keydown', handleKeyDown);
      window.addEventListener('keyup', handleKeyUp);
    } else {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
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
          <Routes>
            <Route
              path="/"
              element={
                <>
                  <h2>Controller</h2>
                  <button onClick={toggleControl}>
                    {isControlActive ? 'Deaktivieren' : 'Aktivieren'}
                  </button>
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

export default Controller;
