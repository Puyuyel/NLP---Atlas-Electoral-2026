const chat = document.getElementById('chat'),
      intro = document.getElementById('intro'),
      q = document.getElementById('q'),
      send = document.getElementById('send'),
      btnNew = document.getElementById('btn-new'),
      ctxBadge = document.getElementById('ctx-badge');

let busy = false;
let historial = []; // [{role:"user",content:"..."},{role:"assistant",content:"..."}]

function actualizarCtx() {
  const turns = historial.length / 2;
  if (turns > 0) {
    ctxBadge.style.display = 'inline';
    ctxBadge.textContent = turns + ' turno' + (turns > 1 ? 's' : '');
  } else {
    ctxBadge.style.display = 'none';
  }
}

btnNew.addEventListener('click', () => {
  historial = [];
  actualizarCtx();
  chat.innerHTML = '';
  intro.style.display = '';
  q.focus();
});

const EJEMPLOS = [
  "¿Qué propone Keiko Fujimori en seguridad y qué opina la gente de ella?",
  "Compara las propuestas de educación de Roberto Sánchez y Rafael López Aliaga",
  "¿Qué dice el plan de Ricardo Belmont sobre la economía?",
  "¿Qué ha declarado Jorge Nieto en entrevistas sobre la corrupción?"
];

fetch('/api/meta').then(r => r.json()).then(m => {
  document.getElementById('planos').textContent = 'Planos: ' + (m.planos || []).join(' · ');
  const chips = document.getElementById('chips');
  (m.candidatos || []).forEach(n => {
    const c = document.createElement('button');
    c.className = 'chip';
    c.textContent = n;
    c.onclick = () => { q.value = '¿Qué propone ' + n + '?'; q.focus(); };
    chips.appendChild(c);
  });
  const ex = document.getElementById('examples');
  EJEMPLOS.forEach(t => {
    const b = document.createElement('button');
    b.className = 'ex';
    b.textContent = t;
    b.onclick = () => { q.value = t; enviar(); };
    ex.appendChild(b);
  });
}).catch(() => { document.getElementById('planos').textContent = 'sin conexión'; });

function esc(s) {
  return s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
}

function fmt(t) {
  let h = esc(t);
  h = h.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  h = h.replace(/\[(\d+)\]/g, '<span class="cite">[$1]</span>');
  const lines = h.split(/\n/).filter(x => x.trim() !== '');
  return lines.map(l => {
    if (/^\s*(📋|🎤|💬)/.test(l)) return '<h4>' + l.trim() + '</h4>';
    if (/^\s*#{1,4}\s/.test(l)) return '<h4>' + l.replace(/^\s*#{1,4}\s/, '') + '</h4>';
    return '<p>' + l + '</p>';
  }).join('');
}

function avatar(b) {
  return '<div class="av">' + (b ? '⚖️' : '🧑') + '</div>';
}

function add(role, html) {
  const d = document.createElement('div');
  d.className = 'msg ' + role;
  d.innerHTML = avatar(role === 'bot') + '<div class="bubble">' + html + '</div>';
  chat.appendChild(d);
  d.scrollIntoView({ behavior: 'smooth', block: 'end' });
  return d;
}

function fuentesHTML(fs) {
  if (!fs || !fs.length) return '';
  const li = fs.map(f => {
    const ref = esc(f.ref || '');
    const url = f.url || '';
    const link = url.startsWith('http')
      ? '<a href="' + esc(url) + '" target="_blank" rel="noopener">' + ref + '</a>'
      : ref;
    return '<li>[' + f.n + '] ' + esc(f.tipo) + ' — ' + link + '</li>';
  }).join('');
  return '<details class="src"><summary>📚 Fuentes (' + fs.length + ')</summary><ol>' + li + '</ol></details>';
}

async function enviar() {
  const texto = q.value.trim();
  if (!texto || busy) return;
  intro.style.display = 'none';
  add('user', esc(texto));
  q.value = '';
  q.style.height = 'auto';
  busy = true;
  send.disabled = true;
  const load = add('bot', '<div class="typing"><span></span><span></span><span></span></div>');
  const bbl = load.querySelector('.bubble');
  let finalAnswer = '';
  try {
    const r = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pregunta: texto, historial: historial.slice(-6) })
    });
    if (!r.ok || !r.body) throw new Error('Sin respuesta del servidor');
    const reader = r.body.getReader();
    const dec = new TextDecoder();
    let buf = '', raw = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const lines = buf.split('\n');
      buf = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        let ev;
        try { ev = JSON.parse(line.slice(6)); } catch { continue; }
        if (ev.status) {
          bbl.innerHTML = '<p class="status-msg">' + esc(ev.status) + '</p>';
        } else if (ev.token) {
          raw += ev.token;
          bbl.innerHTML = fmt(raw) + '<span class="cursor">▋</span>';
          load.scrollIntoView({ behavior: 'smooth', block: 'end' });
        } else if (ev.done) {
          finalAnswer = ev.answer || raw;
          bbl.innerHTML = fmt(finalAnswer) + fuentesHTML(ev.fuentes);
        } else if (ev.error) {
          bbl.innerHTML = '<p>⚠️ ' + esc(ev.error) + '</p>';
        }
      }
    }
    if (finalAnswer) {
      historial.push({ role: 'user', content: texto });
      historial.push({ role: 'assistant', content: finalAnswer });
      actualizarCtx();
    }
  } catch (e) {
    bbl.innerHTML = '<p>⚠️ No pude conectar con el servidor.</p>';
  }
  load.scrollIntoView({ behavior: 'smooth', block: 'end' });
  busy = false;
  send.disabled = false;
  q.focus();
}

send.onclick = enviar;
q.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); enviar(); }
});
q.addEventListener('input', () => {
  q.style.height = 'auto';
  q.style.height = Math.min(q.scrollHeight, 120) + 'px';
});
