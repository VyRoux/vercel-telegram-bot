import { Bot, webhookCallback } from 'grammy'

const bot = new Bot(process.env.BOT_TOKEN)

bot.command('ping', async (ctx) => {
  await ctx.reply('pong!')
})

export default webhookCallback(bot, 'http')
