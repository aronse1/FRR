import React from 'react';
import './Header.css';

const Header = () => {


  return (
    <header className="dashboard-header">
      <div className="left-spacer"></div>
      <div className="logo-container">
        <img src={`${process.env.PUBLIC_URL}/image.png`} alt="Cryptoident Logo" className="header-logo" />
      </div>
    </header>
  );
};

export default Header;
