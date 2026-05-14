import express from 'express';
import botHandler from './api/bot.js';

const app = express();
app.use(express.json());
app.post('/webhook', botHandler);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Bot aktif di port ${PORT}`));
