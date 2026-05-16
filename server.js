import 'dotenv/config';
import bot from './api/bot.js';

bot.start();
console.log('Bot running with long polling...');
