import simpleGit from 'simple-git'
import { execSync } from 'child_process'
import 'dotenv/config'

const git = simpleGit()
const INTERVAL = 5 * 60 * 1000
const BRANCH = 'master'

async function checkAndUpdate() {
  try {
    await git.fetch('origin', BRANCH)
    const status = await git.status()
    if (status.behind > 0) {
      console.log(`[auto-update] ${status.behind} commit(s) di belakang. Pulling...`)
      await git.pull('origin', BRANCH)
      console.log('[auto-update] Pull sukses. Restart bot...')
      execSync('pm2 restart bot-hp', { stdio: 'inherit' })
      console.log('[auto-update] Bot berhasil restart.')
    } else {
      console.log(`[auto-update] Tidak ada update. (${new Date().toLocaleTimeString()})`)
    }
  } catch (err) {
    console.error('[auto-update] Error:', err.message)
  }
}

console.log(`[auto-update] Mulai pantau branch ${BRANCH}, interval ${INTERVAL / 1000}s`)
checkAndUpdate()
setInterval(checkAndUpdate, INTERVAL)
