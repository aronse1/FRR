import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import './Camera.css';

const Camera = () => {
  const [imageSrc, setImageSrc] = useState(null);

  useEffect(() => {
    // Erstelle eine WebSocket-Verbindung
    const ws = new WebSocket('ws://localhost:5000/recieve-camera');

    // Event-Handler für eingehende Nachrichten
    ws.onmessage = (event) => {
      // Erwarte, dass die Daten als Blob (Binärdaten) empfangen werden
      const reader = new FileReader();

      reader.onloadend = () => {
        // Konvertiere die Blob-Daten in ein Base64-URL
        setImageSrc(reader.result);
      };

      // Lies die empfangenen Daten als Data URL
      reader.readAsDataURL(event.data);
    };

    // WebSocket schließen, wenn die Komponente unmontiert wird
    return () => {
      ws.close();
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
                    {imageSrc ? (
                      <img src={imageSrc} alt="Camera Stream" />
                    ) : (
                      <p>Loading...</p>
                    )}
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
