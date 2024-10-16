const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();

// Configura CORS per permetre peticions des del teu frontend React
app.use(cors());

app.get('/api/metrics', async (req, res) => {
  const token = 'eyJrIjoiNHFKeXpoZGExQjJrUk5hU2ZGYThKckdUNGt2MmJMOVQiLCJuIjoicmVhY3QtYXBwIiwiaWQiOjF9';
  const datasourceId = 'caRyqjzNz';
  const query = 'SELECT * FROM "Temperature" LIMIT 10';

  try {
    const response = await axios.get(
      `http://localhost:3000/api/datasources/proxy/${datasourceId}/query`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {
          q: query,
          db: 'dadesaltaveu'
        }
      }
    );

    res.json(response.data);
  } catch (error) {
    console.error('Error al carregar les dades de Grafana', error);
    res.status(500).send('Error al carregar les dades');
  }
});

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Servidor intermediari executant-se al port ${PORT}`);
});
