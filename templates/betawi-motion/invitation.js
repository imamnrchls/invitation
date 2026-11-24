import wedding from '../../wedding.js'

const $ = (id) => document.getElementById(id)
const asset = (file) => new URL('../../assets/' + encodeURIComponent(file), import.meta.url).href
const own = (file) => new URL('./assets/' + file, import.meta.url).href
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag)
  for (const [key, value] of Object.entries(props)) {
    if (key === 'class') node.className = value
    else if (key === 'text') node.textContent = value
    else if (key.startsWith('data-') || key.startsWith('aria-') || key === 'style') node.setAttribute(key, value)
    else node[key] = value
  }
  node.append(...children.filter(Boolean))
  return node
}
const icon = (id, cls = 'ico') => {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.setAttribute('class', cls)
  svg.setAttribute('aria-hidden', 'true')
  const use = document.createElementNS('http://www.w3.org/2000/svg', 'use')
  use.setAttribute('href', '#i-' + id)
  svg.append(use)
  return svg
}

/* ---------- content ---------- */
document.title = wedding.names + ' | Undangan Pernikahan'
document.querySelector('meta[name="description"]').content = 'Undangan pernikahan ' + wedding.names + '.'
document.querySelectorAll('[data-names]').forEach((node) => { node.textContent = wedding.names })
document.querySelectorAll('[data-short-date]').forEach((node) => { node.textContent = wedding.shortDate || wedding.date })
const firstNames = wedding.couple.map(({ name }) => name.split(/\s+/)[0])
document.querySelectorAll('[data-name]').forEach((node) => { node.textContent = firstNames[node.dataset.name] || '' })

// Split the opening names into letters so they can arrive one by one.
{
  let index = 0
  const names = document.getElementById('hero-names')
  const walker = document.createTreeWalker(names, NodeFilter.SHOW_TEXT)
  const texts = []
  while (walker.nextNode()) texts.push(walker.currentNode)
  for (const text of texts) {
    const letters = document.createDocumentFragment()
    for (const char of text.textContent) {
      const span = document.createElement('span')
      span.className = 'ch'
      span.style.setProperty('--i', index++)
      span.textContent = char
      letters.append(span)
    }
    text.replaceWith(letters)
  }
  names.setAttribute('aria-label', names.textContent.replace(/\s+/g, ' ').trim())
}

const photos = wedding.photos || []
const photoAt = (index) => photos[index % Math.max(photos.length, 1)]
const setPhoto = (selector, photo) => document.querySelectorAll(selector).forEach((img) => {
  if (!photo) return img.closest('figure')?.setAttribute('hidden', '')
  img.src = asset(photo.file)
  img.alt = photo.alt
})
setPhoto('[data-cover-photo]', wedding.coverPhoto ? { file: wedding.coverPhoto, alt: wedding.names } : photoAt(0))
setPhoto('[data-feature-photo]', photoAt(0))
setPhoto('[data-story-photo]', photoAt(1))
setPhoto('[data-closing-photo]', photoAt(0))

if (wedding.quote) {
  $('quote-text').textContent = wedding.quote.text
  $('quote-source').textContent = wedding.quote.source || ''
} else {
  $('quote-text').textContent = wedding.blessing || ''
}
$('invite-line').textContent = wedding.inviteLine || wedding.welcome
$('closing-text').textContent = wedding.closing || wedding.welcome

wedding.couple.forEach((partner, index) => {
  const bride = index === 0
  const figure = el('figure', { class: 'oval', 'data-reveal': bride ? 'right' : 'left' })
  if (partner.portrait) figure.append(el('img', { class: 'photo', src: asset(partner.portrait), alt: partner.name, loading: 'lazy' }))
  figure.append(
    el('img', { class: 'frame', src: own('frame.webp'), alt: '' }),
    el('img', { class: 'bouquet', src: own('bouquet.webp'), alt: '' }),
  )
  const text = el('div', { class: 'partner-text', 'data-reveal': 'up', style: '--d:.25s' },
    el('h3', { text: partner.name }),
    partner.family && el('p', { text: partner.family }),
  )
  const handle = partner.instagram?.replace(/^@/, '').trim()
  if (handle && /^[\w.]{1,30}$/.test(handle)) {
    const link = el('a', { class: 'social', href: 'https://www.instagram.com/' + handle + '/', target: '_blank', rel: 'noopener', 'aria-label': 'Instagram ' + partner.name })
    link.append(icon('camera', ''))
    text.append(link)
  }
  $('couple').append(el('article', { class: 'partner ' + (bride ? 'bride' : 'groom') }, figure, text))
  if (bride && wedding.couple.length > 1) $('couple').append(el('p', { class: 'amp-script', 'data-reveal': 'zoom', text: '&', 'aria-hidden': 'true' }))
})

/* ---------- events ---------- */
if (wedding.attendanceNote) {
  $('attendance-note').textContent = wedding.attendanceNote
  $('attendance-note').hidden = false
}
const mapLink = (event) => {
  const pin = event.mapPin && /^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$/.test(event.mapPin)
  return 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(pin ? event.mapPin : event.mapQuery || event.venue + ', ' + event.address)
}
const stamp = (time) => new Date(time).toISOString().replace(/[-:]|\.\d{3}/g, '')
for (const event of wedding.events) {
  const map = el('a', { class: 'pill small', href: mapLink(event), target: '_blank', rel: 'noopener', 'aria-label': 'Lokasi acara ' + event.title + ' di Google Maps' })
  map.append(icon('pin', ''), 'Lokasi Acara')
  const article = el('article', { class: 'event' },
    el('h3', { text: event.title }),
    el('hr'),
    el('p', { class: 'when', text: event.date }),
    el('p', { class: 'time', text: 'Pukul: ' + event.time }),
    el('address', {}, event.venue, el('br'), event.address),
    map,
  )
  const start = Date.parse(event.startsAt)
  const end = Date.parse(event.endsAt)
  if (Number.isFinite(start) && end > start) {
    article.append(el('a', {
      class: 'cal', target: '_blank', rel: 'noopener', text: 'Simpan ke Google Calendar',
      href: 'https://calendar.google.com/calendar/render?' + new URLSearchParams({
        action: 'TEMPLATE', text: event.title + ' · ' + wedding.names, dates: stamp(start) + '/' + stamp(end), location: event.venue + ', ' + event.address,
      }),
    }))
  }
  $('events').append(article)
}

/* ---------- countdown ---------- */
const starts = wedding.events.map(({ startsAt }) => Date.parse(startsAt)).filter(Number.isFinite)
const target = Math.min(...starts)
if (Number.isFinite(target) && target > Date.now()) {
  const box = $('countdown')
  box.hidden = false
  const tick = () => {
    const left = Math.max(0, Math.floor((target - Date.now()) / 1000))
    const parts = { days: Math.floor(left / 86400), hours: Math.floor(left / 3600) % 24, minutes: Math.floor(left / 60) % 60, seconds: left % 60 }
    for (const [unit, value] of Object.entries(parts)) box.querySelector(`[data-unit="${unit}"]`).textContent = value
    if (!left) clearInterval(timer)
  }
  const timer = setInterval(tick, 1000)
  tick()
}

/* ---------- story & gallery ---------- */
for (const chapter of wedding.story || []) {
  $('chapters').append(el('article', { class: 'chapter', 'data-reveal': 'up' },
    el('h3', { text: chapter.title }),
    chapter.date && el('span', { text: chapter.date }),
    el('p', { text: chapter.text }),
  ))
}
$('cerita').hidden = !wedding.story?.length
$('galeri').hidden = !photos.length

const viewer = $('viewer')
let current = 0
let opener
function show(index) {
  current = (index + photos.length) % photos.length
  $('viewer-img').src = asset(photos[current].file)
  $('viewer-img').alt = photos[current].alt
  $('viewer-pos').textContent = current + 1 + ' / ' + photos.length
}
photos.forEach((photo, index) => {
  const link = el('a', { href: asset(photo.file), 'aria-label': 'Lihat foto: ' + photo.alt, 'data-reveal': index % 2 ? 'right' : 'left', style: `--d:${(index % 4) * 0.08}s` },
    el('img', { src: asset(photo.file), alt: photo.alt, loading: 'lazy' }))
  link.addEventListener('click', (event) => {
    if (typeof viewer.showModal !== 'function' || event.metaKey || event.ctrlKey) return
    event.preventDefault()
    opener = link
    show(index)
    viewer.showModal()
  })
  $('photos').append(link)
})
$('viewer-close').addEventListener('click', () => viewer.close())
$('viewer-prev').addEventListener('click', () => show(current - 1))
$('viewer-next').addEventListener('click', () => show(current + 1))
viewer.addEventListener('click', (event) => { if (event.target === viewer) viewer.close() })
viewer.addEventListener('close', () => opener?.focus({ preventScroll: true }))
viewer.addEventListener('keydown', (event) => {
  if (event.key === 'ArrowLeft') show(current - 1)
  if (event.key === 'ArrowRight') show(current + 1)
})

/* ---------- stream & gift ---------- */
if (wedding.stream || wedding.streamUrl) {
  $('stream').hidden = false
  $('stream-text').textContent = wedding.stream || 'Saksikan pernikahan kami secara langsung melalui tautan berikut.'
  const first = wedding.events[0]
  $('stream-meta').textContent = first ? first.date + ' · ' + first.time : ''
  if (/^https:\/\//.test(wedding.streamUrl || '')) {
    $('stream-link').href = wedding.streamUrl
    $('stream-link').hidden = false
  }
}

const accounts = wedding.giftAccounts || []
if (wedding.gift || accounts.length || wedding.giftAddress) {
  $('gift').hidden = false
  $('gift-text').textContent = wedding.gift || 'Bagi Bapak/Ibu/Saudara/i yang ingin mengirimkan hadiah, dapat melalui tautan di bawah ini.'
  const list = $('gift-list')
  accounts.forEach((account, index) => {
    const copy = el('button', { class: 'copy', type: 'button', text: 'Salin', 'aria-label': 'Salin nomor ' + account.bank })
    copy.addEventListener('click', async () => {
      const digits = account.number.replace(/\s+/g, '')
      try {
        await navigator.clipboard.writeText(digits)
        copy.textContent = 'Tersalin'
        copy.classList.add('done')
      } catch {
        copy.textContent = digits
      }
      setTimeout(() => { copy.textContent = 'Salin'; copy.classList.remove('done') }, 2200)
    })
    list.append(el('div', { class: 'bank-card', style: `--i:${index}` },
      el('span', { class: 'bank', text: account.bank }),
      el('span', { class: 'chip', 'aria-hidden': 'true' }),
      el('span', { class: 'number', text: account.number }),
      el('span', { class: 'holder', text: account.holder }),
      copy,
    ))
  })
  if (wedding.giftAddress) {
    const card = el('div', { class: 'address-card', style: `--i:${accounts.length}` })
    card.append(icon('gift', ''), el('strong', { text: 'Kirim Hadiah' }),
      el('p', { text: 'Nama penerima: ' + wedding.giftAddress.recipient }),
      el('p', { text: wedding.giftAddress.address }))
    list.append(card)
  }
  const toggle = $('gift-toggle')
  toggle.hidden = !list.children.length
  toggle.addEventListener('click', () => {
    const open = list.hidden
    list.hidden = !open
    toggle.setAttribute('aria-expanded', String(open))
  })
}

/* ---------- wishes (demo: stored on this device) ---------- */
const form = $('reply')
const status = $('reply-status')
const guest = new URLSearchParams(location.search).get('to')?.trim().slice(0, 80)
if (guest) {
  $('guest').textContent = guest
  form.elements.guest.value = guest
}
const storeKey = 'invitation:wishes:' + wedding.id
const readWishes = () => {
  try { return JSON.parse(localStorage.getItem(storeKey)) || [] } catch { return [] }
}
const ago = (time) => {
  const minutes = Math.max(0, Math.round((Date.now() - time) / 60000))
  if (minutes < 1) return 'baru saja'
  if (minutes < 60) return minutes + ' menit lalu'
  if (minutes < 1440) return Math.round(minutes / 60) + ' jam lalu'
  return Math.round(minutes / 1440) + ' hari lalu'
}
function renderWishes() {
  const wishes = readWishes()
  $('wish-total').textContent = wishes.length
  $('count-yes').textContent = wishes.filter((w) => w.attendance === 'yes').length
  $('count-no').textContent = wishes.filter((w) => w.attendance === 'no').length
  const list = $('wishes')
  list.replaceChildren()
  if (!wishes.length) list.append(el('li', { class: 'empty', text: 'Belum ada ucapan. Jadilah yang pertama.' }))
  for (const wish of wishes) {
    const who = el('span', { class: 'who' }, wish.name)
    who.append(icon('check', ''))
    list.append(el('li', {}, who, el('p', { text: wish.wish }), el('time', { dateTime: new Date(wish.at).toISOString(), text: ago(wish.at) })))
  }
}

if (wedding.demo) {
  $('demo-note').hidden = false
  renderWishes()
  form.addEventListener('submit', (event) => {
    event.preventDefault()
    const data = new FormData(form)
    const name = String(data.get('guest') || '').trim()
    const wish = String(data.get('wish') || '').trim()
    const attendance = data.get('attendance')
    if (!name || !wish || !attendance) {
      status.textContent = 'Mohon isi nama, ucapan, dan konfirmasi kehadiran.'
      form.querySelector(':invalid')?.focus()
      return
    }
    try {
      localStorage.setItem(storeKey, JSON.stringify([{ name, wish, attendance, at: Date.now() }, ...readWishes()].slice(0, 50)))
      status.textContent = 'Terima kasih atas ucapan dan doanya.'
      form.elements.wish.value = ''
      renderWishes()
    } catch {
      status.textContent = 'Ucapan tidak tersimpan. Penyimpanan perangkat tidak tersedia.'
    }
  })
} else {
  form.hidden = true
  document.querySelector('#rsvp .tally').hidden = true
  document.querySelector('#rsvp .count-line').hidden = true
  $('wishes').hidden = true
  const email = wedding.contactEmail?.trim()
  if (email && /^[^\s@?&#]+@[^\s@?&#]+\.[^\s@?&#]+$/.test(email)) {
    form.before(el('a', { class: 'pill small', href: 'mailto:' + email, text: 'Kirim ucapan lewat email' }))
  } else {
    form.before(el('p', { text: 'Formulir ucapan belum tersedia.' }))
  }
}

/* ---------- music ---------- */
let player
const music = $('music')
if (wedding.music) {
  player = new Audio(asset(wedding.music))
  player.loop = true
  player.preload = 'none'
  music.hidden = false
  const sync = () => {
    music.setAttribute('aria-pressed', String(!player.paused))
    music.setAttribute('aria-label', player.paused ? 'Putar musik' : 'Jeda musik')
  }
  player.addEventListener('play', sync)
  player.addEventListener('pause', sync)
  music.addEventListener('click', () => (player.paused ? player.play().catch(() => {}) : player.pause()))
}

/* ---------- reveals & parallax ---------- */
let observer
function watchReveals() {
  const nodes = document.querySelectorAll('[data-reveal]')
  if (reducedMotion || typeof IntersectionObserver !== 'function') {
    nodes.forEach((node) => node.classList.add('in'))
    return
  }
  observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue
      entry.target.classList.add('in')
      observer.unobserve(entry.target)
    }
  }, { threshold: .18, rootMargin: '0px 0px -6% 0px' })
  nodes.forEach((node) => observer.observe(node))
}

const hero = $('pembuka')
const depthNodes = [...hero.querySelectorAll('[data-depth]')]
let ticking = false
function parallax() {
  ticking = false
  const y = Math.min(scrollY, hero.offsetHeight)
  for (const node of depthNodes) node.style.transform = `translate3d(0, ${(y * Number(node.dataset.depth)).toFixed(1)}px, 0)`
}
if (!reducedMotion) {
  addEventListener('scroll', () => {
    if (!ticking) requestAnimationFrame(parallax)
    ticking = true
  }, { passive: true })
}

/* ---------- cover ---------- */
const cover = $('sampul')
const main = $('isi')
function begin() {
  document.body.classList.remove('locked')
  document.body.classList.add('opened')
  main.inert = false
  watchReveals()
}
const shortcut = location.hash && document.getElementById(location.hash.slice(1))
if (shortcut && shortcut !== cover) {
  cover.hidden = true
  begin()
  requestAnimationFrame(() => shortcut.scrollIntoView())
} else {
  main.inert = true
  scrollTo(0, 0)
  $('open-invitation').addEventListener('click', () => {
    player?.play().catch(() => {})
    begin()
    hero.focus({ preventScroll: true })
    if (reducedMotion) {
      cover.hidden = true
      return
    }
    cover.classList.add('leaving')
    cover.addEventListener('animationend', (event) => { if (event.target === cover) cover.hidden = true })
  }, { once: true })
}
