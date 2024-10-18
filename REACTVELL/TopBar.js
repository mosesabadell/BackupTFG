import React from 'react';

const TopBar = () => {
  return (
    <div className="top-bar">
      <div className="zoom-controls">
        <button className="zoom-button">🔍+</button>
        <button className="zoom-button">🔍-</button>
      </div>
    </div>
  );
};

export default TopBar;
