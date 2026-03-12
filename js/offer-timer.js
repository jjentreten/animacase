/**
 * Cronômetro de oferta global – Animacase
 * 15 minutos, persistente em localStorage, sincronizado em todo o site.
 * Inicia na primeira visita; continua ao trocar de página ou recarregar.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'animacase_offer_timer_end';
  var DURATION_MS = 15 * 60 * 1000; // 15 minutos

  function getEndTime() {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      var end = parseInt(stored, 10);
      if (end > Date.now()) return end;
    }
    var endTime = Date.now() + DURATION_MS;
    localStorage.setItem(STORAGE_KEY, String(endTime));
    return endTime;
  }

  function formatRemaining(ms) {
    if (ms <= 0) return '00:00';
    var totalSeconds = Math.floor(ms / 1000);
    var minutes = Math.floor(totalSeconds / 60);
    var seconds = totalSeconds % 60;
    return (
      String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0')
    );
  }

  function updateDisplays(text) {
    var nodes = document.querySelectorAll('.js-offer-timer');
    for (var i = 0; i < nodes.length; i++) {
      nodes[i].textContent = text;
    }
  }

  function tick() {
    var endTime = getEndTime();
    var remaining = endTime - Date.now();

    if (remaining <= 0) {
      updateDisplays('00:00');
      if (window.animacaseOfferTimerId) {
        clearInterval(window.animacaseOfferTimerId);
        window.animacaseOfferTimerId = null;
      }
      return;
    }

    updateDisplays(formatRemaining(remaining));
  }

  function start() {
    tick();
    if (window.animacaseOfferTimerId) clearInterval(window.animacaseOfferTimerId);
    window.animacaseOfferTimerId = setInterval(tick, 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
