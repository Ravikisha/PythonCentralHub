// for every code segment there is a data-rehype-pretty-code-fragment and also a after element which is a copy button
// so i need to write the logic where when user clicks on the copy button the code segment is copied to the clipboard
// Legacy code-block title-bar click-to-copy removed.
// Copy is now handled by explicit buttons (e.g. the python playground toolbar).

// Skip-to-content link for keyboard users. Injected as the first focusable
// element so Tab on page load lands here, letting users bypass the nav.
(function () {
  function addSkipLink() {
    if (document.querySelector(".skip-to-content")) return;
    var target = document.getElementById("_top") || document.querySelector("main");
    if (target && !target.id) target.id = "_top";
    var link = document.createElement("a");
    link.href = "#" + (target && target.id ? target.id : "_top");
    link.className = "skip-to-content";
    link.textContent = "Skip to content";
    document.body.insertBefore(link, document.body.firstChild);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", addSkipLink);
  } else {
    addSkipLink();
  }
})();