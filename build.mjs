import { cp, rm } from 'node:fs/promises'

const [event = 'ayu-raka'] = process.argv.slice(2)
if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(event)) throw new Error('Use a lowercase event slug.')

const output = new URL('./dist/', import.meta.url)
const from = (path) => new URL(path, import.meta.url)
const to = (path) => new URL(path, output)
const site = './templates/olive-motion/'
const eventPath = './events/' + event + '/'

await rm(output, { recursive: true, force: true })
await cp(from(site + 'index.html'), to('index.html'))
for (const file of ['style.css', 'invitation.js']) {
  await cp(from(site + file), to('templates/olive-motion/' + file))
}
await cp(from(site + 'assets/'), to('templates/olive-motion/assets/'), { recursive: true })
await cp(from(eventPath + 'wedding.js'), to('wedding.js'))
await cp(from(eventPath + 'assets/'), to('assets/'), { recursive: true })
