/* ── HICS main.js ───────────────────────────────────────── */

/**
 * Poll the live-data API and update the header station readout.
 * Runs once on page load; the home page has its own inline widget updater.
 */
(function () {
  'use strict';

  // ── Mobile menu toggle ──────────────────────────────────
  var toggle = document.getElementById('mobile-menu-toggle');
  var mobileNav = document.getElementById('mobile-nav');

  if (toggle && mobileNav) {
    toggle.addEventListener('click', function () {
      var isOpen = mobileNav.classList.toggle('open');
      toggle.classList.toggle('active');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      mobileNav.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
      // Prevent body scroll when menu is open
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });
  }

  // ── Live station data ───────────────────────────────────
  var STATION = 'KTM-001';
  var API_URL = '/api/data/latest/?station=' + STATION;

  var dot = document.getElementById('station-dot');
  var reading = document.getElementById('station-reading');

  if (!dot || !reading) return;

  function updateStation(d) {
    if (d.error) return;

    dot.classList.remove('offline');

    var parts = [];
    if (d.temperature_c !== null) parts.push(d.temperature_c.toFixed(1) + '\u00b0C');
    if (d.humidity_rh !== null)   parts.push(d.humidity_rh.toFixed(0) + '% RH');
    if (d.pressure_hpa !== null)  parts.push(d.pressure_hpa.toFixed(0) + ' hPa');

    reading.textContent = parts.join(' \u00b7 ');

    // Also update mobile nav station if present
    var mobileDot = document.getElementById('mobile-station-dot');
    var mobileReading = document.getElementById('mobile-station-reading');
    if (mobileDot) mobileDot.classList.remove('offline');
    if (mobileReading) mobileReading.textContent = 'KTM-001 \u00b7 ' + parts.join(' \u00b7 ');
  }

  fetch(API_URL)
    .then(function (r) { return r.json(); })
    .then(updateStation)
    .catch(function () {
      reading.textContent = 'KTM-001 \u00b7 offline';
    });

  // Auto-refresh every 60 seconds
  setInterval(function () {
    fetch(API_URL)
      .then(function (r) { return r.json(); })
      .then(updateStation)
      .catch(function () {});
  }, 60000);
})();
