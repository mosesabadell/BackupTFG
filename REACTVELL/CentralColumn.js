import React, { useEffect, useRef } from 'react';
import { Chart } from 'chart.js/auto';

const CentralColumn = ({ speaker }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (!chartRef.current) return;

    const ctx = chartRef.current.getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['00:00', '00:30', '01:00', '01:30', '02:00'],
        datasets: [
          {
            label: 'Nivel de Señal',
            data: [20, 50, 30, 80, 60],
            borderColor: 'green',
            backgroundColor: 'rgba(0, 255, 0, 0.2)',
          },
        ],
      },
      options: {
        scales: {
          x: {
            title: {
              display: true,
              text: 'Tiempo (min)',
            },
          },
          y: {
            title: {
              display: true,
              text: 'Nivel',
            },
          },
        },
      },
    });

    return () => chart.destroy(); // Limpieza al desmontar
  }, [speaker]);

  return (
    <div>
      <h2>Métricas de {speaker ? speaker.name : 'Altavoz'}</h2>
      <canvas ref={chartRef} width="400" height="200"></canvas>
    </div>
  );
};

export default CentralColumn;
