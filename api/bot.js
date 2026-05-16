import { Bot, webhookCallback } from 'grammy'

const bot = new Bot(process.env.BOT_TOKEN)
const startTime = Date.now()

const BAR_MAX = 1000
const BAR_SEGMENTS = 10

function bar(ms) {
  const n = Math.min(BAR_SEGMENTS, Math.max(0, Math.round((ms / BAR_MAX) * BAR_SEGMENTS)))
  return `[${'='.repeat(n)}${' '.repeat(BAR_SEGMENTS - n)}]`
}

function label(ms) {
  if (ms < 200) return 'Kecil'
  if (ms < 500) return 'Sedang'
  return 'Besar (Lag)'
}

function uptime(ms) {
  const d = Math.floor(ms / 86400000)
  const h = Math.floor((ms % 86400000) / 3600000)
  const m = Math.floor((ms % 3600000) / 60000)
  const s = Math.floor((ms % 60000) / 1000)
  if (d > 0) return `${d} hari ${h} jam`
  if (h > 0) return `${h} jam ${m} menit`
  if (m > 0) return `${m} menit ${s} detik`
  return `${s} detik`
}

bot.command('ping', async (ctx) => {
  const t1 = Date.now()
  const msg = await ctx.reply('Mengukur...')
  const ms = Date.now() - t1
  await ctx.api.editMessageText(ctx.chat.id, msg.message_id,
    `Latency: ${ms}ms ${bar(ms)} ${label(ms)}\nOnline : ${uptime(Date.now() - startTime)}`)
})

bot.command('info', async (ctx) => {
  const u = ctx.from
  const c = ctx.chat
  await ctx.reply(
    `User  : ${u.first_name}${u.last_name ? ` ${u.last_name}` : ''}\n` +
    `ID    : ${u.id}\n` +
    `Username : ${u.username ? `@${u.username}` : '-'}\n` +
    `Chat  : ${c.type} (#${c.id})`)
})

bot.command('help', async (ctx) => {
  await ctx.reply(
    `Daftar perintah:\n\n` +
    `/ping  - Cek latensi & uptime bot\n` +
    `/info  - Info akun Telegram kamu\n` +
    `/help  - Bantuan ini`)
})

export default bot
