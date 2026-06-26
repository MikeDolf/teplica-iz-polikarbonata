(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    // ── FAQ: переключение иконки +/− ────────────────────────────────
    document.querySelectorAll('.faq-section details').forEach(function (detail) {
      detail.addEventListener('toggle', function () {
        var icon = detail.querySelector('.faq-icon use');
        if (!icon) return;
        icon.setAttribute('href', detail.open ? '#icon-minus' : '#icon-plus');
      });
    });

    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ── Полоса прогресса чтения ─────────────────────────────────────
    var bar = document.createElement('div');
    bar.className = 'read-progress';
    document.body.appendChild(bar);

    // ── Кнопка «наверх» ─────────────────────────────────────────────
    var toTop = document.createElement('button');
    toTop.className = 'to-top';
    toTop.type = 'button';
    toTop.setAttribute('aria-label', 'Наверх');
    toTop.innerHTML = '↑';
    document.body.appendChild(toTop);
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
    });

    // Обновление прогресса и видимости кнопки (через rAF, без нагрузки)
    var ticking = false;
    function update() {
      var el = document.documentElement;
      var max = el.scrollHeight - el.clientHeight;
      bar.style.width = (max > 0 ? (el.scrollTop / max) * 100 : 0) + '%';
      toTop.classList.toggle('show', el.scrollTop > 350);
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();

    // ── Появление блоков при скролле ────────────────────────────────
    if (reduced || !('IntersectionObserver' in window)) return;

    var selector = '.tldr,.svg-figure,.table-wrap,.step-card,.cta-block,' +
                   '.faq-section,.note-box,.warn-box,.related-links,' +
                   '.hub-card,.catalog-cat,.sidebar-block';

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll(selector).forEach(function (el) {
      io.observe(el);
    });
  });
}());
