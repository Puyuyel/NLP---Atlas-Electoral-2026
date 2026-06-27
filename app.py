"""
Interfaz web del chatbot electoral (para no usar la terminal).
Levanta un servidor local y abres la página en el navegador.

Requisitos: pip install flask  (+ todo lo del proyecto y Ollama corriendo)
Uso:  python app.py   ->  abre http://127.0.0.1:5000
"""
import json
from flask import Flask, request, jsonify, Response, stream_with_context

import config
from rag import RAG

app = Flask(__name__)

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

print("Cargando modelos locales (la 1ª vez descarga pesos, puede tardar)...")
rag = RAG()
print("Listo. Abre http://127.0.0.1:5000 en tu navegador.")


@app.route("/")
def index():
    return Response(PAGINA, mimetype="text/html")


@app.route("/api/meta")
def meta():
    return jsonify({
        "candidatos": [c["nombre"] for c in config.CANDIDATOS],
        "planos": rag.planos_disponibles(),
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    pregunta = (data.get("pregunta") or "").strip()
    if not pregunta:
        return jsonify({"error": "Pregunta vacía"}), 400
    try:
        return jsonify(rag.responder(pregunta))
    except Exception as e:
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500


@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json(force=True, silent=True) or {}
    pregunta = (data.get("pregunta") or "").strip()
    if not pregunta:
        return jsonify({"error": "Pregunta vacía"}), 400
    historial = data.get("historial") or []

    def generate():
        try:
            for evento in rag.responder_stream(pregunta, historial):
                yield f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'{type(e).__name__}: {e}'}, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


PAGINA = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Asistente Electoral · Perú 2026</title>
<style>
  :root{
    --bg:#f4f5f7; --panel:#ffffff; --ink:#16181d; --muted:#6b7280;
    --accent:#c1121f; --accent-soft:#fde8ea; --line:#e6e8ec; --user:#1f2937;
    --radius:14px; --shadow:0 1px 3px rgba(0,0,0,.06),0 8px 24px rgba(0,0,0,.05);
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:"Segoe UI",system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif;}
  header{background:var(--panel);border-bottom:1px solid var(--line);padding:14px 20px;
    display:flex;align-items:center;gap:14px;position:sticky;top:0;z-index:5}
  .logo{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,var(--accent),#7a0c14);
    color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:18px}
  header h1{font-size:16px;margin:0;line-height:1.2}
  header p{margin:2px 0 0;font-size:12.5px;color:var(--muted)}
  .badge{margin-left:auto;font-size:11.5px;color:var(--muted);border:1px solid var(--line);
    border-radius:999px;padding:5px 11px;background:#fbfbfc;white-space:nowrap}
  main{max-width:860px;margin:0 auto;padding:22px 16px 130px}
  .chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
  .chip{font-size:12.5px;border:1px solid var(--line);background:var(--panel);color:#374151;
    border-radius:999px;padding:6px 12px;cursor:pointer;transition:.15s}
  .chip:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-soft)}
  .intro{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
    padding:20px 22px;box-shadow:var(--shadow)}
  .intro h2{margin:0 0 6px;font-size:18px}
  .intro p{margin:0 0 14px;color:var(--muted);font-size:14px;line-height:1.5}
  .examples{display:grid;gap:8px}
  .ex{display:block;width:100%;text-align:left;border:1px solid var(--line);background:#fbfbfc;
    border-radius:10px;padding:11px 14px;font-size:13.5px;cursor:pointer;color:#374151;transition:.15s}
  .ex:hover{border-color:var(--accent);background:var(--accent-soft);color:var(--accent)}
  .msg{display:flex;gap:12px;margin:18px 0}
  .msg .av{width:34px;height:34px;border-radius:9px;flex:0 0 34px;display:flex;align-items:center;
    justify-content:center;font-size:16px}
  .msg.user{flex-direction:row-reverse}
  .msg.user .av{background:var(--user);color:#fff}
  .msg.bot .av{background:var(--accent-soft);color:var(--accent)}
  .bubble{padding:14px 16px;border-radius:var(--radius);max-width:82%;font-size:14.5px;line-height:1.6}
  .msg.user .bubble{background:var(--user);color:#fff;border-bottom-right-radius:5px}
  .msg.bot .bubble{background:var(--panel);border:1px solid var(--line);box-shadow:var(--shadow);
    border-bottom-left-radius:5px}
  .bubble h4{margin:14px 0 4px;font-size:14.5px;display:flex;align-items:center;gap:6px}
  .bubble h4:first-child{margin-top:0}
  .bubble p{margin:0 0 9px}
  .cite{color:var(--accent);font-weight:600;font-size:12px;vertical-align:super}
  details.src{margin-top:12px;border-top:1px dashed var(--line);padding-top:9px}
  details.src summary{cursor:pointer;font-size:12.5px;color:var(--muted);font-weight:600}
  details.src ol{margin:8px 0 0;padding-left:20px}
  details.src li{font-size:12.5px;color:#4b5563;margin:3px 0}
  details.src a{color:var(--accent);text-decoration:none}
  .typing span{display:inline-block;width:7px;height:7px;margin:0 2px;border-radius:50%;
    background:var(--muted);animation:b 1.2s infinite}
  .typing span:nth-child(2){animation-delay:.2s}.typing span:nth-child(3){animation-delay:.4s}
  @keyframes b{0%,60%,100%{opacity:.25;transform:translateY(0)}30%{opacity:1;transform:translateY(-4px)}}
  .composer{position:fixed;bottom:0;left:0;right:0;background:linear-gradient(180deg,rgba(244,245,247,0),var(--bg) 28%);
    padding:14px 16px 18px}
  .composer .inner{max-width:860px;margin:0 auto;display:flex;gap:10px;background:var(--panel);
    border:1px solid var(--line);border-radius:14px;padding:8px 8px 8px 14px;box-shadow:var(--shadow)}
  .composer textarea{flex:1;border:0;outline:0;resize:none;font:inherit;font-size:14.5px;
    background:transparent;max-height:120px;padding:8px 0;color:var(--ink)}
  .send{border:0;background:var(--accent);color:#fff;border-radius:10px;padding:0 18px;font-size:14px;
    font-weight:600;cursor:pointer;transition:.15s}
  .send:disabled{background:#cbd0d6;cursor:not-allowed}
  .disclaimer{max-width:860px;margin:8px auto 0;text-align:center;font-size:11px;color:var(--muted)}
  .status-msg{color:var(--muted);font-style:italic;font-size:13px}
  .cursor{opacity:.5;animation:blink 1s step-end infinite}
  @keyframes blink{0%,100%{opacity:.5}50%{opacity:0}}
  .btn-new{font-size:12px;border:1px solid var(--line);background:var(--panel);color:var(--muted);
    border-radius:999px;padding:5px 12px;cursor:pointer;transition:.15s;white-space:nowrap}
  .btn-new:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-soft)}
  .ctx-badge{font-size:11px;color:var(--muted);background:var(--accent-soft);color:var(--accent);
    border-radius:999px;padding:3px 8px;display:none}
</style>
</head>
<body>
<header>
  <div class="logo">PE</div>
  <div>
    <h1>Asistente Electoral · Perú 2026</h1>
    <p>Plan de gobierno · declaraciones · opinión pública</p>
  </div>
  <span class="badge" id="planos">cargando…</span>
  <span class="ctx-badge" id="ctx-badge"></span>
  <button class="btn-new" id="btn-new" title="Borrar historial y empezar una nueva conversación">+ Nueva conversación</button>
</header>

<main id="main">
  <div class="chips" id="chips"></div>
  <div class="intro" id="intro">
    <h2>¿Qué quieres saber de los candidatos?</h2>
    <p>Pregunta en lenguaje natural. Contrasto lo que <b>prometen</b> en su plan, lo que
       <b>declaran</b> en entrevistas y lo que <b>opina la gente</b>, siempre citando las fuentes.</p>
    <div class="examples" id="examples"></div>
  </div>
  <div id="chat"></div>
</main>

<div class="composer">
  <div class="inner">
    <textarea id="q" rows="1" placeholder="Escribe tu pregunta… (Enter para enviar)"></textarea>
    <button class="send" id="send">Enviar</button>
  </div>
  <div class="disclaimer">Información con fines informativos. Las opiniones de redes son percepciones, no hechos verificados.</div>
</div>

<script>
const chat=document.getElementById('chat'), intro=document.getElementById('intro'),
      q=document.getElementById('q'), send=document.getElementById('send'),
      btnNew=document.getElementById('btn-new'), ctxBadge=document.getElementById('ctx-badge');
let busy=false;
let historial=[]; // [{role:"user",content:"..."},{role:"assistant",content:"..."}]

function actualizarCtx(){
  const turns=historial.length/2;
  if(turns>0){
    ctxBadge.style.display='inline';
    ctxBadge.textContent=turns+' turno'+(turns>1?'s':'');
  } else {
    ctxBadge.style.display='none';
  }
}

btnNew.addEventListener('click',()=>{
  historial=[];
  actualizarCtx();
  chat.innerHTML='';
  intro.style.display='';
  q.focus();
});

const EJEMPLOS=[
  "¿Qué propone Keiko Fujimori en seguridad y qué opina la gente de ella?",
  "Compara las propuestas de educación de Roberto Sánchez y Rafael López Aliaga",
  "¿Qué dice el plan de Ricardo Belmont sobre la economía?",
  "¿Qué ha declarado Jorge Nieto en entrevistas sobre la corrupción?"
];

fetch('/api/meta').then(r=>r.json()).then(m=>{
  document.getElementById('planos').textContent='Planos: '+(m.planos||[]).join(' · ');
  const chips=document.getElementById('chips');
  (m.candidatos||[]).forEach(n=>{const c=document.createElement('button');c.className='chip';
    c.textContent=n;c.onclick=()=>{q.value='¿Qué propone '+n+'?';q.focus();};chips.appendChild(c);});
  const ex=document.getElementById('examples');
  EJEMPLOS.forEach(t=>{const b=document.createElement('button');b.className='ex';b.textContent=t;
    b.onclick=()=>{q.value=t;enviar();};ex.appendChild(b);});
}).catch(()=>{document.getElementById('planos').textContent='sin conexión';});

function esc(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function fmt(t){
  let h=esc(t);
  h=h.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
  h=h.replace(/\[(\d+)\]/g,'<span class="cite">[$1]</span>');
  const lines=h.split(/\n/).filter(x=>x.trim()!=='');
  return lines.map(l=>{
    if(/^\s*(📋|🎤|💬)/.test(l)) return '<h4>'+l.trim()+'</h4>';
    if(/^\s*#{1,4}\s/.test(l)) return '<h4>'+l.replace(/^\s*#{1,4}\s/,'')+'</h4>';
    return '<p>'+l+'</p>';
  }).join('');
}
function avatar(b){return '<div class="av">'+(b?'⚖️':'🧑')+'</div>';}
function add(role,html){
  const d=document.createElement('div');d.className='msg '+role;
  d.innerHTML=avatar(role==='bot')+'<div class="bubble">'+html+'</div>';
  chat.appendChild(d);d.scrollIntoView({behavior:'smooth',block:'end'});return d;
}
function fuentesHTML(fs){
  if(!fs||!fs.length) return '';
  const li=fs.map(f=>{
    const ref=esc(f.ref||''); const url=f.url||'';
    const link=url.startsWith('http')?'<a href="'+esc(url)+'" target="_blank" rel="noopener">'+ref+'</a>':ref;
    return '<li>['+f.n+'] '+esc(f.tipo)+' — '+link+'</li>';
  }).join('');
  return '<details class="src"><summary>📚 Fuentes ('+fs.length+')</summary><ol>'+li+'</ol></details>';
}

async function enviar(){
  const texto=q.value.trim(); if(!texto||busy) return;
  intro.style.display='none';
  add('user',esc(texto)); q.value=''; q.style.height='auto';
  busy=true; send.disabled=true;
  const load=add('bot','<div class="typing"><span></span><span></span><span></span></div>');
  const bbl=load.querySelector('.bubble');
  let finalAnswer='';
  try{
    const r=await fetch('/api/chat/stream',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({pregunta:texto, historial:historial.slice(-6)})});
    if(!r.ok||!r.body){throw new Error('Sin respuesta del servidor');}
    const reader=r.body.getReader(); const dec=new TextDecoder();
    let buf='', raw='';
    while(true){
      const{done,value}=await reader.read(); if(done) break;
      buf+=dec.decode(value,{stream:true});
      const lines=buf.split('\n'); buf=lines.pop();
      for(const line of lines){
        if(!line.startsWith('data: ')) continue;
        let ev; try{ev=JSON.parse(line.slice(6));}catch{continue;}
        if(ev.status){
          bbl.innerHTML='<p class="status-msg">'+esc(ev.status)+'</p>';
        }else if(ev.token){
          raw+=ev.token;
          bbl.innerHTML=fmt(raw)+'<span class="cursor">▋</span>';
          load.scrollIntoView({behavior:'smooth',block:'end'});
        }else if(ev.done){
          finalAnswer=ev.answer||raw;
          bbl.innerHTML=fmt(finalAnswer)+fuentesHTML(ev.fuentes);
        }else if(ev.error){
          bbl.innerHTML='<p>⚠️ '+esc(ev.error)+'</p>';
        }
      }
    }
    // Guardar turno en historial solo si hubo respuesta
    if(finalAnswer){
      historial.push({role:'user',content:texto});
      historial.push({role:'assistant',content:finalAnswer});
      actualizarCtx();
    }
  }catch(e){bbl.innerHTML='<p>⚠️ No pude conectar con el servidor.</p>';}
  load.scrollIntoView({behavior:'smooth',block:'end'});
  busy=false; send.disabled=false; q.focus();
}
send.onclick=enviar;
q.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();enviar();}});
q.addEventListener('input',()=>{q.style.height='auto';q.style.height=Math.min(q.scrollHeight,120)+'px';});
</script>
</body>
</html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
