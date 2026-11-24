import wedding from '../../wedding.js'

const byId = (id) => document.getElementById(id)
const asset = (file) => new URL('../../assets/' + encodeURIComponent(file), import.meta.url)

function element(tag, text) {
  const node = document.createElement(tag)
  node.textContent = text
  return node
}

document.title = wedding.names + ' | Undangan Pernikahan'
document.querySelector('meta[name="description"]').content = 'Undangan pernikahan ' + wedding.names + '.'
document.querySelectorAll('[data-names]').forEach((node) => { node.textContent = wedding.names })
const initials = wedding.couple.map(({ name }) => Array.from(name.trim())[0]).filter(Boolean)
document.querySelectorAll('[data-initials]').forEach((node) => { node.textContent = initials.join(' & ') })
if (wedding.photos?.length) {
  document.documentElement.style.setProperty('--cover-image', 'url("' + asset(wedding.photos[0].file) + '")')
}
document.querySelectorAll('[data-date]').forEach((node) => { node.textContent = wedding.date })
if (wedding.blessing) {
  byId('blessing-text').textContent = wedding.blessing
  byId('blessing').hidden = false
}
byId('welcome').textContent = wedding.welcome
byId('deadline').textContent = wedding.replyBy

for (const partner of wedding.couple) {
  const article = element('article', '')
  article.append(element('h3', partner.name))
  if (partner.family) article.append(element('p', partner.family))
  byId('couple').append(article)
}

function venueDetails(event) {
  const venue = element('div', '')
  venue.className = 'venue-details'
  const address = element('address', '')
  address.append(element('strong', event.venue), document.createElement('br'), event.address)
  const pin = event.mapPin && /^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$/.test(event.mapPin)
  const map = element('a', pin ? 'Buka pin pintu masuk' : 'Cari lokasi di Google Maps')
  map.href = 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(pin ? event.mapPin : event.mapQuery || event.venue + ', ' + event.address)
  map.setAttribute('aria-label', map.textContent + ' · ' + event.venue)
  venue.append(address, map)
  return venue
}

const [firstEvent] = wedding.events
const venueFields = ['date', 'venue', 'address', 'mapPin', 'mapQuery']
const sharedVenue = wedding.events.length > 1 && wedding.events.every(
  (event) => venueFields.every((field) => event[field] === firstEvent[field]),
)
if (sharedVenue) {
  const venue = byId('shared-venue')
  venue.append(element('p', firstEvent.date), venueDetails(firstEvent))
  venue.hidden = false
}
if (wedding.attendanceNote) {
  byId('attendance-note').textContent = wedding.attendanceNote
  byId('attendance-note').hidden = false
}

for (const event of wedding.events) {
  const article = element('article', '')
  const time = element('p', sharedVenue ? event.time : event.date + ' · ' + event.time)
  time.className = 'event-time'
  article.append(element('h3', event.title), time)
  if (!sharedVenue) article.append(venueDetails(event))
  const actions = element('div', '')
  actions.className = 'event-actions'
  const start = Date.parse(event.startsAt)
  const end = Date.parse(event.endsAt)
  if (Number.isFinite(start) && end > start) {
    const dateKey = (time) => new Date(time).toISOString().replace(/[-:]|\.\d{3}/g, '')
    const title = event.title + ' · ' + wedding.names
    const location = event.venue + ', ' + event.address
    const calendar = element('details', '')
    const google = element('a', 'Google Calendar')
    google.href = 'https://calendar.google.com/calendar/render?' + new URLSearchParams({
      action: 'TEMPLATE', text: title, dates: dateKey(start) + '/' + dateKey(end), location,
    })
    const download = element('a', 'Unduh kalender (.ics)')
    const escapeText = (text) => text.replaceAll('\\', '\\\\').replaceAll(/\r?\n/g, '\\n').replaceAll(/[,;]/g, '\\$&')
    const ics = [
      'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Invitation//Wedding//ID',
      'BEGIN:VEVENT', 'UID:' + escapeText(wedding.id) + '-' + dateKey(start) + '@invitation',
      'DTSTAMP:' + dateKey(Date.now()), 'DTSTART:' + dateKey(start), 'DTEND:' + dateKey(end),
      'SUMMARY:' + escapeText(title), 'LOCATION:' + escapeText(location),
      'END:VEVENT', 'END:VCALENDAR', '',
    ].join('\r\n')
    download.href = 'data:text/calendar;charset=utf-8,' + encodeURIComponent(ics)
    download.download = wedding.id + '-' + dateKey(start) + '.ics'
    const options = element('div', '')
    options.append(google, download)
    calendar.append(element('summary', 'Simpan ke kalender'), options)
    actions.append(calendar)
    article.append(actions)
  }
  byId('events').append(article)
}

const photos = wedding.photos || []
const viewer = byId('photo-viewer')
let photoIndex = 0
let photoTrigger
function showPhoto(index) {
  photoIndex = (index + photos.length) % photos.length
  const photo = photos[photoIndex]
  byId('full-photo').src = asset(photo.file)
  byId('full-photo').alt = photo.alt
  byId('photo-position').textContent = (photoIndex + 1) + ' / ' + photos.length
}
for (const [index, photo] of photos.entries()) {
  const img = document.createElement('img')
  img.src = asset(photo.file)
  img.alt = photo.alt
  img.loading = 'lazy'
  const thumbnail = element('a', '')
  thumbnail.className = 'thumbnail'
  thumbnail.href = img.src
  thumbnail.setAttribute('aria-label', 'Lihat foto: ' + photo.alt)
  thumbnail.append(img)
  thumbnail.addEventListener('click', (event) => {
    if (typeof viewer.showModal !== 'function' || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return
    event.preventDefault()
    showPhoto(index)
    photoTrigger = thumbnail
    viewer.showModal()
  })
  byId('photos').append(thumbnail)
}
byId('photo-close').addEventListener('click', () => viewer.close())
byId('photo-prev').addEventListener('click', () => showPhoto(photoIndex - 1))
byId('photo-next').addEventListener('click', () => showPhoto(photoIndex + 1))
byId('photo-prev').hidden = byId('photo-next').hidden = photos.length < 2
viewer.addEventListener('close', () => photoTrigger?.focus({ preventScroll: true }))
viewer.addEventListener('click', (event) => {
  if (event.target === viewer) viewer.close()
})
viewer.addEventListener('keydown', (event) => {
  if (photos.length < 2 || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return
  event.preventDefault()
  showPhoto(photoIndex + (event.key === 'ArrowLeft' ? -1 : 1))
})
for (const chapter of wedding.story || []) {
  const article = element('article', '')
  if (chapter.date) article.append(element('span', chapter.date))
  article.append(element('h3', chapter.title), element('p', chapter.text))
  byId('chapters').append(article)
}
byId('story').hidden = !wedding.story?.length
byId('galeri').hidden = !photos.length

const form = byId('reply')
const status = byId('reply-status')
const countField = byId('count-field')
const guest = new URLSearchParams(location.search).get('to')?.trim().slice(0, 120)
if (guest) {
  byId('guest').textContent = guest
  form.elements.guest.value = guest
}

const storageKey = 'invitation:rsvp:' + JSON.stringify([wedding.id, guest || ''])
function updateCount() {
  const attending = form.elements.attendance.value === 'yes'
  countField.hidden = !attending
  form.elements.count.disabled = !attending
  form.elements.count.required = attending
}

if (wedding.demo) {
  byId('demo-note').hidden = false
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey))
    if (saved) {
      form.elements.guest.value = saved.name
      form.elements.attendance.value = saved.attendance
      form.elements.count.value = saved.count || 1
      status.textContent = 'Konfirmasi demo tersimpan di perangkat ini.'
    }
  } catch {
    // The form still works when storage is empty or unavailable.
  }
  form.addEventListener('change', updateCount)
  form.addEventListener('input', () => { status.textContent = '' })
  form.addEventListener('submit', (event) => {
    event.preventDefault()
    const data = new FormData(form)
    const name = data.get('guest').trim()
    if (!name) {
      status.textContent = 'Masukkan nama Anda.'
      form.elements.guest.focus()
      return
    }
    const response = { name, attendance: data.get('attendance'), count: Number(data.get('count')) }
    try {
      localStorage.setItem(storageKey, JSON.stringify(response))
      status.textContent = 'Terima kasih. Konfirmasi demo tersimpan di perangkat ini.'
    } catch {
      status.textContent = 'Jawaban tidak tersimpan. Penyimpanan perangkat tidak tersedia.'
    }
  })
} else {
  form.hidden = true
  const email = wedding.contactEmail?.trim()
  const hasContact = email && /^[^\s@?&#]+@[^\s@?&#]+\.[^\s@?&#]+$/.test(email)
  if (hasContact) {
    const contact = element('a', 'Hubungi tuan rumah lewat email')
    contact.href = 'mailto:' + encodeURIComponent(email).replace('%40', '@')
    contact.className = 'button olive'
    form.before(contact)
  } else {
    form.before(element('p', 'Konfirmasi kehadiran belum tersedia.'))
  }
  byId('reply-deadline').hidden = !wedding.replyBy || !hasContact
}
updateCount()

if (wedding.music) {
  const button = byId('music')
  const player = new Audio(asset(wedding.music))
  player.preload = 'none'
  player.loop = true
  button.hidden = false
  const sync = () => {
    button.setAttribute('aria-pressed', String(!player.paused))
    button.querySelector('span').textContent = player.paused ? 'Putar musik' : 'Jeda musik'
  }
  player.addEventListener('play', sync)
  player.addEventListener('pause', sync)
  button.addEventListener('click', async () => {
    if (!player.paused) {
      player.pause()
      return
    }
    try {
      await player.play()
    } catch {
      button.querySelector('span').textContent = 'Musik tidak tersedia'
    }
  })
}

const countdown = byId('countdown')
const starts = wedding.events.map(({ startsAt }) => Date.parse(startsAt)).filter(Number.isFinite)
const weddingStart = Math.min(...starts)
if (Number.isFinite(weddingStart) && weddingStart > Date.now()) {
  countdown.hidden = false
  const updateTimer = () => {
    const left = Math.max(0, Math.ceil((weddingStart - Date.now()) / 1000))
    const units = { days: Math.floor(left / 86400), hours: Math.floor(left / 3600) % 24, minutes: Math.floor(left / 60) % 60, seconds: left % 60 }
    for (const [unit, value] of Object.entries(units)) {
      countdown.querySelector('[data-unit="' + unit + '"]').textContent = String(value).padStart(2, '0')
    }
    if (!left) clearInterval(timer)
  }
  const timer = setInterval(updateTimer, 1000)
  updateTimer()
}

const cover = byId('sampul')
const content = [document.querySelector('main'), document.querySelector('footer'), byId('music')]
const reducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)')
function revealInvitation(target = byId('pembuka')) {
  document.body.classList.remove('cover-locked')
  cover.inert = true
  for (const node of content) node.inert = false
  const finish = () => {
    cover.hidden = true
    watchReveals()
  }
  if (target.id === 'pembuka') playScene()
  if (!reducedMotion?.matches && cover.animate) {
    const animation = cover.animate(
      [{ transform: 'translateY(0)', opacity: 1 }, { offset: .78, opacity: .96 }, { transform: 'translateY(-100%)', opacity: 0 }],
      { duration: 730, easing: 'cubic-bezier(.68, .02, .22, 1)', fill: 'forwards' },
    )
    animation.finished.then(finish, finish)
  } else {
    finish()
  }
  target.focus({ preventScroll: true })
  target.scrollIntoView?.({ behavior: 'instant' })
}

const shortcut = location.hash && byId(location.hash.slice(1))
if (shortcut && shortcut !== cover) {
  cover.hidden = true
  requestAnimationFrame(() => {
    shortcut.scrollIntoView?.()
    if (shortcut.id === 'pembuka') playScene()
  })
} else {
  cover.classList.add('is-overlay')
  document.body.classList.add('cover-locked')
  for (const node of content) node.inert = true
  cover.querySelectorAll('a[href^="#"]:not([href="#sampul"])').forEach((link) => {
    link.addEventListener('click', (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return
      event.preventDefault()
      const hash = link.getAttribute('href')
      if (hash !== '#pembuka') history.replaceState(null, '', hash)
      revealInvitation(byId(hash.slice(1)))
    })
  })
}

let observer
const revealGroups = [
  ['.opening-details', '[data-motion]'],
  ['.welcome', 'h2, .couple article'],
  ['.story', 'h2, #chapters article'],
  ['.schedule', 'h2, #shared-venue, .events article'],
  ['.keepsakes', 'h2, .thumbnail'],
  ['.reply', 'h2, #reply-deadline, #reply'],
  ['footer', '.wedding-seal, .signature'],
]

function playScene() {
  if (reducedMotion?.matches) return
  byId('pembuka').classList.add('scene-enter')
}

function watchReveals() {
  if (observer || typeof IntersectionObserver !== 'function' || reducedMotion?.matches) return
  observer = new IntersectionObserver((entries) => {
    for (const { target, isIntersecting } of entries) {
      if (!isIntersecting) continue
      observer.unobserve(target)
      if (reducedMotion?.matches) continue
      const { stagger, side } = target.dataset
      target.animate?.(
        [
          { opacity: .15, translate: side + 'px 14px' },
          { opacity: 1, translate: '0 0' },
        ],
        { duration: 560, delay: Number(stagger), easing: 'cubic-bezier(.2,.7,.25,1)', fill: 'backwards' },
      )
    }
  }, { threshold: .12 })
  for (const [group, items] of revealGroups) {
    document.querySelectorAll(group + ' :is(' + items + ')').forEach((node, index) => {
      node.dataset.stagger = String(Math.min(index, 3) * 85)
      node.dataset.side = node.matches('.couple article, #chapters article, .thumbnail') ? (index % 2 ? '-16' : '16') : '0'
      observer.observe(node)
    })
  }
}

if (!document.body.classList.contains('cover-locked')) watchReveals()
