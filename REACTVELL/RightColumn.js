import React from 'react';

const RightColumn = ({ speaker }) => {
  const handleDownload = () => {
    if (speaker) {
      // Lógica para descargar el historial del altavoz
      alert(`Descargando historial del altavoz: ${speaker.name}`);
    }
  };

  return (
    <div>
      <h2>Descargar Historial</h2>
      <button onClick={handleDownload} disabled={!speaker}>
        {speaker ? `Descargar Historial de ${speaker.name}` : 'Selecciona un altavoz'}
      </button>
    </div>
  );
};

export default RightColumn;
