import express from 'express';
import { exec } from 'child_process';
const app = express();

app.use(express.json());

app.post('/webhook', (req, res) => {
    console.log('🔄 Update bot terdeteksi...');
    
    // Command: masuk folder, tarik kode, install deps, lalu restart bot
    const command = 'cd ~/bot-hp && git pull origin master && npm install && pm2 restart bot-hp';

    exec(command, (err, stdout, stderr) => {
        if (err) return res.status(500).send('Deploy Gagal');
        console.log('✅ Bot berhasil di-update dan di-restart!');
        res.status(200).send('OK');
    });
});

app.listen(8080);
