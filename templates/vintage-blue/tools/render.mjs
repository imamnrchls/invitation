// Rasterise the SVG layers from draw.py into transparent PNGs at 2x.
// Usage: node render.mjs <svg-dir> <png-dir>
import { readdir, readFile, mkdir } from 'node:fs/promises'
import { join } from 'node:path'
import { createRequire } from 'node:module'

// Playwright is resolved from the working directory or a global install.
const { chromium } = createRequire(process.cwd() + '/')('playwright')

const [from = 'svg', to = 'png'] = process.argv.slice(2)
await mkdir(to, { recursive: true })
const browser = await chromium.launch()
for (const file of (await readdir(from)).filter((name) => name.endsWith('.svg'))) {
  const markup = await readFile(join(from, file), 'utf8')
  const [, width, height] = markup.match(/width="(\d+)" height="(\d+)"/)
  const page = await browser.newPage({ viewport: { width: +width, height: +height }, deviceScaleFactor: 2 })
  await page.setContent('<style>html,body{margin:0;background:transparent}svg{display:block}</style>' + markup)
  await page.screenshot({ path: join(to, file.replace('.svg', '.png')), omitBackground: true })
  await page.close()
  console.log(file)
}
await browser.close()
