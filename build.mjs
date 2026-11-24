import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises'

const [event = 'ayu-raka', template = 'betawi-motion'] = process.argv.slice(2)
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
if (template === 'olive-motion') {
  const base = './templates/vintage-blue/'
  const markup = await readFile(from(base + 'index.html'), 'utf8')
  const style = await readFile(from(base + 'style.css'), 'utf8')
  const theme = await readFile(from(templatePath + 'style.css'), 'utf8')
  await writeFile(to('index.html'), markup
    .replaceAll('/vintage-blue/', '/olive-motion/')
    .replaceAll('/castle.webp', '/pavilion.webp')
    .replace('#6f8fb8', '#303b28')
    .replace(/&family=Crimson\+Pro[^"]+/, '&family=DM+Sans:wght@400;500;600;700&display=swap'))
  await writeFile(to('templates/olive-motion/style.css'), style + '\n' + theme)
  await cp(from(base + 'invitation.js'), to('templates/olive-motion/invitation.js'))
} else {
  await cp(from(templatePath + 'index.html'), to('index.html'))
  for (const file of ['style.css', 'invitation.js']) {
    await cp(from(templatePath + file), to('templates/' + template + '/' + file))
  }
}
try {
  await cp(from(templatePath + 'assets/'), to('templates/' + template + '/assets/'), { recursive: true })
} catch (error) {
  if (error.code !== 'ENOENT') throw error
}
if (template === 'olive-motion') {
  await cp(from('./templates/olive-garden/assets/garden-landscape.webp'), to('templates/olive-motion/assets/backdrop.webp'))
}
await cp(from(eventPath + 'wedding.js'), to('wedding.js'))
await cp(from(eventPath + 'assets/'), to('assets/'), { recursive: true })
