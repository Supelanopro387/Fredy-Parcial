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
