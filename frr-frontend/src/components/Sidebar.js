import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHome, faCog, faBars, faPlusCircle, faCamera } from '@fortawesome/free-solid-svg-icons';
import './Sidebar.css';

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className={`dashboard-sidebar ${isOpen ? 'open' : 'closed'}`}>
      <button className="sidebar-toggle" onClick={toggleSidebar}>
        <FontAwesomeIcon icon={faBars} />
      </button>
      <ul>
        <li>
          <Link to="/home">
            <FontAwesomeIcon icon={faHome} className="sidebar-icon" />
            {isOpen && <span className="sidebar-text">Home</span>}
          </Link>
        </li>
        <li>
          <Link to="/camera">
            <FontAwesomeIcon icon={faCamera} className="sidebar-icon" />
            {isOpen && <span className="sidebar-text">Camera</span>}
          </Link>
        </li>
        <li>
          <Link to="/create">
            <FontAwesomeIcon icon={faPlusCircle} className="sidebar-icon" />
            {isOpen && <span className="sidebar-text">Create</span>}
          </Link>
        </li>
        <li className="settings">
          <Link to="/settings">
            <FontAwesomeIcon icon={faCog} className="sidebar-icon" />
            {isOpen && <span className="sidebar-text">Settings</span>}
          </Link>
        </li>
      </ul>
    </div>
  );
};

export default Sidebar;
