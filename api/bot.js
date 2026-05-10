import { Bot, webhookCallback } from 'grammy'

const bot = new Bot(process.env.BOT_TOKEN)
const startTime = Date.now()

bot.command('ping', async (ctx) => {
  const t1 = Date.now()
  const uptime = Date.now() - startTime

  const days = Math.floor(uptime / 86400000)
  const hours = Math.floor((uptime % 86400000) / 3600000)
  const minutes = Math.floor((uptime % 3600000) / 60000)
  const seconds = Math.floor((uptime % 60000) / 1000)

  let uptimeStr
  if (days > 0) {
    uptimeStr = `${days} hari ${hours} jam`
  } else if (hours > 0) {
    uptimeStr = `${hours} jam ${minutes} menit`
  } else if (minutes > 0) {
    uptimeStr = `${minutes} menit ${seconds} detik`
  } else {
    uptimeStr = `${seconds} detik`
  }

  const msg = await ctx.reply('Mengukur...')
  const latency = Date.now() - t1

  let label
  if (latency < 200) label = 'Kecil'
  else if (latency < 500) label = 'Sedang'
  else label = 'Besar (Lag)'

  await ctx.api.editMessageText(
    ctx.chat.id,
    msg.message_id,
    `Ping: ${latency}ms (${label})\nUptime: ${uptimeStr}`
  )
})

export default webhookCallback(bot, 'http')
