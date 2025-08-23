import express from 'express';
import { startKafka } from './kafka.js';
const app = express();

app.use(express.json());

app.listen(3000, () => {
    startKafka();
    console.log('Server running on port 3000');
});