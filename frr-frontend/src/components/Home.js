import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import './Home.css';

const Home = () => {
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
                  <h2>Welcome to the Dashboard</h2>
                  <p>This is the home page content. Replace this with the actual content you want to display.</p>
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
