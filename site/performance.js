(() => {
  'use strict';

  const API_BASE = 'https://golscope-api-production.up.railway.app';
  const POLL_ACTIVE_MS = 12000;
  const POLL_BACKGROUND_MS = 45000;
  const HISTORY_DAYS = 30;

  const els = {
    date: document.querySelector('#perfDate'),
    today: document.querySelector('#perfToday'),
    yesterday: document.querySelector('#perfYesterday'),
    dateLabel: document.querySelector('#performanceDateLabel'),
    hits: document.querySelector('#perfHits'),
    misses: document.querySelector('#perfMisses'),
    pending: document.querySelector('#perfPending'),
    resolved: document.querySelector('#perfResolved'),
    hitRate: document.querySelector('#perfHitRate'),
    hitRateSmall: document.querySelector('#perfHitRateSmall'),
    missRateSmall: document.querySelector('#perfMissRateSmall'),
    donut: document.querySelector('#perfDonut'),
    donutRate: document.querySelector('#perfDonutRate'),
    ratioHit: document.querySelector('#perfRatioHit'),
    headline: document.querySelector('#perfHeadline'),
    evolution: document.querySelector('#perfEvolution'),
    updated: document.querySelector('#perfUpdated'),
    status: document.querySelector('#perfStatus')
  };

  if (!els.date || !els.hits) return;

  let selectedDate = '';
  let cursor = 0;
  let timer = null;
  let followingToday = true;
  let inflight = false;

  function brtDate() {
    const parts = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'America/Sao_Paulo', year: 'numeric', month: '2-digit', day: '2-digit'
    }).formatToParts(new Date());
    const map = Object.fromEntries(parts.map((part) => [part.type, part.value]));
    return `${map.year}-${map.month}-${map.day}`;
  }

  function shiftDate(isoDate, days) {
    const date = new Date(`${isoDate}T12:00:00Z`);
    date.setUTCDate(date.getUTCDate() + days);
    return date.toISOString().slice(0, 10);
  }

  function pct(value) {
    const n = Number(value || 0);
    return `${new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 }).format(n)}%`;
  }

  function dateText(isoDate) {
    const today = brtDate();
    if (isoDate === today) return 'Hoje';
    if (isoDate === shiftDate(today, -1)) return 'Ontem';
    const [year, month, day] = isoDate.split('-');
    return `${day}/${month}/${year}`;
  }

  async function api(path) {
    const response = await fetch(`${API_BASE}${path}`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      cache: 'no-store'
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || 'Dados públicos temporariamente indisponíveis.');
    return data;
  }

  function setActiveDateButtons() {
    const today = brtDate();
    els.today.classList.toggle('active', selectedDate === today);
    els.yesterday.classList.toggle('active', selectedDate === shiftDate(today, -1));
  }

  function renderPerformance(data) {
    const hits = Number(data.hits || 0);
    const misses = Number(data.misses || 0);
    const pending = Number(data.pending || 0);
    const resolved = Number(data.resolved || 0);
    const hitRate = Number(data.hit_rate || 0);
    const missRate = Number(data.miss_rate || 0);

    selectedDate = data.date || selectedDate || brtDate();
    cursor = Math.max(cursor, Number(data.cursor || 0));
    els.date.value = selectedDate;
    els.dateLabel.textContent = dateText(selectedDate);
    els.hits.textContent = hits;
    els.misses.textContent = misses;
    els.pending.textContent = pending;
    els.resolved.textContent = resolved;
    els.hitRate.textContent = pct(hitRate);
    els.hitRateSmall.textContent = pct(hitRate);
    els.missRateSmall.textContent = pct(missRate);
    els.donutRate.textContent = pct(hitRate);
    els.donut.style.setProperty('--hit-rate', String(Math.max(0, Math.min(100, hitRate))));
    els.ratioHit.style.width = `${Math.max(0, Math.min(100, hitRate))}%`;
    els.headline.textContent = `${hits} acertos / ${misses} erros — ${pct(hitRate)}`;
    els.updated.textContent = 'Atualizado automaticamente';
    els.status.textContent = pending > 0
      ? `${pending} pendente${pending === 1 ? '' : 's'} acompanhando o estado canônico.`
      : 'Todos os alertas publicados deste dia estão resolvidos.';
    els.status.classList.remove('performance-error');
    setActiveDateButtons();
  }

  function renderHistory(payload) {
    const days = Array.isArray(payload.days) ? payload.days.slice(-7) : [];
    els.evolution.replaceChildren();
    if (!days.length) {
      const empty = document.createElement('p');
      empty.className = 'panel-copy';
      empty.textContent = 'O histórico agregado aparecerá aqui conforme houver resultados publicados.';
      els.evolution.appendChild(empty);
      return;
    }

    days.forEach((day) => {
      const item = document.createElement('div');
      item.className = 'evolution-day';

      const rate = document.createElement('span');
      rate.className = 'evolution-rate';
      rate.textContent = pct(day.hit_rate);

      const wrap = document.createElement('div');
      wrap.className = 'evolution-bar-wrap';
      const bar = document.createElement('div');
      bar.className = 'evolution-bar';
      bar.style.height = `${Math.max(3, Math.min(100, Number(day.hit_rate || 0)))}%`;
      wrap.appendChild(bar);

      const date = document.createElement('span');
      date.className = 'evolution-date';
      const parts = String(day.date || '').split('-');
      date.textContent = parts.length === 3 ? `${parts[2]}/${parts[1]}` : day.date;

      const n = document.createElement('span');
      n.className = 'evolution-n';
      n.textContent = `N=${Number(day.resolved || 0)}`;

      item.append(rate, wrap, date, n);
      els.evolution.appendChild(item);
    });
  }

  async function loadDate(date) {
    selectedDate = date;
    const data = await api(`/public/performance?date=${encodeURIComponent(date)}`);
    renderPerformance(data);
  }

  async function loadHistory() {
    const data = await api(`/public/performance/history?days=${HISTORY_DAYS}`);
    cursor = Math.max(cursor, Number(data.cursor || 0));
    renderHistory(data);
  }

  async function refreshChanges() {
    if (inflight) return;
    inflight = true;
    try {
      const currentToday = brtDate();
      if (followingToday && selectedDate && selectedDate !== currentToday) {
        selectedDate = currentToday;
        await loadDate(selectedDate);
        await loadHistory();
        return;
      }
      const data = await api(`/public/performance/changes?since=${encodeURIComponent(cursor)}&date=${encodeURIComponent(selectedDate)}`);
      cursor = Math.max(cursor, Number(data.cursor || 0));
      if (data.changed && data.performance) {
        renderPerformance(data.performance);
        await loadHistory();
      }
    } catch (error) {
      els.status.textContent = error.message || 'Falha temporária de atualização.';
      els.status.classList.add('performance-error');
    } finally {
      inflight = false;
      schedulePoll();
    }
  }

  function schedulePoll() {
    if (timer) clearTimeout(timer);
    timer = setTimeout(refreshChanges, document.hidden ? POLL_BACKGROUND_MS : POLL_ACTIVE_MS);
  }

  els.today.addEventListener('click', async () => {
    followingToday = true;
    try {
      await loadDate(brtDate());
    } catch (error) {
      els.status.textContent = error.message;
      els.status.classList.add('performance-error');
    }
  });

  els.yesterday.addEventListener('click', async () => {
    followingToday = false;
    try {
      await loadDate(shiftDate(brtDate(), -1));
    } catch (error) {
      els.status.textContent = error.message;
      els.status.classList.add('performance-error');
    }
  });

  els.date.addEventListener('change', async () => {
    if (!els.date.value) return;
    followingToday = els.date.value === brtDate();
    try {
      await loadDate(els.date.value);
    } catch (error) {
      els.status.textContent = error.message;
      els.status.classList.add('performance-error');
    }
  });

  document.addEventListener('visibilitychange', schedulePoll);

  (async () => {
    try {
      selectedDate = brtDate();
      els.date.max = selectedDate;
      await Promise.all([loadDate(selectedDate), loadHistory()]);
    } catch (error) {
      els.status.textContent = error.message || 'Dados públicos temporariamente indisponíveis.';
      els.status.classList.add('performance-error');
      els.updated.textContent = 'Falha de sincronização';
    } finally {
      schedulePoll();
    }
  })();
})();
