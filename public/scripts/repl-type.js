/* Landing-page enhancements: REPL typing animation + bento pointer glow.
   Progressive enhancement — if the markup or JS is absent, the terminal
   still shows every line (see .pch-typing rules in landing.css) and the
   cards still work. No-ops on any page without .pch-landing. */
(function () {
  "use strict";

  var reduce =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function typeTerminal() {
    var term = document.querySelector(".pch-terminal .pch-term-body");
    if (!term) return;
    var lines = Array.prototype.slice.call(term.querySelectorAll(".pch-line"));
    if (!lines.length) return;

    // Reveal-all when motion is reduced; markup is already readable.
    if (reduce) {
      lines.forEach(function (l) { l.classList.add("is-shown"); });
      return;
    }

    term.parentElement.classList.add("pch-typing");
    // Stash & clear each line's HTML so we can retype input lines char by
    // char and pop output lines in whole.
    lines.forEach(function (l) {
      l.dataset.html = l.innerHTML;
      l.innerHTML = "";
    });

    var cursor = document.createElement("span");
    cursor.className = "pch-cursor";
    cursor.textContent = " ";

    var i = 0;
    function nextLine() {
      if (i >= lines.length) {
        // Park a blinking cursor on the last line when done.
        lines[lines.length - 1].appendChild(cursor);
        return;
      }
      var line = lines[i];
      line.classList.add("is-shown");
      var isInput = line.dataset.role === "in" || line.dataset.role === "cont";

      if (!isInput) {
        line.innerHTML = line.dataset.html;
        i++;
        setTimeout(nextLine, 260);
        return;
      }

      // Type input lines: render the prompt immediately, then the tokens.
      line.innerHTML = line.dataset.html;
      var ps = line.querySelector(".pch-ps");
      var payload = line.querySelector(".pch-code");
      if (!payload) { i++; setTimeout(nextLine, 120); return; }

      var full = payload.innerHTML;
      var text = payload.textContent;
      payload.innerHTML = "";
      payload.appendChild(cursor);

      var c = 0;
      function typeChar() {
        c++;
        // Reveal by trimming the source HTML to c visible characters is
        // fragile with tags; simplest robust path: type plain text, then
        // swap to the highlighted HTML at the end.
        payload.textContent = text.slice(0, c);
        payload.appendChild(cursor);
        if (c < text.length) {
          setTimeout(typeChar, 26 + Math.random() * 34);
        } else {
          payload.innerHTML = full; // restore syntax highlighting
          i++;
          setTimeout(nextLine, 320);
        }
      }
      setTimeout(typeChar, 160);
    }
    nextLine();
  }

  function bentoGlow() {
    var cells = document.querySelectorAll(".pch-cell");
    if (!cells.length || reduce) return;
    cells.forEach(function (cell) {
      cell.addEventListener("pointermove", function (e) {
        var r = cell.getBoundingClientRect();
        cell.style.setProperty("--mx", e.clientX - r.left + "px");
        cell.style.setProperty("--my", e.clientY - r.top + "px");
      });
    });
  }

  function init() {
    if (!document.querySelector(".pch-landing")) return;
    typeTerminal();
    bentoGlow();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
