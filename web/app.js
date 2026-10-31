// Local navigation, reveal effects, and program catalogue filters.
const menuToggle = document.querySelector('.menu-toggle');
const mainNav = document.querySelector('#main-nav');

document.documentElement.classList.add('js');

const revealItems = document.querySelectorAll(
  '.intro-grid, .campaign-card, .activity-summary, .process-item, .tools-row, .program-card, .prompt-card, .responsibility-cards article, .references-list article'
);

if ('IntersectionObserver' in window) {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  revealItems.forEach((item, index) => {
    item.classList.add('reveal');
    item.style.transitionDelay = `${Math.min(index % 4, 3) * 65}ms`;
    revealObserver.observe(item);
  });
} else {
  revealItems.forEach((item) => item.classList.add('is-visible'));
}

menuToggle?.addEventListener('click', () => {
  const isOpen = menuToggle.getAttribute('aria-expanded') === 'true';
  menuToggle.setAttribute('aria-expanded', String(!isOpen));
  mainNav?.classList.toggle('is-open', !isOpen);
});

mainNav?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    mainNav.classList.remove('is-open');
    menuToggle?.setAttribute('aria-expanded', 'false');
  });
});

const searchInput = document.querySelector('#program-search');
const programCards = [...document.querySelectorAll('.program-card')];
const filterButtons = [...document.querySelectorAll('.filter-button')];
const resultsCount = document.querySelector('#results-count');
const noResults = document.querySelector('#no-results');
let activeFilter = 'todos';

function updatePrograms() {
  const query = searchInput?.value.trim().toLocaleLowerCase('es') ?? '';
  let visibleCount = 0;

  programCards.forEach((card) => {
    const matchesFilter = activeFilter === 'todos' || card.dataset.area === activeFilter;
    const matchesQuery = (card.dataset.search ?? '').toLocaleLowerCase('es').includes(query);
    const isVisible = matchesFilter && matchesQuery;
    card.hidden = !isVisible;
    if (isVisible) visibleCount += 1;
  });

  if (resultsCount) {
    resultsCount.textContent = `${visibleCount} ${visibleCount === 1 ? 'programa' : 'programas'}`;
  }
  if (noResults) noResults.hidden = visibleCount !== 0;
}

searchInput?.addEventListener('input', updatePrograms);
filterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    activeFilter = button.dataset.filter ?? 'todos';
    filterButtons.forEach((item) => {
      const isActive = item === button;
      item.classList.toggle('is-active', isActive);
      item.setAttribute('aria-pressed', String(isActive));
    });
    updatePrograms();
  });
});

const promptSearch = document.querySelector('#prompt-search');
const promptCards = [...document.querySelectorAll('.prompt-card')];
const promptFilterButtons = [...document.querySelectorAll('.prompt-filter-button')];
const promptCount = document.querySelector('#prompt-count');
const noPromptResults = document.querySelector('#no-prompt-results');
let activePromptFilter = 'todos';

function updatePromptLibrary() {
  const query = promptSearch?.value.trim().toLocaleLowerCase('es') ?? '';
  let visibleCount = 0;

  promptCards.forEach((card) => {
    const matchesFilter = activePromptFilter === 'todos' || card.dataset.area === activePromptFilter || card.dataset.type === activePromptFilter;
    const matchesQuery = (card.dataset.search ?? '').toLocaleLowerCase('es').includes(query);
    const isVisible = matchesFilter && matchesQuery;
    card.hidden = !isVisible;
    if (isVisible) visibleCount += 1;
  });

  if (promptCount) {
    promptCount.textContent = `${visibleCount} ${visibleCount === 1 ? 'prompt documentado' : 'prompts documentados'}`;
  }
  if (noPromptResults) noPromptResults.hidden = visibleCount !== 0;
}

promptSearch?.addEventListener('input', updatePromptLibrary);
promptFilterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    activePromptFilter = button.dataset.filter ?? 'todos';
    promptFilterButtons.forEach((item) => {
      const isActive = item === button;
      item.classList.toggle('is-active', isActive);
      item.setAttribute('aria-pressed', String(isActive));
    });
    updatePromptLibrary();
  });
});

document.querySelectorAll('.copy-prompt').forEach((button) => {
  const originalLabel = button.textContent;
  let resetTimer = 0;

  button.addEventListener('click', async () => {
    const quote = button.closest('.prompt-card')?.querySelector('.prompt-quote');
    if (!quote) return;
    const text = quote.textContent.replace(/\s+/g, ' ').trim();
    let copied = false;

    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
        copied = true;
      }
    } catch {
      copied = false;
    }

    if (!copied) {
      const helper = document.createElement('textarea');
      helper.value = text;
      helper.setAttribute('readonly', '');
      helper.style.position = 'fixed';
      helper.style.opacity = '0';
      document.body.appendChild(helper);
      helper.select();
      try {
        copied = document.execCommand('copy');
      } catch {
        copied = false;
      }
      helper.remove();
    }

    button.textContent = copied ? 'Copiado ✓' : 'No disponible';
    button.classList.toggle('is-copied', copied);
    window.clearTimeout(resetTimer);
    resetTimer = window.setTimeout(() => {
      button.textContent = originalLabel;
      button.classList.remove('is-copied');
    }, 1800);
  });
});

async function loadPublishedMediaLinks() {
  try {
    const response = await fetch(new URL('media-links.json', document.baseURI), { cache: 'no-store' });
    if (!response.ok) return;

    const mediaConfig = await response.json();
    const driveUrl = getSafeHttpsUrl(mediaConfig.driveFolderUrl);
    const driveLink = document.querySelector('#drive-folder-link');
    const drivePending = document.querySelector('#drive-link-pending');

    if (driveUrl && driveLink && drivePending) {
      driveLink.href = driveUrl;
      driveLink.hidden = false;
      drivePending.hidden = true;
    }

    document.querySelectorAll('[data-media-id]').forEach((slot) => {
      const url = getSafeHttpsUrl(mediaConfig.products?.[slot.dataset.mediaId]);
      const link = slot.querySelector('a');
      const pending = slot.querySelector('small');
      if (!url || !link || !pending) return;

      link.href = url;
      link.hidden = false;
      pending.hidden = true;
    });
  } catch {
    // Local file previews work without the optional hosted-media configuration.
  }
}

function getSafeHttpsUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === 'https:' ? url.href : '';
  } catch {
    return '';
  }
}

loadPublishedMediaLinks();

/* ------------------------------------------------------------------ */
/* Examen final · productos interactivos                              */
/* Reglas escritas a mano: sin servicios externos y sin datos         */
/* inventados. Todo dato institucional viene de fuentes verificadas   */
/* y todo contenido ficticio va rotulado como tal.                    */
/* ------------------------------------------------------------------ */

// 1) Infografía interactiva de fundamentos de programación (IS · TP).
const infraConcepts = {
  variable: {
    title: 'Variable',
    text: 'Un espacio con nombre donde el programa guarda un dato.',
    code: 'edad = 16'
  },
  tipos: {
    title: 'Tipos de datos',
    text: 'Cada dato tiene un tipo: texto, número o verdadero/falso.',
    code: 'nombre = "Ana"   # texto\nnota = 4.5         # número\naprobado = True    # booleano'
  },
  condicional: {
    title: 'Condicional',
    text: 'Decide qué bloque de código se ejecuta según una condición.',
    code: 'if nota >= 3.0:\n    print("Aprueba")\nelse:\n    print("Refuerza")'
  },
  ciclo: {
    title: 'Ciclo',
    text: 'Repite instrucciones mientras una condición se cumpla.',
    code: 'for i in range(1, 6):\n    print("Reel", i, "listo")'
  },
  funcion: {
    title: 'Función',
    text: 'Bloque de código reutilizable que recibe datos y devuelve un resultado.',
    code: 'def saludo(nombre):\n    return "Hola, " + nombre'
  },
  algoritmo: {
    title: 'Algoritmo',
    text: 'Secuencia ordenada de pasos para resolver un problema.',
    code: 'pasos = ["leer", "procesar", "responder"]\nfor paso in pasos:\n    ejecutar(paso)'
  }
};

const infraChips = [...document.querySelectorAll('.infra-chip')];
const infraPanel = document.querySelector('.infra-panel');

infraChips.forEach((chip) => {
  chip.addEventListener('click', () => {
    const concept = infraConcepts[chip.dataset.concept];
    if (!concept || !infraPanel) return;

    infraChips.forEach((item) => {
      const isActive = item === chip;
      item.classList.toggle('is-active', isActive);
      item.setAttribute('aria-pressed', String(isActive));
    });

    const title = infraPanel.querySelector('.infra-title');
    const text = infraPanel.querySelector('.infra-text');
    const code = infraPanel.querySelector('.infra-code');
    if (title) title.textContent = concept.title;
    if (text) text.textContent = concept.text;
    if (code) {
      code.textContent = concept.code;
      code.animate?.([{ opacity: 0.25 }, { opacity: 1 }], { duration: 220 });
    }
  });
});

// 2) Chat conversacional con reglas (MKT · TP): solo datos verificados.
const CHAT_OFFICIAL_CHANNELS = 'PBX (601) 746 8757, la sección de admisiones en nuevaamerica.edu.co/admisiones/ o Coordinación de Virtualidad.';
const CHAT_FALLBACK = `Esa información no está en mi base verificada y no invento datos 🙂. Confírmala por los canales oficiales de FESNA: ${CHAT_OFFICIAL_CHANNELS} (Recuerda que soy una simulación con reglas escritas por el estudiante, no un asistente oficial.)`;

const chatRules = [
  {
    re: /titul|t[eí]cnico|tecn[oó]logo|t\.p\.|profesional universitario|(qu[eé]|los)\s+(da|dice)\s+la\s+ruta/,
    answer: 'La ruta otorga tres títulos en cascada: (1) Técnico Profesional en Comercialización y Comunicación Publicitaria (Res. 011477 de 2026, 49 créditos), (2) Tecnología en Gestión Comercial y Publicidad (Res. 011476 de 2026, 82 créditos) y (3) Profesional Universitario en Marketing y Publicidad (Res. 011475 de 2026, 133 créditos, 8 periodos).'
  },
  {
    re: /modalidad|presencial|virtual/,
    answer: 'El programa profesional en Marketing y Publicidad se ofrece en modalidad presencial y virtual. Para horarios específicos te recomiendo los canales oficiales, porque los detalles de calendario los consulta directamente la universidad.'
  },
  {
    re: /snies|registro calificado|resoluci[oó]n/,
    answer: 'SNIES verificados: Marketing y Publicidad 119242 y 119243 (Res. 011475 del 30 de abril de 2026); la tecnología y el técnico profesional tienen registro con las Resoluciones 011476 y 011477 de la misma fecha. Puedes consultarlos en el Directorio de Instituciones y Programas SNIES.'
  },
  {
    re: /cr[eé]dito|periodo|semestre|duraci[oó]n|cu[aá]nto\s+(dura|tarda)/,
    answer: 'El plan de estudios suma 49 créditos en el técnico profesional, 82 en la tecnología y 133 en el profesional, que se cursa en 8 periodos académicos. Son datos del registro calificado, no estimaciones.'
  },
  {
    re: /costo|matr[ií]cula|pago|precio|beca|financiaci[oó]n|valor\s+(del\s+)?(programa|semestre)/,
    answer: 'Los costos de matrícula y las opciones de financiación no forman parte de mi información verificada, así que no puedo darte cifras. Confírmalas por los canales oficiales: ' + CHAT_OFFICIAL_CHANNELS
  },
  {
    re: /requisito|inscribirme|inscripci[oó]n|admi[sb]|[cç]omo\s+ingreso|documento/,
    answer: 'Los requisitos y el proceso de admisión los maneja directamente el equipo de admisiones y no los incluyo para no darte una versión desactualizada. Escríbeles por los canales oficiales: ' + CHAT_OFFICIAL_CHANNELS
  },
  {
    re: /contacto|tel[eé]fono|correo|pbx|whatsapp|sede|d[oó]nde\s+(llamo|escribo)/,
    answer: 'Puedes comunicarte por la PBX (601) 746 8757 o escribir desde la sección de admisiones en nuevaamerica.edu.co/admisiones/. Y para el catálogo SNIES puedes consultar siempre el directorio del Ministerio de Educación.'
  },
  {
    re: /hola|buenas|buenos|saludos|hey|qui[eé]n\s+eres/,
    answer: '¡Hola! Soy una simulación de atención al cliente hecha con reglas escritas por el estudiante. Puedo contarte sobre títulos, modalidad, SNIES, créditos y duración de la ruta de comercialización y publicidad 🙂 Para lo demás te remito a los canales oficiales.'
  },
  {
    re: /gracias|chao|adi[oó]s|bye/,
    answer: '¡Con gusto! Recuerda que cualquier dato específico (costos, fechas de admisión) siempre conviene confirmarlo por los canales oficiales de FESNA. ¡Éxitos en tu proceso 🎓'
  },
  {
    re: /andrea|buyer\s*persona|mkt|marketing|publicidad/,
    answer: 'Andrea es nuestra buyer persona ficticia (26 años, aspirante a la ruta): la usamos solo como ejemplo didáctico. Si preguntas por el programa de Marketing y Publicidad, puedo darte SNIES, créditos, duración y modalidad verificadas.'
  }
];

// Cableado del chat (reglas locales, sin servicios externos).
const chatLog = document.querySelector('#chat-log');
const chatForm = document.querySelector('#chat-form');
const chatInput = document.querySelector('#chat-input');
const chatQuickButtons = [...document.querySelectorAll('.chat-quick button')];

function addChatBubble(kind, text) {
  if (!chatLog) return null;
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${kind}`;
  bubble.textContent = text;
  chatLog.appendChild(bubble);
  chatLog.scrollTop = chatLog.scrollHeight;
  return bubble;
}

function findChatAnswer(question) {
  const normalized = question.toLocaleLowerCase('es');
  const rule = chatRules.find((item) => item.re.test(normalized));
  return rule ? rule.answer : CHAT_FALLBACK;
}

function sendChatMessage(question) {
  const clean = question.trim();
  if (!clean) return;
  addChatBubble('user', clean);
  if (chatInput) chatInput.value = '';

  const waitBubble = addChatBubble('bot wait', 'Escribiendo…');
  window.setTimeout(() => {
    if (waitBubble?.parentNode) waitBubble.remove();
    addChatBubble('bot', findChatAnswer(clean));
  }, 420);
}

chatForm?.addEventListener('submit', (event) => {
  event.preventDefault();
  sendChatMessage(chatInput?.value ?? '');
});

chatQuickButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const question = button.dataset.q;
    if (!question) return;
    if (chatInput) chatInput.value = question;
    sendChatMessage(question);
  });
});

// 3) Panel de trazabilidad (IS · profesional): flujo con auto-progreso.
const panelCases = {
  corte: [
    'Entra el radicado de la solicitud de notas.',
    'Se valida semestre, asignatura y remitente.',
    'Se remite a Registro y Control Académico.',
    'Se verifica el consolidado y se redacta la respuesta.',
    'El estudiante consulta estado y respuesta con su folio.'
  ],
  virtualidad: [
    'La duda llega por el canal de soporte con fecha y folio.',
    'Se identifica si es tema de plataforma o de clase.',
    'Se remite a Soporte de Virtualidad.',
    'Se envía la guía de solución y queda constancia.',
    'Se confirma con el estudiante que quedó resuelta.'
  ],
  certificado: [
    'El estudiante solicita el certificado con folio automático.',
    'Se revisa el estado académico del solicitante.',
    'Se remite a Secretaría General.',
    'Se genera y firma el documento digital.',
    'Queda el folio habilitado para consulta y descarga.'
  ]
};

const panelButtons = [...document.querySelectorAll('.panel-btn')];
const panelSteps = [...document.querySelectorAll('#panel-steps li')];
const PANEL_STEP_DELAY = 850;
let panelTimers = [];

function runPanelFlow(caso) {
  panelTimers.forEach((timer) => window.clearTimeout(timer));
  panelTimers = [];

  const descriptions = panelCases[caso] ?? panelCases.corte;
  panelSteps.forEach((step, index) => {
    step.classList.remove('is-done');
    const note = step.querySelector('em');
    if (note && descriptions[index]) note.textContent = descriptions[index];
  });

  panelSteps.forEach((step, index) => {
    panelTimers.push(window.setTimeout(() => {
      step.classList.add('is-done');
      step.animate?.([{ opacity: 0.55 }, { opacity: 1 }], { duration: 260 });
    }, PANEL_STEP_DELAY * (index + 1)));
  });
}

panelButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const caso = button.dataset.caso ?? 'corte';
    panelButtons.forEach((item) => {
      const isActive = item === button;
      item.classList.toggle('is-active', isActive);
      item.setAttribute('aria-pressed', String(isActive));
    });
    runPanelFlow(caso);
  });
});

if (panelSteps.length && 'IntersectionObserver' in window) {
  const panelCard = document.querySelector('#interactivo-panel');
  if (panelCard) {
    const panelObserver = new IntersectionObserver((entries, observer) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        runPanelFlow(panelButtons[0]?.dataset.caso ?? 'corte');
        observer.disconnect();
      }
    }, { threshold: 0.45 });
    panelObserver.observe(panelCard);
  }
} else if (panelSteps.length) {
  runPanelFlow('corte');
}

// 4) Dashboard de KPIs simulado (MKT · tecnología): fórmulas visibles.
const kpiFormat = new Intl.NumberFormat('es-CO', { maximumFractionDigits: 1 });
const kpiMoney = new Intl.NumberFormat('es-CO', { maximumFractionDigits: 0 });
const kpiInputs = {
  impresiones: document.querySelector('#kpi-impresiones'),
  clics: document.querySelector('#kpi-clics'),
  conversiones: document.querySelector('#kpi-conversiones'),
  gasto: document.querySelector('#kpi-gasto'),
  valor: document.querySelector('#kpi-valor')
};
const kpiOutputs = {
  ctr: document.querySelector('#kpi-ctr'),
  cpc: document.querySelector('#kpi-cpc'),
  cpa: document.querySelector('#kpi-cpa'),
  roas: document.querySelector('#kpi-roas')
};

function clampKpiInput(input) {
  if (!input) return 0;
  const min = Number(input.min) || 0;
  const max = Number(input.max) || Number.MAX_SAFE_INTEGER;
  let value = Number(input.value);
  if (!Number.isFinite(value)) value = min;
  value = Math.min(Math.max(value, min), max);
  input.value = String(value);
  return value;
}

function updateKpis() {
  let impresiones = clampKpiInput(kpiInputs.impresiones);
  let clics = clampKpiInput(kpiInputs.clics);
  let conversiones = clampKpiInput(kpiInputs.conversiones);
  const gasto = clampKpiInput(kpiInputs.gasto);
  const valor = clampKpiInput(kpiInputs.valor);

  if (clics > impresiones) {
    clics = impresiones;
    if (kpiInputs.clics) kpiInputs.clics.value = String(impresiones);
  }
  if (conversiones > clics) {
    conversiones = clics;
    if (kpiInputs.conversiones) kpiInputs.conversiones.value = String(clics);
  }

  if (kpiOutputs.ctr) {
    kpiOutputs.ctr.textContent = impresiones > 0 ? `${kpiFormat.format((clics / impresiones) * 100)} %` : '—';
  }
  if (kpiOutputs.cpc) {
    kpiOutputs.cpc.textContent = clics > 0 ? `$${kpiMoney.format(gasto / clics)}` : '—';
  }
  if (kpiOutputs.cpa) {
    kpiOutputs.cpa.textContent = conversiones > 0 ? `$${kpiMoney.format(gasto / conversiones)}` : '—';
  }
  if (kpiOutputs.roas) {
    const ingreso = conversiones * valor;
    kpiOutputs.roas.textContent = gasto > 0 && conversiones > 0 ? `${kpiFormat.format(ingreso / gasto)} ×` : '—';
  }
}

Object.values(kpiInputs).forEach((input) => {
  input?.addEventListener('input', updateKpis);
});

if (Object.values(kpiInputs).some(Boolean)) updateKpis();

// 5) Explorador de macrotendencias (MKT · profesional): 2 toggles mínimo.
const planRecommendations = {
  ia: 'Ajuste sugerido: destinar una prueba controlada de gestión de pauta asistida por IA, documentando cada decisión y su resultado humano de revisión.',
  social: 'Ajuste sugerido: habilitar catálogo y pagos nativos del canal social y unificar el contenido del calendario con la vitrina digital.',
  personal: 'Ajuste sugerido: segmentar los mensajes según comportamiento del usuario y evaluar cada variante con pruebas A/B verificables.',
  first: 'Ajuste sugerido: fortalecer la base de datos propia (boletín, comunidad, atención directa) antes de escalar la pauta fría.'
};

const planPairNotes = {
  'ia|first': 'Escenario coherente: automatizar decisiones apoyadas en los datos propios antes que depender solo de la pauta externa.',
  'ia|social': 'Señal convergente: la automatización dentro del canal social exige medir cada resultado y mantener la revisión humana.',
  'personal|first': 'Escenario coherente: la personalización solo es honesta si se apoya en datos propios con consentimiento declarado.',
  'ia|personal': 'Escenario exploratorio: combinar automatización y personalización exige métricas claras y límites de uso declarados.',
  'social|personal': 'Escenario exploratorio: el comercio social gana cuando el mensaje se adapta al comportamiento real del canal.',
  'social|first': 'Escenario exploratorio: ventas en canal social sostenibles requieren alimentar la comunidad propia, no solo la pauta.'
};

const planButtons = [...document.querySelectorAll('.plan-btn')];
const planOut = document.querySelector('#plan-out');

function updatePlanExplorer() {
  if (!planOut) return;
  const active = planButtons.filter((button) => button.getAttribute('aria-pressed') === 'true');

  planOut.innerHTML = '';

  const heading = document.createElement('h4');
  const paragraphs = [];

  if (active.length < 2) {
    heading.textContent = 'Escenario actual';
    paragraphs.push(`Activa al menos dos tendencias para leer la recomendación del explorador (${active.length} activa${active.length === 1 ? '' : 's'}).`);
  } else {
    heading.textContent = `Escenario combinado · ${active.length} tendencias activas`;
    active.forEach((button) => {
      const text = planRecommendations[button.dataset.plan];
      if (text) paragraphs.push(text);
    });
    const key = active.map((button) => button.dataset.plan).sort().join('|');
    const pairNote = planPairNotes[key];
    if (pairNote) paragraphs.push(pairNote);
    if (!pairNote && active.length >= 3) {
      paragraphs.push('Escenario completo: prioriza los ajustes en orden —primero públicos y datos, después canales, por último presupuesto— y declara los supuestos de cada decisión.');
    }
  }

  planOut.appendChild(heading);
  paragraphs.forEach((text) => {
    const paragraph = document.createElement('p');
    paragraph.textContent = text;
    planOut.appendChild(paragraph);
  });
}

planButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const isActive = button.getAttribute('aria-pressed') === 'true';
    button.classList.toggle('is-active', !isActive);
    button.setAttribute('aria-pressed', String(!isActive));
    updatePlanExplorer();
  });
});

if (planOut) updatePlanExplorer();

// 6) Pitch deck "AURORA" (MKT · profesional): 6 láminas ficticias rotuladas.
const deckSlides = [
  {
    kicker: '01 / 06 · PROBLEMA',
    title: 'Las cafeterías de especialidad no llegan fuera de la ciudad.',
    body: 'Encuentro ficticio de partida para la narrativa demostrativa del deck.'
  },
  {
    kicker: '02 / 06 · SOLUCIÓN',
    title: 'Un club de suscripción de café de origen con asesoría de pauta local.',
    body: 'Marca ficticia AURORA: cajas mensuales de fincas aliadas y contenido que educa al suscriptor sobre el origen del grano.'
  },
  {
    kicker: '03 / 06 · MERCADO ILUSTRATIVO',
    title: 'Andrea, 26 años, descubre marcas por video corto y compra por suscripción.',
    body: 'Buyer persona ficticia: la ilustración del segmento no representa datos de mercado reales ni cifras de industria verificada.'
  },
  {
    kicker: '04 / 06 · MODELO',
    title: 'Suscripción mensual + venta directa en eventos de barrio.',
    body: 'Combinación ilustrativa de ingresos: este deck es un ejercicio académico del examen final, no la presentación de una empresa real.'
  },
  {
    kicker: '05 / 06 · EQUIPO (FICTICIO)',
    title: 'Tres roles inventados: marca, logística y contenido.',
    body: 'Nombres y perfiles son ficticios y van rotulados; ninguna persona real participa en este ejercicio de pitch.'
  },
  {
    kicker: '06 / 06 · HOJA DE RUTA',
    title: 'Piloto de barrio → plataforma propia → alianza con tostadores.',
    body: 'La ruta se propone con supuestos declarados; cada hito exige verificación previa, presupuesto propio y medición honesta.'
  }
];

const deckSlide = document.querySelector('#deck-slide');
const deckKicker = document.querySelector('#deck-kicker');
const deckTitle = document.querySelector('#deck-title');
const deckBody = document.querySelector('#deck-body');
const deckProgress = document.querySelector('#deck-progress');
const deckPrev = document.querySelector('#deck-prev');
const deckNext = document.querySelector('#deck-next');
let deckIndex = 0;

function renderDeckSlide() {
  const slide = deckSlides[deckIndex];
  if (!slide) return;
  if (deckKicker) deckKicker.textContent = slide.kicker;
  if (deckTitle) deckTitle.textContent = slide.title;
  if (deckBody) deckBody.textContent = slide.body;
  if (deckProgress) deckProgress.textContent = `Lámina ${deckIndex + 1} de ${deckSlides.length} · A→D para avanzar`;
  if (deckPrev) deckPrev.disabled = deckIndex === 0;
  if (deckNext) deckNext.disabled = deckIndex === deckSlides.length - 1;
  deckSlide?.animate?.([{ opacity: 0.25 }, { opacity: 1 }], { duration: 220 });
}

function goDeck(step) {
  const next = Math.min(Math.max(deckIndex + step, 0), deckSlides.length - 1);
  if (next === deckIndex) return;
  deckIndex = next;
  renderDeckSlide();
}

deckPrev?.addEventListener('click', () => goDeck(-1));
deckNext?.addEventListener('click', () => goDeck(1));

document.addEventListener('keydown', (event) => {
  const target = event.target;
  if (target instanceof HTMLElement && (target.matches('input, textarea, select') || target.isContentEditable)) return;
  if (event.key === 'ArrowLeft' || event.key === 'a' || event.key === 'A') goDeck(-1);
  if (event.key === 'ArrowRight' || event.key === 'd' || event.key === 'D') goDeck(1);
});

if (deckSlide) renderDeckSlide();

