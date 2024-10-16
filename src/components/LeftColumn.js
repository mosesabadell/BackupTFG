import React from 'react';

const LeftColumn = ({ macAddresses, onSelectSpeaker }) => {
  return (
    <div>
      <h2>Select Channels to Monitor</h2>
      <div className="search-bar">
        <input type="text" placeholder="Search by MAC" />
      </div>
      <div className="selected-speakers">Selected Speakers: {macAddresses.length}</div>
      <div className="header-row">
        <span>Select</span>
        <span>Device MAC</span>
        <span>ID</span>
        <span>Tags</span>
      </div>
      <div className="speaker-list">
        {macAddresses.map((mac, index) => (
          <div className="speaker-item" key={index}>
            <input type="checkbox" onChange={() => onSelectSpeaker(mac)} />
            <span>{mac}</span>
            <span>{`ID-${index + 1}`}</span>
            <span>{`Tag-${index + 1}`}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LeftColumn;
