(function () {
  const rootAttr = document.documentElement.getAttribute("data-root");
  const root = rootAttr == null || rootAttr === "" ? "." : rootAttr.replace(/\/$/, "");
  const page = document.body.dataset.page || "home";

  const LANG_DEST = {
    en: { home: "en/home/", support: "en/", privacy: "en/privacy/" },
    "zh-Hans": { home: "", support: "support/", privacy: "privacy/" },
    zh: { home: "", support: "support/", privacy: "privacy/" },
    "zh-CN": { home: "", support: "support/", privacy: "privacy/" },
    "zh-Hant": { home: "zh-Hant/home/", support: "zh-Hant/", privacy: "zh-Hant/privacy/" },
    ja: { home: "ja/home/", support: "ja/", privacy: "ja/privacy/" },
    ko: { home: "ko/home/", support: "ko/", privacy: "ko/privacy/" },
    de: { home: "de/home/", support: "de/", privacy: "de/privacy/" },
    fr: { home: "fr/home/", support: "fr/", privacy: "fr/privacy/" },
    es: { home: "es/home/", support: "es/", privacy: "es/privacy/" },
    it: { home: "it/home/", support: "it/", privacy: "it/privacy/" },
    "pt-BR": { home: "pt-BR/home/", support: "pt-BR/", privacy: "pt-BR/privacy/" },
    ru: { home: "ru/home/", support: "ru/", privacy: "ru/privacy/" },
    ar: { home: "ar/home/", support: "ar/", privacy: "ar/privacy/" },
    hi: { home: "hi/home/", support: "hi/", privacy: "hi/privacy/" }
  };

  function redirectLegacyLang() {
    const query = new URLSearchParams(location.search).get("lang");
    if (!query || !LANG_DEST[query]) return;
    const dest = LANG_DEST[query][page];
    if (dest == null) return;
    const next = dest === "" ? root + "/" : root + "/" + dest;
    const here = location.pathname.replace(/index\.html$/, "");
    const targetPath = new URL(next, location.href).pathname.replace(/index\.html$/, "");
    if (here.replace(/\/$/, "") === targetPath.replace(/\/$/, "")) return;
    location.replace(next);
  }

  function desktopNav() {
    return window.matchMedia("(min-width: 901px)").matches;
  }

  function placeNav() {
    const header = document.querySelector(".site-header");
    const inner = header && header.querySelector(".header-inner");
    const tools = header && header.querySelector(".header-tools");
    const cluster = document.getElementById("nav-cluster");
    const backdrop = document.getElementById("nav-backdrop");
    if (!header || !inner || !tools || !cluster || !backdrop) return;
    if (desktopNav()) {
      if (cluster.parentElement !== inner) inner.insertBefore(cluster, tools);
      if (backdrop.parentElement !== header) header.appendChild(backdrop);
      if (isNavOpen()) closeNav();
      return;
    }
    if (cluster.parentElement !== document.body) {
      document.body.append(backdrop, cluster);
    }
  }

  let scrollLockY = 0;

  function isNavOpen() {
    return Boolean(document.querySelector(".site-header.is-open"));
  }

  function lockScroll() {
    scrollLockY = window.scrollY;
    document.documentElement.classList.add("is-nav-open");
    document.body.classList.add("is-nav-open");
    document.body.style.top = `-${scrollLockY}px`;
  }

  function unlockScroll() {
    document.documentElement.classList.remove("is-nav-open");
    document.body.classList.remove("is-nav-open");
    document.body.style.top = "";
    window.scrollTo(0, scrollLockY);
  }

  function syncToggle(open) {
    const toggle = document.querySelector(".nav-toggle");
    if (!toggle) return;
    const label = open ? toggle.dataset.closeLabel : toggle.dataset.openLabel;
    toggle.setAttribute("aria-expanded", String(open));
    if (label) toggle.setAttribute("aria-label", label);
    const text = toggle.querySelector(".nav-toggle-text");
    if (text && label) text.textContent = label;
  }

  function setNav(open) {
    const header = document.querySelector(".site-header");
    if (!header) return;
    if (open && desktopNav()) return;
    const wasOpen = header.classList.contains("is-open");
    header.classList.toggle("is-open", open);
    const backdrop = document.getElementById("nav-backdrop");
    if (backdrop) backdrop.hidden = !open;
    syncToggle(open);
    if (open && !wasOpen) lockScroll();
    if (!open && wasOpen) unlockScroll();
  }

  function closeNav() {
    setNav(false);
  }

  const BEAD = {
    c: "#c44732",
    o: "#e39a12",
    w: "#fff6e8",
    s: "#5f8a52",
    k: "#9a2216"
  };

  const PATTERNS = {
    fox: [
      "...............",
      "....ccc.ccc....",
      "...coooooooc...",
      "..cowoowoowoc..",
      "..cowoowoowoc..",
      "...csss.sssc...",
      "....s.s.s.s....",
      "......s.s......",
      "......www......",
      ".....wwwww.....",
      "....www.www....",
      "...k..........."
    ],
    bloom: [
      "...............",
      "......c.c......",
      "....coooooc....",
      "...cooooooooc..",
      "....coowwooc...",
      "...cooowwoooc..",
      "....coowwooc...",
      "...cooooooooc..",
      "....coooooc....",
      "......c.c......",
      ".......s.......",
      "......sss......"
    ],
    mini: [
      ".......",
      ".c.o.s.",
      "..c.o..",
      ".s.k.s.",
      "..o.c..",
      ".s.o.c.",
      "......."
    ]
  };

  function drawPegboard(host, name) {
    if (!host) return;
    const peg = PATTERNS[name] || PATTERNS.fox;
    const cols = peg[0].length;
    const rows = peg.length;
    const cell = 22;
    const pad = 16;
    const width = cols * cell + pad * 2;
    const height = rows * cell + pad * 2;
    let marks = "";
    peg.forEach((row, y) => {
      [...row].forEach((ch, x) => {
        const cx = pad + x * cell + cell / 2;
        const cy = pad + y * cell + cell / 2;
        marks += `<circle cx="${cx}" cy="${cy}" r="2.1" fill="#d5c7b5"/>`;
        if (!BEAD[ch]) return;
        marks += `<g>
          <circle cx="${cx}" cy="${cy}" r="8.4" fill="${BEAD[ch]}" stroke="#3d3129" stroke-opacity="0.12" stroke-width="0.7"/>
          <circle cx="${cx - 2.1}" cy="${cy - 2.2}" r="2.1" fill="rgba(255,255,255,0.34)"/>
          <circle cx="${cx}" cy="${cy}" r="2.5" fill="#f4ede3"/>
        </g>`;
      });
    });
    host.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-hidden="true">${marks}</svg>`;
  }

  function fixLostLinks() {
    if (document.body.dataset.page !== "lost") return;
    if (location.pathname.startsWith("/beadtime-site")) return;
    document.querySelectorAll('.lost-actions a[href^="/beadtime-site"]').forEach((anchor) => {
      const next = anchor.getAttribute("href").replace("/beadtime-site", "") || "/";
      anchor.setAttribute("href", next);
    });
  }

  redirectLegacyLang();
  fixLostLinks();

  const toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      setNav(!document.querySelector(".site-header")?.classList.contains("is-open"));
    });
  }

  document.addEventListener("click", (event) => {
    if (event.target.closest(".site-nav a")) {
      closeNav();
      return;
    }
    if (event.target.closest("#nav-backdrop") || event.target.classList.contains("nav-backdrop")) {
      closeNav();
    }
    if (!event.target.closest(".locale-picker")) {
      document.querySelectorAll(".locale-picker details[open]").forEach((node) => {
        node.removeAttribute("open");
      });
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !isNavOpen()) return;
    closeNav();
    document.querySelector(".nav-toggle")?.focus();
  });

  window.addEventListener("resize", placeNav);
  placeNav();
  drawPegboard(document.getElementById("pegboard"), "fox");
  drawPegboard(document.getElementById("loop-board"), "bloom");
  drawPegboard(document.getElementById("lost-board"), "mini");
})();
