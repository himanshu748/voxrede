// Progressive enhancement: every recording and source link remains readable without JS.
(() => {
  const root = document.querySelector('.walkthrough');
  if (!root) return;
  const controls = root.querySelector('.walk-controls');
  const buttons = [...controls.querySelectorAll('button')];
  const panels = [...root.querySelectorAll('.walk-panel')];
  function select(id) {
    if (!panels.some(panel => panel.id === id)) return;
    root.querySelectorAll('audio').forEach(audio => audio.pause());
    panels.forEach(panel => { panel.hidden = panel.id !== id; });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.walk === id)));
  }
  controls.hidden = false;
  select(panels.some(panel => '#' + panel.id === location.hash) ? location.hash.slice(1) : panels[0].id);
  buttons.forEach(button => button.addEventListener('click', () => {
    select(button.dataset.walk);
    history.replaceState(null, '', '#' + button.dataset.walk);
  }));
  addEventListener('hashchange', () => select(location.hash.slice(1)));
  root.querySelectorAll('audio').forEach(audio => {
    audio.addEventListener('play', () => document.querySelectorAll('audio').forEach(other => { if (other !== audio) other.pause(); }));
    audio.addEventListener('error', () => {
      audio.parentElement.querySelector('.audio-help').textContent = 'This browser could not play the excerpt. Download the WAV below or open the page in Safari. The source transcript remains available.';
    });
  });
})();
