// Minimal control UI for ESP-Music-Player.

const $ = (sel) => document.querySelector(sel);
const api = (path, opts = {}) => fetch(path, { method: opts.method || 'GET', body: opts.body });
const post = (path, params) => {
  const body = new URLSearchParams(params || {});
  return fetch(path, { method: 'POST', body });
};

let lastVolumeSent = -1;
let activeIndex = -1;

function renderLibrary(tracks) {
  const lib = $('#library');
  if (!tracks.length) { lib.textContent = 'No music on SD card. Upload some, or copy /music/<Album>/*.mp3.'; return; }
  // Group by album.
  const byAlbum = new Map();
  for (const t of tracks) {
    if (!byAlbum.has(t.album)) byAlbum.set(t.album, []);
    byAlbum.get(t.album).push(t);
  }
  lib.innerHTML = '';
  for (const [album, list] of byAlbum) {
    const wrap = document.createElement('div');
    wrap.className = 'album';
    const h = document.createElement('h3'); h.textContent = album; wrap.appendChild(h);
    for (const t of list) {
      const row = document.createElement('div');
      row.className = 'track' + (t.i === activeIndex ? ' active' : '');
      row.dataset.i = t.i;
      const nm = document.createElement('span'); nm.className = 'name'; nm.textContent = t.name;
      const pl = document.createElement('span'); pl.textContent = '▶';
      row.append(nm, pl);
      row.addEventListener('click', () => post('/api/play', { i: t.i }));
      wrap.appendChild(row);
    }
    lib.appendChild(wrap);
  }
}

async function refreshLibrary() {
  try {
    const r = await api('/api/files'); const j = await r.json();
    renderLibrary(j.tracks || []);
  } catch (e) { /* ignore */ }
}

async function refreshStatus() {
  try {
    const r = await api('/api/status'); const j = await r.json();
    $('#np-title').textContent = j.title || '—';
    $('#np-state').textContent = j.playing ? 'playing' : 'paused';
    $('#status').textContent = `${j.wifi || ''} ${j.ip || ''} · ${(j.heap/1024)|0}KB free`;
    if (j.index !== activeIndex) {
      activeIndex = j.index;
      // Toggle .active class without re-rendering everything
      document.querySelectorAll('.track').forEach(el => {
        el.classList.toggle('active', Number(el.dataset.i) === activeIndex);
      });
    }
    if (lastVolumeSent < 0) {
      const pct = Math.round((j.volume / (j.volumeMax || 21)) * 100);
      $('#vol').value = pct;
      $('#vol-pct').textContent = pct;
    }
    $('#footer-info').textContent = `host: esp-music · firmware OTA → /update`;
  } catch (e) { $('#status').textContent = 'offline'; }
}

// Controls
$('#play').addEventListener('click', () => post('/api/play'));
$('#pause').addEventListener('click', () => post('/api/pause'));
$('#prev').addEventListener('click', () => post('/api/prev'));
$('#next').addEventListener('click', () => post('/api/next'));
$('#next-album').addEventListener('click', () => post('/api/next_album'));
$('#rescan').addEventListener('click', async () => { await post('/api/rescan'); refreshLibrary(); });
$('#wifi-reset').addEventListener('click', async () => {
  if (confirm('Forget Wi-Fi credentials and reboot into setup AP?')) await post('/api/wifi_reset');
});

// Volume slider — debounce, only send on change.
let volTimer;
$('#vol').addEventListener('input', (e) => {
  const v = Number(e.target.value);
  $('#vol-pct').textContent = v;
  clearTimeout(volTimer);
  volTimer = setTimeout(() => { lastVolumeSent = v; post('/api/volume', { v }); }, 80);
});

// Upload via XHR so we get progress
$('#upload-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const album = form.album.value || 'Uploads';
  const files = form.file.files;
  if (!files.length) return;

  const progress = $('#upload-progress');
  progress.hidden = false; progress.value = 0;

  const queue = [...files];
  const next = () => {
    if (!queue.length) {
      progress.hidden = true;
      form.reset();
      refreshLibrary();
      return;
    }
    const f = queue.shift();
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `/api/upload?album=${encodeURIComponent(album)}`);
    xhr.upload.onprogress = (ev) => {
      if (ev.lengthComputable) progress.value = (ev.loaded / ev.total) * 100;
    };
    xhr.onload = () => next();
    xhr.onerror = () => { alert(`Upload failed: ${f.name}`); next(); };
    const fd = new FormData();
    fd.append('album', album);
    fd.append('file', f, f.name);
    xhr.send(fd);
  };
  next();
});

// Initial + polling
refreshLibrary();
refreshStatus();
setInterval(refreshStatus, 2000);
