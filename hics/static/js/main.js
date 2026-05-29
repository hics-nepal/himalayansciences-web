/* ── HICS main.js ───────────────────────────────────────── */

/**
 * Poll the live-data API and update the header station readout.
 * Runs once on page load; the home page has its own inline widget updater.
 */
(function () {
  'use strict';

  const STATION = 'KTM-001';
  const API_URL = '/api/data/latest/?station=' + STATION;

  const dot = document.getElementById('station-dot');
  const reading = document.getElementById('station-reading');

  if (!dot || !reading) return;

  fetch(API_URL)
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (d.error) return;

      dot.classList.remove('offline');

      var parts = [];
      if (d.temperature_c !== null) parts.push(d.temperature_c.toFixed(1) + '\u00b0C');
      if (d.humidity_rh !== null)   parts.push(d.humidity_rh.toFixed(0) + '% RH');
      if (d.pressure_hpa !== null)  parts.push(d.pressure_hpa.toFixed(0) + ' hPa');

      reading.textContent = parts.join(' · ');
    })
    .catch(function () {
      // Silently fail — station might be offline.
    });
})();
