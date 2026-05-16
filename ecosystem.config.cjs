module.exports = {
  apps: [
    {
      name: 'bot-hp',
      script: 'server.js',
      env: { NODE_ENV: 'production' },
    },
    {
      name: 'auto-update',
      script: 'auto-update.js',
      env: { NODE_ENV: 'production' },
    },
  ],
}
