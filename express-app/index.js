const express = require('express');
const app = express();

const PORT = process.env.PORT || 4567;

app.get('/', (req, res) => {
  res.send('Hello from Express running in Docker!');
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});