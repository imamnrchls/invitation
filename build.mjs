import { cp, mkdir, rm } from 'node:fs/promises'

const [event = 'ayu-raka', template = 'vintage-blue'] = process.argv.slice(2)
for (const slug of [event, template]) {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) throw new Error('Use lowercase event and template slugs.')
}

const output = new URL('./dist/', import.meta.url)
const from = (path) => new URL(path, import.meta.url)
const to = (path) => new URL(path, output)
const templatePath = './templates/' + template + '/'
const eventPath = './events/' + event + '/'

await rm(output, { recursive: true, force: true })
await mkdir(to('templates/' + template + '/'), { recursive: true })
await cp(from(templatePath + 'index.html'), to('index.html'))
for (const file of ['style.css', 'invitation.js']) {
  await cp(from(templatePath + file), to('templates/' + template + '/' + file))
}
try {
  await cp(from(templatePath + 'assets/'), to('templates/' + template + '/assets/'), { recursive: true })
} catch (error) {
  if (error.code !== 'ENOENT') throw error
}
await cp(from(eventPath + 'wedding.js'), to('wedding.js'))
await cp(from(eventPath + 'assets/'), to('assets/'), { recursive: true })
