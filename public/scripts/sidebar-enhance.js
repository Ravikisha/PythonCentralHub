// Sidebar enhancements: live search, collapse/expand-all, and persisted
// collapse state across page loads. Operates on Starlight's default sidebar
// markup (ul.top-level > li > details/summary | a) rendered inside
// .sidebar-content. No build-time coupling; runs on every full page load.
(function () {
  var STORAGE_KEY = "pch-sidebar-collapsed";

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function loadState() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch (e) {
      return {};
    }
  }

  function saveState(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      /* storage unavailable / full — ignore */
    }
  }

  // Stable key for a <details> group: ancestor group labels joined by " / ".
  function groupKey(details) {
    var labels = [];
    var cur = details;
    while (cur) {
      var summary = cur.querySelector(":scope > summary");
      var span = summary && summary.querySelector(".group-label span");
      labels.unshift(span ? span.textContent.trim() : "");
      cur = cur.parentElement ? cur.parentElement.closest("details") : null;
    }
    return labels.join(" / ");
  }

  function init() {
    var root = document.querySelector(".sidebar-content");
    if (!root) return;
    var list = root.querySelector("ul.top-level");
    var search = document.getElementById("pch-sidebar-search");
    var toggleAll = document.getElementById("pch-sidebar-toggle-all");
    var noResults = document.getElementById("pch-sidebar-noresults");
    if (!list) return;

    var allDetails = function () {
      return Array.prototype.slice.call(list.querySelectorAll("details"));
    };

    // --- Persisted collapse state ---------------------------------------
    var state = loadState();

    // Apply saved state. Never collapse a group that holds the current page.
    allDetails().forEach(function (d) {
      var key = groupKey(d);
      if (!(key in state)) return;
      var hasCurrent = !!d.querySelector('[aria-current="page"]');
      if (state[key] === false && !hasCurrent) {
        d.open = false;
      } else if (state[key] === true) {
        d.open = true;
      }
    });

    // Persist on every user toggle.
    allDetails().forEach(function (d) {
      d.addEventListener("toggle", function () {
        if (search && search.value.trim()) return; // ignore search-driven toggles
        state[groupKey(d)] = d.open;
        saveState(state);
        syncToggleAllLabel();
      });
    });

    // --- Collapse / Expand all ------------------------------------------
    function syncToggleAllLabel() {
      if (!toggleAll) return;
      var anyOpen = allDetails().some(function (d) {
        return d.open;
      });
      var label = toggleAll.querySelector(".pch-toggle-label");
      // Labels are rendered onto the button by Sidebar.astro via
      // Astro.locals.t, so this file carries no translatable copy.
      var collapseLabel = toggleAll.dataset.labelCollapse || "Collapse all";
      var expandLabel = toggleAll.dataset.labelExpand || "Expand all";
      if (label) label.textContent = anyOpen ? collapseLabel : expandLabel;
      toggleAll.setAttribute("aria-expanded", anyOpen ? "true" : "false");
    }

    if (toggleAll) {
      toggleAll.addEventListener("click", function () {
        var anyOpen = allDetails().some(function (d) {
          return d.open;
        });
        var open = !anyOpen; // if any open -> collapse all, else expand all
        allDetails().forEach(function (d) {
          d.open = open;
          state[groupKey(d)] = open;
        });
        saveState(state);
        syncToggleAllLabel();
      });
      syncToggleAllLabel();
    }

    // --- Live search -----------------------------------------------------
    // Returns true if the li (link or group) matches and should stay visible.
    function filterLi(li, q) {
      var details = li.querySelector(":scope > details");
      if (details) {
        var childMatch = false;
        var childItems = details.querySelectorAll(":scope > ul > li");
        Array.prototype.forEach.call(childItems, function (child) {
          if (filterLi(child, q)) childMatch = true;
        });
        // Group label itself can match too.
        var lbl = details.querySelector(":scope > summary .group-label span");
        var selfMatch = lbl && lbl.textContent.toLowerCase().indexOf(q) !== -1;
        var visible = childMatch || selfMatch;
        li.classList.toggle("pch-hidden", !visible);
        if (visible) details.open = true; // expand to reveal matches
        return visible;
      }
      var link = li.querySelector(":scope > a");
      var match = link && link.textContent.toLowerCase().indexOf(q) !== -1;
      li.classList.toggle("pch-hidden", !match);
      return !!match;
    }

    function restoreFromState() {
      allDetails().forEach(function (d) {
        var key = groupKey(d);
        var hasCurrent = !!d.querySelector('[aria-current="page"]');
        if (key in state) {
          d.open = state[key] === true || hasCurrent;
        }
      });
    }

    if (search) {
      search.addEventListener("input", function () {
        var q = search.value.trim().toLowerCase();
        if (!q) {
          // clear filter, restore persisted collapse state
          Array.prototype.forEach.call(
            list.querySelectorAll("li.pch-hidden"),
            function (li) {
              li.classList.remove("pch-hidden");
            }
          );
          restoreFromState();
          syncToggleAllLabel();
          if (noResults) noResults.hidden = true;
          return;
        }
        var any = false;
        var topItems = list.querySelectorAll(":scope > li");
        Array.prototype.forEach.call(topItems, function (li) {
          if (filterLi(li, q)) any = true;
        });
        if (noResults) noResults.hidden = any;
      });

      // Esc clears the search.
      search.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && search.value) {
          e.preventDefault();
          search.value = "";
          search.dispatchEvent(new Event("input"));
        }
      });
    }
  }

  ready(init);
})();
