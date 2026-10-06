import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';

/* Theme mermaid to the "Interactive Shell" palette so diagrams read as part
   of the site rather than a stock white chart. The render pane is always the
   editor-ink surface (see .mermaid-diagram in viz.css), so we use light text
   on dark nodes in both site themes for a consistent instrument look. */
const ink = '#0d1117';
const surface = '#161b22';
const blue = '#4b8bbe';
const blueBright = '#6ba9dd';
const amber = '#ffd343';
const text = '#d7dde5';
const line = 'rgba(139, 148, 158, 0.5)';

mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  fontFamily: "'Atkinson Hyperlegible', 'Poppins', sans-serif",
  themeVariables: {
    background: 'transparent',
    primaryColor: surface,
    primaryBorderColor: blue,
    primaryTextColor: text,
    secondaryColor: '#1d2632',
    secondaryBorderColor: blueBright,
    secondaryTextColor: text,
    tertiaryColor: ink,
    tertiaryBorderColor: line,
    tertiaryTextColor: text,
    mainBkg: surface,
    nodeBorder: blue,
    nodeTextColor: text,
    lineColor: blueBright,
    textColor: text,
    titleColor: amber,
    edgeLabelBackground: ink,
    clusterBkg: 'rgba(75, 139, 190, 0.08)',
    clusterBorder: line,
    // Sequence / flow accents
    actorBkg: surface,
    actorBorder: blue,
    actorTextColor: text,
    signalColor: blueBright,
    signalTextColor: text,
    labelBoxBkgColor: ink,
    labelBoxBorderColor: blue,
    labelTextColor: text,
    noteBkgColor: 'rgba(255, 211, 67, 0.14)',
    noteBorderColor: amber,
    noteTextColor: text,
    // State / class
    fillType0: surface,
    fillType1: '#1d2632',
    // Pie
    pie1: blue,
    pie2: amber,
    pie3: blueBright,
    pie4: '#a5d6a4',
  },
});

/* `startOnLoad` rendered once, at load. The site navigates between pages on the
   client, so a diagram reached by clicking a link in the contents never got
   rendered and the reader saw the diagram's source instead. `run()` is
   idempotent -- mermaid marks what it has drawn with `data-processed` -- so the
   shell can call it after every navigation. */
/* Each diagram is drawn as it comes within a screen or so of the viewport,
   not all at once at load: a lesson can hold a dozen, and laying them all out
   up front blocked the main thread for seconds on a phone. */
let observer = null;

function draw(nodes) {
  if (nodes.length) mermaid.run({ nodes });
}

export function run() {
  const nodes = Array.from(
    document.querySelectorAll("pre.mermaid:not([data-processed]):not([data-queued])"),
  );
  if (!nodes.length) return;
  if (!("IntersectionObserver" in window)) {
    draw(nodes);
    return;
  }
  observer ??= new IntersectionObserver(
    (entries) => {
      const ready = entries.filter((e) => e.isIntersecting).map((e) => e.target);
      for (const el of ready) observer.unobserve(el);
      draw(ready);
    },
    { rootMargin: "800px 0px" },
  );
  for (const el of nodes) {
    el.dataset.queued = "true";
    observer.observe(el);
  }
}

window.__pchMermaid = { run };
run();
