/* Vantage microsite runtime: highlight the nav entry for the section on screen, and filter the
 * nav by a search term. Zero dependencies; degrades to a plain scrolling document without it.
 */
(function () {
  "use strict";

  var links = Array.prototype.slice.call(document.querySelectorAll(".site__nav a[href^='#']"));
  var search = document.querySelector(".site__nav input[type='search']");
  if (search) {
    search.addEventListener("input", function () {
      var term = search.value.trim().toLowerCase();
      links.forEach(function (link) {
        var hit = !term || link.textContent.toLowerCase().indexOf(term) !== -1 ||
          (link.getAttribute("data-text") || "").indexOf(term) !== -1;
        link.classList.toggle("is-hidden", !hit);
      });
    });
  }

  if (!links.length || !("IntersectionObserver" in window)) return;

  var byId = {};
  links.forEach(function (link) { byId[link.getAttribute("href").slice(1)] = link; });
  var targets = Object.keys(byId)
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean);
  var visible = new Set();

  function paint() {
    links.forEach(function (link) { link.classList.remove("is-current"); });
    // The topmost visible section wins, so scrolling never leaves two lit.
    var best = targets.filter(function (t) { return visible.has(t.id); })[0];
    if (best && byId[best.id]) byId[best.id].classList.add("is-current");
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) visible.add(entry.target.id);
      else visible.delete(entry.target.id);
    });
    paint();
  }, { rootMargin: "-8% 0px -70% 0px", threshold: 0 });

  targets.forEach(function (target) { observer.observe(target); });
})();
