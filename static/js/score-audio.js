(function () {
  var current = null;

  function stopCurrent() {
    if (!current) return;
    current.pause();
    current = null;
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest("a.score-audio-play");
    if (!link) return;
    var src = link.getAttribute("href");
    if (!src) return;
    event.preventDefault();
    if (current && current.src && current.src.indexOf(src) !== -1 && !current.paused) {
      stopCurrent();
      return;
    }
    stopCurrent();
    current = new Audio(src);
    current.play().catch(function () {
      stopCurrent();
    });
  });
})();
