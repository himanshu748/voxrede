/* Progressive enhancement for already-rendered, local archived evidence. */
(() => {
  'use strict';
  const dataNode = document.getElementById('archive-data');
  if (!dataNode) return;
  let archive;
  try { archive = JSON.parse(dataNode.textContent); } catch { return; }
  if (!archive.cases.length) return;
  const search = document.getElementById('case-search');
  const suite = document.getElementById('suite-filter');
  const outcome = document.getElementById('outcome-filter');
  const count = document.getElementById('result-count');
  const empty = document.getElementById('search-empty');
  const docs = [...document.querySelectorAll('[data-case]')];
  const links = [...document.querySelectorAll('[data-open]')];
  const rows = [...document.querySelectorAll('[data-index-case]')];
  const byKey = new Map(archive.cases.map(c => [c.key, c]));
  const searchable = new Map(archive.cases.map(c => [c.key,
    [c.suite_label, c.target, c.result.name, c.result.attack, c.result.class,
      ...c.result.timeline.map(t => t.text), ...c.result.findings.map(f => f.label || f.tool)].join(' ').toLowerCase()]));
  let current = archive.cases[0].key;
  let noticeTimer;
  function announce(text) {
    const box = document.getElementById('action-status');
    box.textContent = text; box.hidden = false;
    clearTimeout(noticeTimer); noticeTimer = setTimeout(() => { box.hidden = true; }, 3500);
  }
  function matches(c) {
    const r = c.result;
    return (suite.value === 'all' || suite.value === c.suite) &&
      (outcome.value === 'all' || (outcome.value === 'findings' && r.findings.length > 0) ||
       (outcome.value === 'clear' && r.verdict === 'PASS') ||
       (outcome.value === 'incomplete' && (r.verdict === 'INCONCLUSIVE' || (r.quality_issues || []).length > 0))) &&
      searchable.get(c.key).includes(search.value.trim().toLowerCase());
  }
  function filters() {
    const visible = archive.cases.filter(matches);
    const keys = new Set(visible.map(c => c.key));
    rows.forEach(r => { r.hidden = !keys.has(r.dataset.indexCase); });
    count.textContent = `${visible.length} of ${archive.cases.length} samples`;
    empty.hidden = visible.length > 0;
    if (!keys.has(current)) current = visible[0]?.key || null;
    docs.forEach(d => { d.hidden = d.dataset.case !== current; });
    links.forEach(l => { if (l.dataset.open === current) l.setAttribute('aria-current', 'true'); else l.removeAttribute('aria-current'); });
    return visible;
  }
  function show(key, event, focus = false) {
    if (!byKey.has(key)) return;
    current = key;
    if (!matches(byKey.get(key))) { search.value = ''; suite.value = 'all'; outcome.value = 'all'; }
    filters();
    document.querySelectorAll('.spotlight').forEach(e => e.classList.remove('spotlight'));
    const doc = document.getElementById(byKey.get(key).dom_id);
    if (event !== undefined) {
      const node = document.getElementById(`${byKey.get(key).dom_id}/event-${event}`);
      if (node) {
        const select = doc.querySelector('[data-speakers]');
        select.value = 'all'; applySpeakers(doc, 'all');
        node.classList.add('spotlight'); node.scrollIntoView({block:'center'}); node.focus({preventScroll:true});
      } else announce('That event is not in this recording. Showing the case.');
    } else if (focus) { doc.focus({preventScroll:true}); doc.scrollIntoView({block:'start'}); }
  }
  function fromHash(focus = false) {
    const hash = location.hash.slice(1);
    if (!hash) { show(archive.cases[0].key, undefined, focus); return; }
    const parts = hash.split('/');
    if (parts.length === 1 && archive.suites.some(s => s.tag === parts[0])) {
      suite.value = parts[0]; search.value = ''; outcome.value = 'all';
      show(archive.cases.find(c => c.suite === parts[0]).key, undefined, focus); return;
    }
    const key = parts.slice(0,2).join('/');
    if (parts.length >= 2 && byKey.has(key) && parts.length <= 3) {
      if (parts[2] && !/^event-\d+$/.test(parts[2])) { announce('The event link is invalid. Showing the case.'); show(key, undefined, focus); return; }
      show(key, parts[2] ? Number(parts[2].slice(6)) : undefined, focus);
    } else { show(archive.cases[0].key, undefined, focus); announce('Recording link not found. Showing the first archived case.'); }
  }
  function applySpeakers(doc, speaker) {
    const events = [...doc.querySelectorAll('[data-speaker]')];
    events.forEach(e => { e.hidden = speaker !== 'all' && e.dataset.speaker !== speaker; });
    doc.querySelector('.transcript-empty').hidden = events.some(e => !e.hidden);
  }
  function applyFilters() { filters(); if (current) history.replaceState(null, '', `#${current}`); }
  function reset() { search.value = ''; suite.value = 'all'; outcome.value = 'all'; applyFilters(); }
  search.addEventListener('input', applyFilters);
  suite.addEventListener('change', applyFilters);
  outcome.addEventListener('change', applyFilters);
  document.getElementById('clear-filters').addEventListener('click', reset);
  document.getElementById('empty-reset').addEventListener('click', () => { reset(); search.focus(); });
  document.querySelectorAll('[data-speakers]').forEach(s => s.addEventListener('change', () => applySpeakers(s.closest('[data-case]'), s.value)));
  document.querySelectorAll('[data-copy]').forEach(b => b.addEventListener('click', async () => {
    const url = new URL(location.href); url.hash = b.dataset.copy;
    try { await navigator.clipboard.writeText(url.href); announce('Case link copied.'); }
    catch { const fallback = document.getElementById('copy-fallback'); fallback.hidden = false;
      const input = document.getElementById('copy-url'); input.value = url.href; input.focus(); input.select(); }
  }));
  document.getElementById('close-copy').addEventListener('click', () => { document.getElementById('copy-fallback').hidden = true; });
  document.querySelectorAll('[data-export]').forEach(b => b.addEventListener('click', () => {
    const c = byKey.get(b.dataset.export);
    const bundle = {format:'voxrede-evidence-v1', scope:'Archived project-owned fixture. Mocked business tools. No safety certification.',
      source:{file:c.filename,sha256:c.sha256,suite:c.suite,target:c.target,hardened:c.hardened}, result:c.result};
    const url = URL.createObjectURL(new Blob([JSON.stringify(bundle,null,2)], {type:'application/json'}));
    const a = document.createElement('a'); a.href = url; a.download = `voxrede-${c.suite}-${c.result.attack.replace(/[^a-zA-Z0-9_-]/g,'_')}.json`;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    announce('Evidence JSON prepared for download.');
  }));
  document.addEventListener('click', e => {
    const link = e.target.closest('a[href^="#"]');
    if (link && link.hash === location.hash && link.hash !== '#workspace') { e.preventDefault(); fromHash(true); }
  });
  window.addEventListener('hashchange', () => fromHash(true));
  document.querySelectorAll('.index-controls,.case-actions,.speaker-filter').forEach(e => { e.hidden = false; });
  document.body.classList.add('enhanced');
  const compact = matchMedia('(max-width:700px)');
  const browser = document.querySelector('.recording-browser');
  browser.open = !compact.matches;
  compact.addEventListener('change', () => { browser.open = !compact.matches; });
  fromHash();
})();
