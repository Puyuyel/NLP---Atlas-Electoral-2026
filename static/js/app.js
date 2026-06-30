'use strict';

// ─── CANDIDATOS ───────────────────────────────────────────────────────────────

const CANDS = [
  {
    id: 'keiko', name: 'Keiko Fujimori', party: 'Fuerza Popular',
    initials: 'KF', cv: 'cv-keiko',
    photo: 'img/candidates/keiko-fujimori.jpg',
    partyLogo: 'img/parties/fuerza-popular.png',
    bio: 'Excandidata presidencial en tres ocasiones (2011, 2016, 2021) y líder de Fuerza Popular. Su propuesta combina economía social de mercado, mano dura en seguridad y defensa de la familia tradicional.',
    sent: { pos: 38, neg: 54 }
  },
  {
    id: 'sanchez', name: 'Roberto Sánchez', party: 'Juntos por el Perú',
    initials: 'RS', cv: 'cv-sanchez',
    photo: 'img/candidates/roberto-sanchez.jpg',
    partyLogo: 'img/parties/juntos-por-el-peru.png',
    bio: 'Exministro de Comercio Exterior y Turismo del gobierno de Pedro Castillo. Representa la izquierda democrática con énfasis en derechos laborales, transición ecológica y reforma del Estado.',
    sent: { pos: 42, neg: 35 }
  },
  {
    id: 'belmont', name: 'Ricardo Belmont', party: 'Partido Cívico Obras',
    initials: 'RB', cv: 'cv-belmont',
    photo: 'img/candidates/ricardo-belmont.jpg',
    partyLogo: 'img/parties/partido-civico-obras.png',
    bio: 'Empresario de medios y exalcalde de Lima (1990-1995). Propone un enfoque pragmático de centro-derecha, centrado en gestión eficiente, grandes obras de infraestructura y reducción de la burocracia.',
    sent: { pos: 45, neg: 30 }
  },
  {
    id: 'lopez', name: 'Rafael López Aliaga', party: 'Renovación Popular',
    initials: 'RL', cv: 'cv-lopez',
    photo: 'img/candidates/rafael-lopez-aliaga.jpg',
    partyLogo: 'img/parties/renovacion-popular.png',
    bio: 'Empresario del transporte y líder de Renovación Popular. Su plataforma es ultraliberal en economía (reducción drástica del Estado, privatizaciones) y conservadora en valores sociales.',
    sent: { pos: 31, neg: 58 }
  },
  {
    id: 'nieto', name: 'Jorge Nieto', party: 'Partido del Buen Gobierno',
    initials: 'JN', cv: 'cv-nieto',
    photo: 'img/candidates/jorge-nieto.jpg',
    partyLogo: 'img/parties/partido-del-buen-gobierno.png',
    bio: 'Politólogo, exministro de Defensa y académico. Perfil técnico-reformista de centro, enfocado en reforma de justicia, modernización del Estado y política social basada en evidencia.',
    sent: { pos: 51, neg: 28 }
  },
];

// ─── TEMAS ────────────────────────────────────────────────────────────────────

const TOPICS = [
  { key: 'economia',   es: 'Economía',      qu: "Qullqi" },
  { key: 'seguridad',  es: 'Seguridad',     qu: "Allin kawsay" },
  { key: 'educacion',  es: 'Educación',     qu: "Yachay" },
  { key: 'salud',      es: 'Salud',         qu: "Hampikuy" },
  { key: 'cultura',    es: 'Cultura',       qu: "Kawsay" },
  { key: 'ambiente',   es: 'Ambiente',      qu: "Pachamama" },
  { key: 'empleo',     es: 'Empleo',        qu: "Llank'ay" },
  { key: 'corrupcion', es: 'Corrupción',    qu: "Ch'iqniy" },
];

// Índice de postura por candidato (0=conservador … 3=progresista)
const STANCE = {
  lopez:   [0, 0, 0, 0, 1, 0, 0, 0],
  keiko:   [1, 0, 1, 1, 1, 1, 1, 0],
  belmont: [1, 1, 1, 1, 2, 1, 2, 1],
  nieto:   [2, 2, 2, 2, 2, 2, 1, 2],
  sanchez: [3, 3, 3, 2, 3, 3, 3, 3],
};

// 8 preguntas con 4 opciones cada una (índice 0-3 = eje conservador→progresista)
const QUESTIONS = [
  {
    topic: 'economia',
    text: '¿Cuál debe ser el rol del Estado en la economía?',
    opts: [
      'Libre mercado con mínima intervención estatal y reducción de impuestos',
      'Economía social de mercado con regulación moderada en sectores clave',
      'Gestión técnica con inversión pública estratégica en infraestructura',
      'Estado rector con empresas públicas y control de precios en sectores básicos',
    ]
  },
  {
    topic: 'seguridad',
    text: '¿Cómo debe enfrentarse la inseguridad ciudadana?',
    opts: [
      'Penas más severas, mayor represión y control migratorio estricto',
      'Más policías en las calles y reforma del sistema penitenciario',
      'Reforma integral de la PNP, fiscalía y justicia con métricas claras',
      'Atacar las causas raíz: pobreza, desempleo juvenil y exclusión social',
    ]
  },
  {
    topic: 'educacion',
    text: '¿Cuál debe ser la prioridad en educación?',
    opts: [
      'Libertad de enseñanza, más participación privada y currículum basado en valores',
      'Reforzar la educación básica con disciplina, vocación técnica y moral',
      'Reforma curricular basada en evidencia, meritocracia docente y tecnología',
      'Educación pública gratuita y de calidad como derecho universal, sin lucro',
    ]
  },
  {
    topic: 'salud',
    text: '¿Cómo mejorar el sistema de salud?',
    opts: [
      'Fomentar el aseguramiento privado y la competencia entre prestadores',
      'Fortalecer EsSalud y el SIS con participación complementaria del sector privado',
      'Sistema universal técnico: fusión EsSalud-MINSA y gestión por resultados',
      'Sistema único de salud estatal, gratuito y universal para todos',
    ]
  },
  {
    topic: 'cultura',
    text: '¿Qué política cultural y de valores debe tener el Estado?',
    opts: [
      'Proteger la familia tradicional y los valores cristianos en la educación pública',
      'Promover la identidad nacional con respeto a la tradición y el patrimonio',
      'Invertir en diversidad cultural, creatividad y patrimonio como motor económico',
      'Reconocer la plurinacionalidad y los derechos de comunidades indígenas y afroperuanas',
    ]
  },
  {
    topic: 'ambiente',
    text: '¿Cómo debe el Perú gestionar sus recursos naturales?',
    opts: [
      'Priorizar la extracción de recursos para el crecimiento económico',
      'Equilibrio entre extracción responsable y protección ambiental mínima',
      'Economía verde con estándares técnicos y atracción de inversión sostenible',
      'Transición ecológica justa: derechos de la naturaleza y consulta previa obligatoria',
    ]
  },
  {
    topic: 'empleo',
    text: '¿Qué enfoque debe tener la política de empleo?',
    opts: [
      'Flexibilización laboral total para reducir informalidad y atraer inversión',
      'Reforma laboral moderada con contratos flexibles y protecciones básicas',
      'Formalización con incentivos a PYMES, capacitación y reducción de sobrecostos',
      'Empleo pleno: alza del salario mínimo, sindicatos fuertes y derechos laborales',
    ]
  },
  {
    topic: 'corrupcion',
    text: '¿Cómo combatir la corrupción en el Estado?',
    opts: [
      'Reducir el tamaño del Estado para eliminar oportunidades de corrupción',
      'Fortalecer la Contraloría, sanciones más duras y sistema anticorrupción',
      'Reforma del sistema de justicia con meritocracia, transparencia y tecnología',
      'Control social: participación ciudadana activa y transparencia radical del Estado',
    ]
  },
];

const EXAMPLES = [
  '¿Qué propone Keiko Fujimori en seguridad ciudadana?',
  '¿Cuál es el plan de Roberto Sánchez para el medio ambiente?',
  '¿Qué dice López Aliaga sobre la economía?',
  '¿Qué candidato tiene el plan más detallado en educación?',
  '¿Cómo piensa Jorge Nieto reformar el sistema de salud?',
];

// Traducciones de textos de UI
const T = {
  es: {
    navHome: 'Inicio', navCands: 'Candidatos', navChat: 'Asistente', navCalc: 'Calculadora',
    disclaimer: 'Plataforma de demostración · Las posturas mostradas son ilustrativas, basadas en declaraciones y planes públicos disponibles.',
    homeTitle: 'Tu brújula para las elecciones 2026',
    homeSub: 'Consulta los planes de gobierno, compara posturas y descubre qué candidato se acerca más a tus ideas.',
    cardChatTitle: 'Asistente Electoral', cardCalcTitle: 'Calculadora de Afinidad',
    cardChatDesc: 'Pregunta en lenguaje natural. Contrasto lo que prometen en su plan, lo que declaran en entrevistas y lo que opina la ciudadanía.',
    cardCalcDesc: 'Responde 8 preguntas sobre los temas del país y descubre qué candidato comparte tus posiciones.',
    cardChatBtn: 'Consultar ahora', cardCalcBtn: 'Calcular afinidad',
    homeCandsTitle: 'Candidatos en carrera',
    candsTitle: 'Candidatos', candsSub: 'Conoce el perfil y las propuestas de cada candidato.',
    verPerfil: 'Ver perfil →',
    perfilBack: '← Volver a candidatos',
    perfilPropTitle: 'Propuestas por tema', propTopicCol: 'Tema', propPropCol: 'Postura',
    chatTitle: 'Asistente Electoral',
    chatSub: 'Pregunta sobre planes, propuestas y declaraciones de los candidatos.',
    chatPlaceholder: 'Escribe tu pregunta…', chatSend: 'Enviar',
    sourcesLabel: 'Fuentes consultadas', botAvatar: 'BE', userAvatar: 'Tú',
    statusQuery: 'Consultando base de conocimiento…', statusGen: 'Generando respuesta…',
    noConn: 'No pude conectar con el servidor.',
    calcTitle: 'Calculadora de Afinidad',
    calcSub: 'Responde las 8 preguntas y descubre tu candidato más afín.',
    calcNext: 'Siguiente →', calcPrev: '← Anterior',
    calcResult: 'Ver resultado', calcRestart: 'Volver a empezar',
    calcResultTitle: 'Tu afinidad electoral', calcBreakTitle: 'Detalle por tema',
    noMatch: 'Sin coincidencia',
    footerBrand: 'Brújula Electoral 2026',
    footerNote: 'Herramienta cívica independiente · Solo con fines informativos',
    themeLight: 'Cívico', themeDark: 'Editorial', langEs: 'ES', langQu: 'QU',
    sentiment: 'Aprobación en redes',
  },
  qu: {
    navHome: 'Qallariy', navCands: 'Candidatokuna', navChat: 'Tapukuy', navCalc: 'Tupuy',
    disclaimer: 'Kay musuq kutichiy · Ima rimaykuna qhawanankupaq, mana chiqaq kamachiychu.',
    homeTitle: 'Kay brújulawan 2026 eleccionpaq',
    homeSub: 'Candidatokuna imata nisqankuta rimanki, tupuykiwan ima candidato hinallan kasqaykita riqsinki.',
    cardChatTitle: 'Tapukuy', cardCalcTitle: 'Afinidad tupuy',
    cardChatDesc: 'Rimaypi tapukuy. Imata candidatokuna nisqankuta, imasqankutawan chinkachini.',
    cardCalcDesc: '8 tapukuyta kutichiy hinaspan ima candidato hinallan kasqaykita riqsinki.',
    cardChatBtn: 'Tapukuy', cardCalcBtn: 'Tupuyta qallariy',
    homeCandsTitle: 'Candidatokuna',
    candsTitle: 'Candidatokuna', candsSub: 'Sapa candidatopa kawsayninta imata nisqankutawan riqsiy.',
    verPerfil: 'Riqsiy →',
    perfilBack: '← Kutiy',
    perfilPropTitle: 'Imakunapi munanku', propTopicCol: 'Tukuy ima', propPropCol: 'Ima nisqan',
    chatTitle: 'Tapukuy',
    chatSub: 'Candidatokuna haqaypi imata nisqankuta tapukuy.',
    chatPlaceholder: 'Tapukuykita qillqay…', chatSend: 'Kachamuy',
    sourcesLabel: 'Yachay mamakuna', botAvatar: 'BE', userAvatar: 'Qam',
    statusQuery: 'Maskaspa…', statusGen: 'Kutichispa…',
    noConn: 'Servidor watukuyta mana atirqanichu.',
    calcTitle: 'Afinidad tupuy',
    calcSub: '8 tapukuykunata kutichiy hinaspan riqsinki.',
    calcNext: 'Hawkaman →', calcPrev: '← Qipaman',
    calcResult: 'Tupuna qhawana', calcRestart: 'Qayna qallariy',
    calcResultTitle: 'Chayniykin electoral', calcBreakTitle: 'Tukuy imapi tupuna',
    noMatch: 'Mana tupanchu',
    footerBrand: 'Brújula Electoral 2026',
    footerNote: 'Herramienta cívica independiente · Yachachiy hinallan',
    themeLight: 'Cívico', themeDark: 'Editorial', langEs: 'ES', langQu: 'QU',
    sentiment: 'Aprobación',
  }
};

// ─── ESTADO ───────────────────────────────────────────────────────────────────

const state = {
  screen:     'home',
  lang:       'es',
  theme:      'civic',
  candidate:  null,
  topicIdx:   0,
  answers:    {},
  showResult: false,
  streaming:  false,
  messages:   [],
  chatHistory:[],
};

// ─── HELPERS ──────────────────────────────────────────────────────────────────

const el  = id  => document.getElementById(id);
const t   = key => T[state.lang][key] ?? key;
const gc  = id  => CANDS.find(c => c.id === id);
const tl  = tp  => state.lang === 'qu' ? tp.qu : tp.es;

function staticUrl(relPath) {
  return `/static/${String(relPath).replace(/^\/+/, '')}`;
}

function avatarHtml(c, sizeClass = 'avatar-lg') {
  const src = staticUrl(c.photo || '');
  return `
    <span class="avatar ${sizeClass} avatar-photo cv-${c.id}">
      <img src="${esc(src)}" alt="${esc(c.name)}"
           onerror="this.closest('.avatar-photo').classList.add('is-fallback');this.remove();">
      <span class="avatar-fallback">${esc(c.initials)}</span>
    </span>`;
}

function partyLogoHtml(c, sizeClass = 'party-logo-md') {
  const src = staticUrl(c.partyLogo || '');
  return `
    <span class="party-logo ${sizeClass} cv-${c.id}">
      <img src="${esc(src)}" alt="${esc(c.party)}"
           onerror="this.closest('.party-logo').classList.add('is-fallback');this.remove();">
      <span class="party-logo-fallback">${esc(c.party.slice(0, 2))}</span>
    </span>`;
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function fmt(text) {
  let h = esc(text);
  h = h.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  h = h.replace(/\[(\d+)\]/g, '<span class="cite">[$1]</span>');
  const lines = h.split('\n').filter(l => l.trim());
  return lines.map(l => {
    if (/^\s*(📋|🎤|💬|##?)/.test(l)) return '<h4>' + l.replace(/^#{1,3}\s*/, '').trim() + '</h4>';
    return '<p>' + l.trim() + '</p>';
  }).join('');
}

function fuentesHtml(fuentes) {
  if (!fuentes || !fuentes.length) return '';
  const items = fuentes.map(f => {
    if (typeof f === 'string') return `<li>${esc(f)}</li>`;
    const ref  = esc(f.ref || f.titulo || '');
    const tipo = f.tipo ? `[${esc(f.tipo)}] ` : '';
    const url  = f.url || '';
    const link = url.startsWith('http')
      ? `<a href="${esc(url)}" target="_blank" rel="noopener">${ref}</a>` : ref;
    return `<li>${tipo}${link}</li>`;
  }).join('');
  return `<details class="chat-sources"><summary>${t('sourcesLabel')} (${fuentes.length})</summary><ol>${items}</ol></details>`;
}

// ─── TEMA & LENGUA ────────────────────────────────────────────────────────────

function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.dataset.theme = theme === 'editorial' ? 'editorial' : '';
  document.querySelectorAll('[data-theme-toggle]').forEach(b =>
    b.classList.toggle('active', b.dataset.themeToggle === theme));
}

function applyLang(lang) {
  state.lang = lang;
  document.querySelectorAll('[data-lang-toggle]').forEach(b =>
    b.classList.toggle('active', b.dataset.langToggle === lang));
  // update static masthead text that references T
  const disc = el('disclaimer-text');
  if (disc) disc.textContent = t('disclaimer');
  updateNavLabels();
  render();
}

// ─── ROUTING ──────────────────────────────────────────────────────────────────

function goScreen(name) {
  state.screen = name;
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const scr = el('screen-' + name);
  if (scr) scr.classList.add('active');
  const comp = el('composer');
  if (comp) comp.classList.toggle('visible', name === 'chat');
  window.scrollTo(0, 0);
  render();
}

const goHome  = ()  => goScreen('home');
const goCands = ()  => goScreen('candidatos');
const goChat  = ()  => goScreen('chat');
const goCalc  = ()  => { state.topicIdx = 0; state.answers = {}; state.showResult = false; goScreen('calc'); };

function openCand(id) {
  state.candidate = id;
  goScreen('perfil');
}

// ─── NAV ─────────────────────────────────────────────────────────────────────

function updateNavLabels() {
  document.querySelectorAll('[data-nav-label]').forEach(el => {
    el.textContent = t(el.dataset.navLabel);
  });
}

function updateNavActive() {
  const s = state.screen;
  document.querySelectorAll('[data-nav]').forEach(b => {
    const match = b.dataset.nav === s ||
      (s === 'perfil' && b.dataset.nav === 'candidatos');
    b.classList.toggle('active', match);
  });
}

// ─── RENDER: HOME ─────────────────────────────────────────────────────────────

function renderHome() {
  const scr = el('screen-home');
  if (!scr) return;
  scr.innerHTML = `
    <div class="home-hero">
      <h1 class="home-hero-title">${t('homeTitle')}</h1>
      <p class="home-hero-sub">${t('homeSub')}</p>
    </div>
    <div class="home-cards">
      <div class="card card-btn" data-action="goChat">
        <div class="home-card-icon">💬</div>
        <div class="home-card-title text-serif">${t('cardChatTitle')}</div>
        <div class="home-card-desc">${t('cardChatDesc')}</div>
        <button class="btn btn-primary btn-sm" tabindex="-1">${t('cardChatBtn')}</button>
      </div>
      <div class="card card-btn" data-action="goCalc">
        <div class="home-card-icon">🧭</div>
        <div class="home-card-title text-serif">${t('cardCalcTitle')}</div>
        <div class="home-card-desc">${t('cardCalcDesc')}</div>
        <button class="btn btn-primary btn-sm" tabindex="-1">${t('cardCalcBtn')}</button>
      </div>
    </div>
    <div class="home-cands-title text-serif">${t('homeCandsTitle')}</div>
    <div class="home-cands-grid">
      ${CANDS.map(c => `
        <button class="home-cand-chip cv-${c.id}" data-cand="${c.id}">
          ${avatarHtml(c, 'avatar-chip')}
          ${c.name.split(' ').slice(0, 2).join(' ')}
        </button>`).join('')}
    </div>`;
}

// ─── RENDER: CANDIDATOS ───────────────────────────────────────────────────────

function renderCands() {
  const scr = el('screen-candidatos');
  if (!scr) return;
  scr.innerHTML = `
    <div class="section-head">
      <h2 class="section-title">${t('candsTitle')}</h2>
      <p class="section-sub">${t('candsSub')}</p>
    </div>
    <div class="cands-grid">
      ${CANDS.map(c => `
        <div class="cand-card cv-${c.id}" data-cand="${c.id}">
          <div class="cand-card-hd">
            ${avatarHtml(c, 'avatar-lg')}
            <div>
              <div class="cand-card-name">${c.name}</div>
              <div class="cand-card-partyline">
                ${partyLogoHtml(c)}
                <span>${c.party}</span>
              </div>
            </div>
          </div>
          <div class="cand-card-bio">${c.bio}</div>
          <div class="cand-card-ft">
            <span class="pill pill-accent">👍 ${c.sent.pos}%</span>
            <span class="text-sm text-muted">${t('verPerfil')}</span>
          </div>
        </div>`).join('')}
    </div>`;
}

// ─── RENDER: PERFIL ───────────────────────────────────────────────────────────

function renderPerfil() {
  const scr = el('screen-perfil');
  if (!scr || !state.candidate) return;
  const c = gc(state.candidate);
  if (!c) return;

  const rows = TOPICS.map((tp, i) => {
    const optIdx = STANCE[c.id][i];
    return `<tr>
      <td class="topic-cell">${tl(tp)}</td>
      <td>${esc(QUESTIONS[i].opts[optIdx])}</td>
    </tr>`;
  }).join('');

  scr.innerHTML = `
    <button class="back-btn" data-action="goCands">${t('perfilBack')}</button>
    <div class="perfil-hero cv-${c.id}">
      ${avatarHtml(c, 'avatar-xl')}
      <div>
        <div class="perfil-name">${c.name}</div>
        <div class="perfil-partywrap">
          ${partyLogoHtml(c, 'party-logo-lg')}
          <div>
            <div class="perfil-party">${c.party}</div>
            <div class="perfil-party-note">Logo del partido</div>
          </div>
        </div>
        <p class="perfil-bio">${c.bio}</p>
      </div>
    </div>
    <hr class="divider">
    <div class="propuestas-section">
      <div class="propuestas-title text-serif">${t('perfilPropTitle')}</div>
      <table class="propuestas-table">
        <thead><tr><th style="width:110px">${t('propTopicCol')}</th><th>${t('propPropCol')}</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

// ─── RENDER: CHAT ─────────────────────────────────────────────────────────────

function renderChat() {
  const scr = el('screen-chat');
  if (!scr) return;

  const exHtml = state.messages.length === 0 ? `
    <div class="chat-examples">
      ${EXAMPLES.map(ex => `<button class="chat-ex-btn" data-example="${esc(ex)}">${esc(ex)}</button>`).join('')}
    </div>` : '';

  const msgsHtml = state.messages.map(m => {
    if (m.role === 'user') return `
      <div class="chat-msg user">
        <span class="avatar">${t('userAvatar')}</span>
        <div class="chat-bubble">${esc(m.text)}</div>
      </div>`;
    // bot — may be typing placeholder or real content
    const body = m.typing
      ? `<div class="typing-dots"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></div>`
      : `${fmt(m.text || '')}${m.streaming ? '<span class="cursor"></span>' : ''}${fuentesHtml(m.fuentes)}`;
    return `
      <div class="chat-msg bot">
        <span class="avatar">${t('botAvatar')}</span>
        <div class="chat-bubble">${body}</div>
      </div>`;
  }).join('');

  scr.innerHTML = `
    <div class="chat-wrap">
      <div class="chat-header">
        <div class="chat-title text-serif">${t('chatTitle')}</div>
        <div class="chat-subtitle">${t('chatSub')}</div>
      </div>
      ${exHtml}
      <div class="chat-msgs" id="chat-msgs">${msgsHtml}</div>
    </div>`;

  const msgs = el('chat-msgs');
  if (msgs) msgs.scrollTop = msgs.scrollHeight;

  const input = el('composer-input');
  if (input) input.placeholder = t('chatPlaceholder');
  const send = el('composer-send');
  if (send) send.textContent = t('chatSend');
}

// ─── RENDER: CALC ─────────────────────────────────────────────────────────────

function renderCalc() {
  const scr = el('screen-calc');
  if (!scr) return;
  if (state.showResult) { renderResult(scr); return; }

  const answered = TOPICS.filter(tp => state.answers[tp.key] !== undefined).length;
  const pct = Math.round(answered / TOPICS.length * 100);
  const q   = QUESTIONS[state.topicIdx];
  const tp  = TOPICS[state.topicIdx];
  const curAns = state.answers[tp.key];
  const isLast  = state.topicIdx === TOPICS.length - 1;
  const allDone = answered === TOPICS.length;

  const tabs = TOPICS.map((tp2, i) => {
    const cls = i === state.topicIdx        ? 'calc-tab active'
               : state.answers[tp2.key] !== undefined ? 'calc-tab answered'
               : 'calc-tab';
    return `<button class="${cls}" data-topic-idx="${i}">${tl(tp2)}</button>`;
  }).join('');

  const LETTERS = ['A', 'B', 'C', 'D'];
  const opts = q.opts.map((opt, i) => `
    <button class="q-option${curAns === i ? ' selected' : ''}" data-opt="${i}">
      <span class="q-letter">${LETTERS[i]}</span>
      <span>${esc(opt)}</span>
    </button>`).join('');

  const showResultBtn = allDone;
  const nextDisabled  = curAns === undefined ? 'disabled' : '';

  scr.innerHTML = `
    <div class="calc-wrap">
      <div class="section-head">
        <h2 class="section-title">${t('calcTitle')}</h2>
        <p class="section-sub">${t('calcSub')}</p>
      </div>
      <div class="calc-progress">
        <div class="calc-progress-bar">
          <div class="calc-progress-fill" style="width:${pct}%"></div>
        </div>
        <span class="calc-progress-label">${answered}/${TOPICS.length}</span>
      </div>
      <div class="calc-tabs">${tabs}</div>
      <div class="q-card">
        <div class="q-topic-label">${tl(tp)}</div>
        <div class="q-text">${esc(q.text)}</div>
        <div class="q-options">${opts}</div>
      </div>
      <div class="calc-nav">
        <button class="btn btn-ghost btn-sm" data-action="calcPrev"
          ${state.topicIdx === 0 ? 'disabled' : ''}>${t('calcPrev')}</button>
        ${showResultBtn
          ? `<button class="btn btn-primary btn-sm" data-action="calcResult">${t('calcResult')}</button>`
          : `<button class="btn btn-primary btn-sm" data-action="calcNext" ${nextDisabled}
              ${isLast && !allDone ? '' : ''}>${t('calcNext')}</button>`}
      </div>
    </div>`;
}

function renderResult(scr) {
  const scores = CANDS.map(c => {
    const matches = TOPICS.filter((tp, i) => state.answers[tp.key] === STANCE[c.id][i]);
    return { c, matches, score: matches.length };
  }).sort((a, b) => b.score - a.score);

  const rankHtml = scores.map((s, i) => `
    <div class="result-item cv-${s.c.id} ${i === 0 ? 'rank-1' : ''}">
      <span class="result-rank">${i + 1}</span>
      <span class="avatar">${s.c.initials}</span>
      <div class="result-info">
        <div class="result-name">${s.c.name}</div>
        <div class="result-party">${s.c.party}</div>
      </div>
      <div class="result-score-wrap">
        <div class="result-bar">
          <div class="result-bar-fill" style="width:${Math.round(s.score / TOPICS.length * 100)}%"></div>
        </div>
        <span class="result-pct">${Math.round(s.score / TOPICS.length * 100)}%</span>
      </div>
    </div>`).join('');

  const breakHtml = TOPICS.map((tp, i) => {
    const userOpt = state.answers[tp.key];
    const matches = CANDS.filter(c => STANCE[c.id][i] === userOpt);
    const chips = matches.length
      ? matches.map(c => `<span class="breakdown-chip cv-${c.id}">${c.name.split(' ')[0]}</span>`).join('')
      : `<span class="text-muted text-sm">${t('noMatch')}</span>`;
    return `
      <div class="breakdown-row">
        <span class="breakdown-topic">${tl(tp)}</span>
        <div class="breakdown-chips">${chips}</div>
      </div>`;
  }).join('');

  scr.innerHTML = `
    <div class="calc-wrap">
      <div class="section-head">
        <h2 class="section-title">${t('calcResultTitle')}</h2>
      </div>
      <div class="result-list">${rankHtml}</div>
      <hr class="divider">
      <div class="propuestas-title text-serif" style="margin-bottom:14px">${t('calcBreakTitle')}</div>
      <div class="breakdown-grid">${breakHtml}</div>
      <div style="margin-top:24px;display:flex;gap:10px;flex-wrap:wrap">
        <button class="btn btn-secondary btn-sm" data-action="goCalc">${t('calcRestart')}</button>
        <button class="btn btn-primary btn-sm" data-action="goChat">${t('cardChatBtn')}</button>
      </div>
    </div>`;
}

// ─── RENDER MASTER ────────────────────────────────────────────────────────────

function render() {
  updateNavActive();
  const s = state.screen;
  if (s === 'home')       renderHome();
  if (s === 'candidatos') renderCands();
  if (s === 'perfil')     renderPerfil();
  if (s === 'chat')       renderChat();
  if (s === 'calc')       renderCalc();
}

// ─── CHAT: SSE STREAMING ──────────────────────────────────────────────────────

async function enviarMensaje(texto) {
  if (!texto.trim() || state.streaming) return;
  state.streaming = true;
  const sendBtn = el('composer-send');
  if (sendBtn) sendBtn.disabled = true;

  state.messages.push({ role: 'user', text: texto.trim() });
  const botIdx = state.messages.length;
  state.messages.push({ role: 'bot', text: '', typing: true, streaming: true, fuentes: [] });
  renderChat();

  // get direct reference to the streaming bubble for efficient updates
  const msgs = el('chat-msgs');
  let bbl = msgs ? msgs.querySelector('.chat-msg.bot:last-child .chat-bubble') : null;

  state.chatHistory.push({ role: 'user', content: texto.trim() });

  let accumulated = '';
  let finalAnswer = '';

  try {
    const resp = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pregunta: texto.trim(), historial: state.chatHistory.slice(-6), lang: state.lang }),
    });
    if (!resp.ok || !resp.body) throw new Error(`HTTP ${resp.status}`);

    const reader  = resp.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const lines = buf.split('\n');
      buf = lines.pop();

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        let ev;
        try { ev = JSON.parse(line.slice(6)); } catch { continue; }

        if (ev.status) {
          if (bbl) bbl.innerHTML = `<p class="status-msg">${esc(ev.status)}</p>`;
        } else if (ev.token) {
          accumulated += ev.token;
          if (bbl) {
            bbl.innerHTML = fmt(accumulated) + '<span class="cursor"></span>';
            if (msgs) msgs.scrollTop = msgs.scrollHeight;
          }
        } else if (ev.done) {
          finalAnswer = ev.answer || accumulated;
          const fuentes = ev.fuentes || [];
          if (bbl) bbl.innerHTML = fmt(finalAnswer) + fuentesHtml(fuentes);
          state.messages[botIdx] = { role: 'bot', text: finalAnswer, streaming: false, fuentes };
          state.chatHistory.push({ role: 'assistant', content: finalAnswer });
          if (state.chatHistory.length > 12) state.chatHistory = state.chatHistory.slice(-12);
        } else if (ev.error) {
          if (bbl) bbl.innerHTML = `<p>⚠️ ${esc(ev.error)}</p>`;
          state.messages[botIdx] = { role: 'bot', text: ev.error, streaming: false };
        }
      }
    }
  } catch (err) {
    const msg = t('noConn');
    if (bbl) bbl.innerHTML = `<p>⚠️ ${esc(msg)}</p>`;
    state.messages[botIdx] = { role: 'bot', text: msg, streaming: false };
  } finally {
    state.streaming = false;
    if (sendBtn) { sendBtn.disabled = false; }
    if (msgs) msgs.scrollTop = msgs.scrollHeight;
  }
}

// ─── EVENT DELEGATION ─────────────────────────────────────────────────────────

document.addEventListener('click', e => {
  const btn = e.target.closest('[data-action],[data-nav],[data-cand],[data-example],[data-opt],[data-topic-idx],[data-theme-toggle],[data-lang-toggle]');
  if (!btn || btn.disabled) return;

  const { action, nav, cand, example, opt, topicIdx, themeToggle, langToggle } = btn.dataset;

  if (nav) {
    ({ home: goHome, candidatos: goCands, chat: goChat, calc: goCalc }[nav] || (() => {}))();
  }
  if (action) {
    const actions = {
      goHome, goCands, goChat, goCalc,
      calcNext:   () => { if (state.topicIdx < TOPICS.length - 1) { state.topicIdx++; renderCalc(); } },
      calcPrev:   () => { if (state.topicIdx > 0) { state.topicIdx--; renderCalc(); } },
      calcResult: () => { state.showResult = true; renderCalc(); },
    };
    (actions[action] || (() => {}))();
  }
  if (cand) openCand(cand);
  if (example) {
    if (state.screen !== 'chat') {
      goChat();
      // small delay so chat screen is rendered before submitting
      setTimeout(() => enviarMensaje(example), 50);
    } else {
      enviarMensaje(example);
    }
    const input = el('composer-input');
    if (input) input.value = '';
  }
  if (opt !== undefined && state.screen === 'calc') {
    state.answers[TOPICS[state.topicIdx].key] = parseInt(opt);
    renderCalc();
  }
  if (topicIdx !== undefined) {
    state.topicIdx = parseInt(topicIdx);
    renderCalc();
  }
  if (themeToggle) applyTheme(themeToggle);
  if (langToggle)  applyLang(langToggle);
});

// ─── COMPOSER ─────────────────────────────────────────────────────────────────

function setupComposer() {
  const input   = el('composer-input');
  const sendBtn = el('composer-send');
  if (!input || !sendBtn) return;

  const trySubmit = () => {
    const text = input.value.trim();
    if (text && !state.streaming) {
      input.value = '';
      input.style.height = 'auto';
      enviarMensaje(text);
    }
  };

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); trySubmit(); }
  });
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    sendBtn.disabled = !input.value.trim() || state.streaming;
  });
  sendBtn.addEventListener('click', trySubmit);
}

// ─── INIT ─────────────────────────────────────────────────────────────────────

function init() {
  applyTheme('civic');
  setupComposer();
  goScreen('home');
}

document.addEventListener('DOMContentLoaded', init);
