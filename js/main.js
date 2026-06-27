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

    // ── Увеличение схем по тапу ─────────────────────────────────────
    (function () {
      var overlay = null;
      function close() {
        if (!overlay) return;
        overlay.classList.remove('open');
        document.body.style.overflow = '';
        setTimeout(function () { overlay.style.display = 'none'; }, 200);
      }
      function build() {
        overlay = document.createElement('div');
        overlay.className = 'svg-zoom-overlay';
        overlay.innerHTML =
          '<button class="svg-zoom-close" type="button" aria-label="Закрыть">×</button>' +
          '<div class="svg-zoom-scroll"><div class="svg-zoom-inner"></div></div>';
        document.body.appendChild(overlay);
        overlay.addEventListener('click', function (e) {
          if (e.target === overlay ||
              e.target.classList.contains('svg-zoom-scroll') ||
              e.target.closest('.svg-zoom-close')) close();
        });
        document.addEventListener('keydown', function (e) {
          if (e.key === 'Escape') close();
        });
        return overlay;
      }
      document.querySelectorAll('.svg-figure').forEach(function (fig) {
        var svg = fig.querySelector('svg');
        if (!svg) return;
        fig.addEventListener('click', function () {
          if (!overlay) build();
          var inner = overlay.querySelector('.svg-zoom-inner');
          inner.innerHTML = '';
          inner.appendChild(svg.cloneNode(true));
          var cap = fig.querySelector('figcaption');
          if (cap) inner.appendChild(cap.cloneNode(true));
          overlay.style.display = 'block';
          document.body.style.overflow = 'hidden';
          requestAnimationFrame(function () {
            overlay.classList.add('open');
            var sc = overlay.querySelector('.svg-zoom-scroll');
            sc.scrollLeft = (inner.offsetWidth - sc.clientWidth) / 2;
          });
        });
      });
    }());

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
