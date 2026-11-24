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
if (wedding.photos?.length) {
  byId('sampul').style.setProperty('--cover-image', 'url("' + asset(wedding.photos[0].file) + '")')
}
document.querySelector('[data-date]').textContent = wedding.date
byId('welcome').textContent = wedding.welcome
byId('deadline').textContent = wedding.replyBy

for (const partner of wedding.couple) {
  const article = element('article', '')
  article.append(element('h3', partner.name))
  if (partner.family) article.append(element('p', partner.family))
  byId('couple').append(article)
}

for (const event of wedding.events) {
  const article = element('article', '')
  const address = element('address', '')
  address.append(element('strong', event.venue), document.createElement('br'), event.address)
  const map = element('a', 'Lihat lokasi')
  map.href = 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(event.mapQuery || event.venue + ', ' + event.address)
  map.setAttribute('aria-label', 'Lihat lokasi ' + event.title)
  article.append(element('h3', event.title), element('p', event.date + ' · ' + event.time), address, map)
  byId('events').append(article)
}

for (const photo of wedding.photos || []) {
  const img = document.createElement('img')
  img.src = asset(photo.file)
  img.alt = photo.alt
  img.loading = 'lazy'
  byId('photos').append(img)
}
for (const chapter of wedding.story || []) {
  const article = element('article', '')
  article.append(element('h4', chapter.title), element('p', chapter.text))
  byId('chapters').append(article)
}
byId('story').hidden = !wedding.story?.length
byId('galeri').hidden = !(wedding.photos?.length || wedding.story?.length)
if (!wedding.photos?.length) byId('galeri').querySelector('h2').textContent = 'Cerita kami'

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
  form.elements.attendance.addEventListener('change', updateCount)
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
  form.before(element('p', 'Konfirmasi online belum tersedia. Silakan hubungi tuan rumah.'))
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
