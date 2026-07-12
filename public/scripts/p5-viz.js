/* p5.js visualization runtime for Python Central Hub.
   Finds every .pch-p5 panel emitted by the remark plugin (lib/p5/remake.ts),
   lazy-loads p5 from a CDN once, and runs each sketch in INSTANCE mode so
   multiple sketches can coexist on a page.

   Sketches are authored in ordinary global style (bare `createCanvas`,
   `setup`, `draw`, …). The wrapper below evaluates that source inside a
   `with (p)` block so those bare calls resolve to the p5 instance, then
   re-binds the declared lifecycle hooks onto the instance.

   Behaviour:
   - Lazy: a sketch is only built when it first scrolls into view.
   - Frugal: paused (noLoop) when scrolled out of view, resumed when back —
     unless the reader paused it manually.
   - Accessible: under prefers-reduced-motion the sketch builds one frame then
     stops; the reader can press Play.
   No-ops on any page with no .pch-p5 panels. */
(function () {
  "use strict";

  var P5_SRC = "https://cdn.jsdelivr.net/npm/p5@1.9.4/lib/p5.min.js";
  var HOOKS = [
    "preload", "setup", "draw",
    "mousePressed", "mouseReleased", "mouseClicked", "mouseMoved",
    "mouseDragged", "doubleClicked", "mouseWheel",
    "keyPressed", "keyReleased", "keyTyped",
    "touchStarted", "touchMoved", "touchEnded",
    "windowResized",
  ];

  var reduce =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var p5Promise = null;
  function loadP5() {
    if (window.p5) return Promise.resolve();
    if (p5Promise) return p5Promise;
    p5Promise = new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = P5_SRC;
      s.crossOrigin = "anonymous";
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
    return p5Promise;
  }

  // Base64 → UTF-8 string (matches Buffer.from(code).toString('base64')).
  function decode(b64) {
    try {
      return decodeURIComponent(
        Array.prototype.map
          .call(atob(b64), function (c) {
            return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
          })
          .join("")
      );
    } catch (e) {
      try { return atob(b64); } catch (e2) { return ""; }
    }
  }

  function makeFactory(code) {
    var rebind = "";
    for (var i = 0; i < HOOKS.length; i++) {
      var n = HOOKS[i];
      // typeof on an undeclared identifier is safe (returns "undefined"),
      // so sketches only need to declare the hooks they actually use.
      rebind += 'if(typeof ' + n + '==="function"){p.' + n + "=" + n + ";}";
    }
    // eslint-disable-next-line no-new-func
    return new Function("p", "with(p){\n" + code + "\n}\n" + rebind);
  }

  function setError(fig, message) {
    var stage = fig.querySelector("[data-p5-stage]");
    if (stage) {
      stage.innerHTML =
        '<pre class="pch-p5__error">Sketch error: ' +
        String(message).replace(/</g, "&lt;") +
        "</pre>";
    }
  }

  function initFig(fig) {
    if (fig.dataset.p5Ready === "1") return;
    fig.dataset.p5Ready = "1";

    var stage = fig.querySelector("[data-p5-stage]");
    var code = decode(fig.getAttribute("data-p5-code") || "");
    var toggleBtn = fig.querySelector("[data-p5-toggle]");
    var toggleLabel = toggleBtn && toggleBtn.querySelector(".pch-viz__btn-label");
    var restartBtn = fig.querySelector("[data-p5-restart]");

    var instance = null;
    var running = false;
    var manuallyPaused = reduce; // reduced-motion starts paused
    var built = false;

    function setLabel() {
      if (toggleLabel) toggleLabel.textContent = running ? "Pause" : "Play";
      if (toggleBtn) toggleBtn.setAttribute("aria-pressed", String(!running));
      fig.classList.toggle("is-paused", !running);
    }

    function build() {
      if (built) return;
      built = true;
      try {
        var factory = makeFactory(code);
        instance = new window.p5(factory, stage);
        running = true;
        if (manuallyPaused && instance && instance.noLoop) {
          instance.noLoop();
          running = false;
        }
      } catch (err) {
        setError(fig, (err && err.message) || err);
      }
      setLabel();
    }

    function pause(auto) {
      if (!instance || !running) return;
      if (instance.noLoop) instance.noLoop();
      running = false;
      if (!auto) manuallyPaused = true;
      setLabel();
    }
    function play(auto) {
      if (!instance || running) return;
      if (instance.loop) instance.loop();
      running = true;
      if (!auto) manuallyPaused = false;
      setLabel();
    }

    if (toggleBtn) {
      toggleBtn.addEventListener("click", function () {
        if (!built) build();
        if (running) pause(false);
        else play(false);
      });
    }
    if (restartBtn) {
      restartBtn.addEventListener("click", function () {
        if (instance && instance.remove) instance.remove();
        instance = null;
        built = false;
        manuallyPaused = false;
        build();
      });
    }

    // Lazy build + frugal pause/resume via viewport visibility.
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            if (!built) build();
            else if (!manuallyPaused) play(true);
          } else if (built && !manuallyPaused) {
            pause(true);
          }
        });
      }, { rootMargin: "120px" });
      io.observe(fig);
    } else {
      build();
    }
  }

  function init() {
    var figs = document.querySelectorAll(".pch-p5[data-p5]");
    if (!figs.length) return;
    loadP5()
      .then(function () {
        figs.forEach(initFig);
      })
      .catch(function () {
        figs.forEach(function (fig) {
          setError(fig, "could not load p5.js (offline?)");
        });
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
