const WEBHOOK_URL = process.env.WEBHOOK_URL
const BOT_TOKEN = process.env.BOT_TOKEN

if (!WEBHOOK_URL || !BOT_TOKEN) {
  console.error('Missing WEBHOOK_URL or BOT_TOKEN in environment')
  process.exit(1)
}

const url = `https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${WEBHOOK_URL}`
const res = await fetch(url)
const data = await res.json()

console.log(data.description || JSON.stringify(data))
