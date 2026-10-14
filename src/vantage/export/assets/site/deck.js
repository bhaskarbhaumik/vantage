/* Vantage deck runtime: scale the fixed 1920x1080 stage to the viewport, and navigate.
 *
 * Zero dependencies. Authoring at a fixed stage size and scaling the whole
 * thing means a slide is pixel-identical on a laptop, a projector and in a
 * screenshot — no reflow surprises mid-presentation.
 */
(function () {
  "use strict";

  var stage = document.querySelector(".stage");
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var progress = document.querySelector(".deck__progress");
  var counter = document.querySelector("[data-counter]");
  if (!stage || !slides.length) return;

  var STAGE_W = 1920;
  var STAGE_H = 1080;
  var index = 0;

  function fit() {
    var pad = 0.965;
    var scale = Math.min(window.innerWidth / STAGE_W, window.innerHeight / STAGE_H) * pad;
    stage.style.transform = "scale(" + scale + ")";
  }

  function show(next, viaHash) {
    index = Math.max(0, Math.min(slides.length - 1, next));
    slides.forEach(function (slide, i) {
      slide.classList.toggle("is-active", i === index);
    });
    if (progress) progress.style.width = ((index + 1) / slides.length) * 100 + "%";
    if (counter) counter.textContent = index + 1 + " / " + slides.length;
    if (!viaHash) {
      // replaceState, not a hash assignment: deep links survive without
      // filling the back button with every slide the presenter stepped past.
      history.replaceState(null, "", "#" + (index + 1));
    }
  }

  function fromHash() {
    var n = parseInt((location.hash || "").replace("#", ""), 10);
    return isNaN(n) ? 0 : n - 1;
  }

  document.addEventListener("keydown", function (event) {
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    switch (event.key) {
      case "ArrowRight": case "ArrowDown": case " ": case "PageDown": case "n": case "j":
        event.preventDefault(); show(index + 1); break;
      case "ArrowLeft": case "ArrowUp": case "PageUp": case "p": case "k":
        event.preventDefault(); show(index - 1); break;
      case "Home": event.preventDefault(); show(0); break;
      case "End": event.preventDefault(); show(slides.length - 1); break;
      case "f": if (document.fullscreenElement) document.exitFullscreen();
                else document.documentElement.requestFullscreen(); break;
    }
  });

  // Click to advance, but never steal a click meant for a link or a control.
  document.addEventListener("click", function (event) {
    if (event.target.closest("a, button, .deck__hud, table")) return;
    show(index + 1);
  });

  var touchX = null;
  document.addEventListener("touchstart", function (e) { touchX = e.changedTouches[0].clientX; }, { passive: true });
  document.addEventListener("touchend", function (e) {
    if (touchX === null) return;
    var dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 55) show(index + (dx < 0 ? 1 : -1));
    touchX = null;
  }, { passive: true });

  var prev = document.querySelector("[data-prev]");
  var next = document.querySelector("[data-next]");
  if (prev) prev.addEventListener("click", function () { show(index - 1); });
  if (next) next.addEventListener("click", function () { show(index + 1); });

  window.addEventListener("resize", fit);
  window.addEventListener("hashchange", function () { show(fromHash(), true); });

  fit();
  show(fromHash(), true);
})();
