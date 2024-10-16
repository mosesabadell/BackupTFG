import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

const GrafanaData = () => {
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fa la petició al servidor backend
        const response = await axios.get('http://localhost:5000/api/metrics');
        // Processa les dades retornades pel backend
        const rawData = response.data.results[0].series[0];
        const columns = rawData.columns;
        const values = rawData.values;

        // Combina les columnes i els valors en un array d'objectes
        const chartData = values.map(entry => {
          const dataPoint = {};
          columns.forEach((col, index) => {
            dataPoint[col] = entry[index];
          });
          // Converteix el temps a un format llegible
          dataPoint.time = new Date(dataPoint.time).toLocaleTimeString();
          return dataPoint;
        });

        setMetrics(chartData);
      } catch (error) {
        console.error('Error al carregar les dades del servidor', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h2>Dades de les Mètriques</h2>
      <LineChart width={800} height={400} data={metrics}>
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="temperature" stroke="#8884d8" />
        <Line type="monotone" dataKey="nivell" stroke="#82ca9d" />
      </LineChart>
    </div>
  );
};

export default GrafanaData;
