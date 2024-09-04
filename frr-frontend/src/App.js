import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Home from './components/Home';
import Camera from './components/Camera'
import Controller from './components/Controller'
import './App.css';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/home" element={<Home />} />
        <Route path="/camera" element={<Camera />} />
        <Route path="/controller" element={<Controller />} />
        <Route path="/" element={<Navigate to="/home" />} />
      </Routes>
    </Router>
  );
};

export default App;
