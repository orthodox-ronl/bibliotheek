(function () {
  var bar = document.getElementById("score-audio-bar");
  var audio = document.getElementById("score-audio-bar-element");
  if (!bar || !audio) return;

  var titleEl = bar.querySelector(".score-audio-bar-title");
  var playBtn = bar.querySelector(".score-audio-bar-play");
  var seekEl = bar.querySelector(".score-audio-bar-seek");
  var elapsedEl = bar.querySelector(".score-audio-bar-elapsed");
  var durationEl = bar.querySelector(".score-audio-bar-duration");
  var rateSelect = bar.querySelector(".score-audio-bar-rate-select");
  var closeBtn = bar.querySelector(".score-audio-bar-close");
  var skipBtns = bar.querySelectorAll(".score-audio-bar-skip");

  var activeSrc = "";
  var seeking = false;

  function formatTime(seconds) {
    if (!isFinite(seconds) || seconds < 0) return "0:00";
    var total = Math.floor(seconds);
    var m = Math.floor(total / 60);
    var s = total % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  function setPlayingUi(playing) {
    bar.classList.toggle("score-audio-bar--paused", !playing);
    playBtn.setAttribute("aria-label", playing ? "Pauzeren" : "Afspelen");
    playBtn.setAttribute("aria-pressed", playing ? "true" : "false");
  }

  function showBar() {
    bar.hidden = false;
    document.body.classList.add("score-audio-bar-open");
  }

  function hideBar() {
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    activeSrc = "";
    bar.hidden = true;
    document.body.classList.remove("score-audio-bar-open");
    setPlayingUi(false);
    if ("mediaSession" in navigator) {
      navigator.mediaSession.metadata = null;
      navigator.mediaSession.playbackState = "none";
    }
  }

  function updateMediaSession(title) {
    if (!("mediaSession" in navigator)) return;
    navigator.mediaSession.metadata = new MediaMetadata({ title: title });
    navigator.mediaSession.setActionHandler("play", function () {
      audio.play();
    });
    navigator.mediaSession.setActionHandler("pause", function () {
      audio.pause();
    });
    navigator.mediaSession.setActionHandler("seekbackward", function () {
      audio.currentTime = Math.max(0, audio.currentTime - 10);
    });
    navigator.mediaSession.setActionHandler("seekforward", function () {
      audio.currentTime = Math.min(audio.duration || 0, audio.currentTime + 10);
    });
  }

  function readTitle(link) {
    var fromData = link.getAttribute("data-audio-title");
    if (fromData) return fromData;
    var detail = link.querySelector(".score-action-menu-detail");
    var label = link.querySelector(".score-action-menu-label");
    if (label && detail) return label.textContent.trim() + " — " + detail.textContent.trim();
    if (label) return label.textContent.trim();
    return link.textContent.trim() || "Beluisteren";
  }

  function syncSeekUi() {
    var dur = audio.duration;
    if (!isFinite(dur) || dur <= 0) {
      durationEl.textContent = "0:00";
      if (!seeking) seekEl.value = "0";
      return;
    }
    durationEl.textContent = formatTime(dur);
    if (!seeking) {
      seekEl.value = String(Math.round((audio.currentTime / dur) * 1000));
    }
    elapsedEl.textContent = formatTime(audio.currentTime);
  }

  function loadAndPlay(link) {
    var src = link.getAttribute("href");
    if (!src) return;
    var title = readTitle(link);
    var abs;
    try {
      abs = new URL(src, window.location.href).href;
    } catch (e) {
      return;
    }

    if (abs === activeSrc || audio.currentSrc === abs) {
      if (audio.paused) {
        audio.play().catch(function () {});
      } else {
        audio.pause();
      }
      return;
    }

    activeSrc = abs;
    audio.src = src;
    audio.playbackRate = parseFloat(rateSelect.value, 10) || 1;
    titleEl.textContent = title;
    showBar();
    updateMediaSession(title);
    audio.play().catch(function () {
      hideBar();
    });
  }

  playBtn.addEventListener("click", function () {
    if (!audio.src) return;
    if (audio.paused) {
      audio.play().catch(function () {});
    } else {
      audio.pause();
    }
  });

  closeBtn.addEventListener("click", hideBar);

  skipBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var delta = parseFloat(btn.getAttribute("data-skip"), 10);
      if (!isFinite(delta) || !audio.src) return;
      var dur = audio.duration;
      var next = audio.currentTime + delta;
      if (isFinite(dur)) next = Math.min(dur, Math.max(0, next));
      else next = Math.max(0, next);
      audio.currentTime = next;
    });
  });

  rateSelect.addEventListener("change", function () {
    audio.playbackRate = parseFloat(rateSelect.value, 10) || 1;
  });

  seekEl.addEventListener("input", function () {
    seeking = true;
    var dur = audio.duration;
    if (!isFinite(dur) || dur <= 0) return;
    var t = (parseInt(seekEl.value, 10) / 1000) * dur;
    elapsedEl.textContent = formatTime(t);
  });

  seekEl.addEventListener("change", function () {
    var dur = audio.duration;
    if (isFinite(dur) && dur > 0) {
      audio.currentTime = (parseInt(seekEl.value, 10) / 1000) * dur;
    }
    seeking = false;
  });

  audio.addEventListener("timeupdate", syncSeekUi);
  audio.addEventListener("loadedmetadata", syncSeekUi);
  audio.addEventListener("durationchange", syncSeekUi);
  audio.addEventListener("play", function () {
    setPlayingUi(true);
    if ("mediaSession" in navigator) navigator.mediaSession.playbackState = "playing";
  });
  audio.addEventListener("pause", function () {
    setPlayingUi(false);
    if ("mediaSession" in navigator) navigator.mediaSession.playbackState = "paused";
  });
  audio.addEventListener("ended", function () {
    setPlayingUi(false);
    syncSeekUi();
  });

  window.addEventListener("pagehide", function () {
    if (!audio.paused) audio.pause();
  });

  document.addEventListener("click", function (event) {
    var audioLink = event.target.closest("a.score-audio-play");
    if (audioLink) {
      event.preventDefault();
      loadAndPlay(audioLink);
      return;
    }

    // Andere score-acties (Oefenen, Downloaden, Printen, Bronnen): stop Beluisteren.
    // Beluisteren-menu zelf (trigger of keuzes) blijft open/speelbaar.
    if (bar.hidden) return;
    var inActions = event.target.closest(".score-actions");
    if (!inActions) return;
    var beluisterMenu = event.target.closest(".score-action-menu");
    if (beluisterMenu && beluisterMenu.querySelector("a.score-audio-play")) return;
    if (!event.target.closest("a, button")) return;
    hideBar();
  });
})();
