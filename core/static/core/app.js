const csrf = () => document.cookie.split('; ').find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';
const post = (url, body) => fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()}, body: JSON.stringify(body)});
const toast = m => { const t = document.getElementById('toast'); t.textContent = m; t.hidden = false; setTimeout(() => t.hidden = true, 3500); };

function initBoard() {
  let dragged = null;
  document.querySelectorAll('.task').forEach(t => {
    t.addEventListener('dragstart', () => { dragged = t; t.classList.add('drag'); });
    t.addEventListener('dragend', () => t.classList.remove('drag'));
  });
  document.querySelectorAll('.col').forEach(col => {
    col.addEventListener('dragover', e => { e.preventDefault(); col.classList.add('over'); });
    col.addEventListener('dragleave', () => col.classList.remove('over'));
    col.addEventListener('drop', async e => {
      e.preventDefault(); col.classList.remove('over');
      if (!dragged) return;
      const from = dragged.closest('.cards'), to = col.querySelector('.cards');
      to.appendChild(dragged);
      const r = await post(`/tasks/${dragged.dataset.id}/move/`, {status: col.dataset.status});
      if (!r.ok) { from.appendChild(dragged); toast((await r.json()).error || 'Could not move task.'); }
      document.querySelectorAll('.col').forEach(c => c.querySelector('.count').textContent = c.querySelectorAll('.task').length);
    });
  });
}

function initComments() {
  const box = document.getElementById('comments'), txt = document.getElementById('ctext');
  document.getElementById('csend').addEventListener('click', async () => {
    if (!txt.value.trim()) return;
    const r = await post(box.dataset.url, {text: txt.value});
    if (!r.ok) return toast((await r.json()).error);
    const c = await r.json(), d = document.createElement('div');
    d.className = 'comment'; d.innerHTML = '<b></b> <span class="small"></span><p></p>';
    d.querySelector('b').textContent = c.author; d.querySelector('span').textContent = c.created; d.querySelector('p').textContent = c.text;
    box.appendChild(d); txt.value = '';
  });
}

if (document.body.dataset.auth) {
  const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/notifications/`);
  ws.onmessage = e => {
    const d = JSON.parse(e.data), b = document.getElementById('badge');
    b.textContent = d.unread; b.hidden = !d.unread; toast(d.message);
    const list = document.getElementById('nlist');
    if (list) { const a = document.createElement('a'); a.className = 'note new'; a.href = d.link || '#'; a.textContent = d.message; list.prepend(a); }
  };
}
