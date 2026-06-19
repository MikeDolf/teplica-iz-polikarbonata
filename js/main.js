(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var faqDetails = document.querySelectorAll('.faq-section details');
    faqDetails.forEach(function (detail) {
      detail.addEventListener('toggle', function () {
        var icon = detail.querySelector('.faq-summary-icon use');
        if (!icon) return;
        if (detail.open) {
          icon.setAttribute('href', '#icon-minus');
        } else {
          icon.setAttribute('href', '#icon-plus');
        }
      });
    });
  });
}());
