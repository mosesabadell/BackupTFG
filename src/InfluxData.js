import React, { useEffect, useState } from 'react';
import axios from 'axios';

const GrafanaData = () => {
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const token = 'EL_TEU_TOKEN_D_API';
      const datasourceId = '1'; // Reemplaça amb el teu ID
      const query = 'SELECT * FROM "nom_de_la_mètrica" LIMIT 10'; // Ajusta la consulta segons les teves necessitats

      try {
        const response = await axios.get(
          `http://localhost:3000/api/datasources/proxy/${datasourceId}/query`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            },
            params: {
              q: query,
              db: 'dadesaltaveu' // El nom de la teva base de dades InfluxDB
            }
          }
        );

        // Processa les dades segons el format retornat
        setMetrics(response.data.results);
      } catch (error) {
        console.error('Error al carregar les dades de Grafana', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h2>Dades de les Mètriques</h2>
      <pre>{JSON.stringify(metrics, null, 2)}</pre>
    </div>
  );
};

export default GrafanaData;
