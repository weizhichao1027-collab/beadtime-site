(function () {
  const STORAGE_KEY = "beadtime-lang";
  const I18N = window.BEADTIME_I18N || {};
  const rawRoot = document.documentElement.getAttribute("data-root");
  const root = (rawRoot == null ? "." : rawRoot).replace(/\/$/, "");
  const page = document.body.dataset.page || "home";

  function detectLang() {
    const query = new URLSearchParams(location.search).get("lang");
    if (query === "zh" || query === "zh-Hans" || query === "zh-CN") return "zh-Hans";
    if (query === "en") return "en";
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "zh-Hans" || stored === "en") return stored;
    const nav = (navigator.language || "en").toLowerCase();
    return nav.startsWith("zh") ? "zh-Hans" : "en";
  }

  let lang = detectLang();
  let faqIndex = 1;
  let scrollLockY = 0;

  function t(key) {
    return (I18N[lang] && I18N[lang][key]) || (I18N.en && I18N.en[key]) || key;
  }

  function href(path) {
    const clean = path.replace(/^\//, "");
    if (root === "") return "/" + clean;
    return root + "/" + clean;
  }

  function asset(path) {
    return href(path.replace(/^\//, ""));
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
    const label = t(open ? "navClose" : "navOpen");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", label);
    const text = toggle.querySelector("[data-i18n]");
    if (text) text.textContent = label;
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

  function apply() {
    document.documentElement.lang = lang === "zh-Hans" ? "zh-Hans" : "en";
    document.querySelectorAll("[data-i18n]").forEach((node) => {
      node.textContent = t(node.dataset.i18n);
    });
    document.querySelectorAll("[data-i18n-alt]").forEach((node) => {
      node.setAttribute("alt", t(node.dataset.i18nAlt));
    });
    const titleKey = document.body.dataset.titleKey;
    if (titleKey) document.title = t(titleKey);
    const desc = document.querySelector('meta[name="description"]');
    if (desc && document.body.dataset.descKey) {
      desc.setAttribute("content", t(document.body.dataset.descKey));
    }
    document.querySelectorAll("[data-lang-btn]").forEach((btn) => {
      btn.setAttribute("aria-pressed", String(btn.dataset.langBtn === lang));
    });
    const nav = document.querySelector(".site-nav");
    if (nav) nav.setAttribute("aria-label", t("navAria"));
    const langSwitch = document.querySelector(".lang-switch");
    if (langSwitch) langSwitch.setAttribute("aria-label", t("langAria"));
    const faqList = document.getElementById("faq-list");
    if (faqList) faqList.setAttribute("aria-label", t("faqTitle"));
    const toc = document.querySelector(".toc");
    if (toc) toc.setAttribute("aria-label", t("tocLabel"));
    syncToggle(isNavOpen());
    renderFaq();
  }

  function setLang(next) {
    lang = next;
    localStorage.setItem(STORAGE_KEY, next);
    const url = new URL(location.href);
    url.searchParams.set("lang", next);
    history.replaceState({}, "", url);
    apply();
  }

  function mountChrome() {
    const header = document.getElementById("site-header");
    const footer = document.getElementById("site-footer");
    if (header) {
      header.className = "site-header";
      header.innerHTML = `
        <div class="wrap header-inner">
          <a class="brand" href="${href("index.html")}">
            <img class="brand-mark" src="${asset("assets/img/favicon.svg")}" alt="" width="36" height="36">
            <span class="brand-name">
              <strong data-i18n="brandZh"></strong>
              <span data-i18n="brandEn"></span>
            </span>
          </a>
          <div class="nav-cluster" id="nav-cluster">
            <nav class="site-nav">
              <a href="${href("index.html")}" data-nav="home" data-i18n="navHome"></a>
              <a href="${href("support/")}" data-nav="support" data-i18n="navSupport"></a>
              <a href="${href("privacy/")}" data-nav="privacy" data-i18n="navPrivacy"></a>
            </nav>
          </div>
          <div class="header-tools">
            <div class="lang-switch" role="group">
              <button type="button" data-lang-btn="zh-Hans" data-i18n="langZh"></button>
              <button type="button" data-lang-btn="en" data-i18n="langEn"></button>
            </div>
            <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-cluster">
              <span class="nav-toggle-bars" aria-hidden="true"></span>
              <span data-i18n="navOpen"></span>
            </button>
          </div>
        </div>
        <div class="nav-backdrop" id="nav-backdrop" hidden></div>`;
      const current = header.querySelector(`[data-nav="${page}"]`);
      if (current) current.setAttribute("aria-current", "page");
      header.querySelector(".nav-toggle").addEventListener("click", () => {
        setNav(!header.classList.contains("is-open"));
      });
    }
    if (footer) {
      footer.className = "site-footer";
      footer.innerHTML = `
        <div class="wrap footer-grid">
          <div>
            <strong data-i18n="brandZh"></strong>
            <p data-i18n="brandEn"></p>
          </div>
          <div>
            <h2 data-i18n="footerExplore"></h2>
            <ul>
              <li><a href="${href("index.html")}" data-i18n="navHome"></a></li>
              <li><a href="https://apps.apple.com/app/id6799906107" data-i18n="ctaStore"></a></li>
            </ul>
          </div>
          <div>
            <h2 data-i18n="footerHelp"></h2>
            <ul>
              <li><a href="${href("support/")}" data-i18n="navSupport"></a></li>
              <li><a href="${href("privacy/")}" data-i18n="navPrivacy"></a></li>
              <li><a href="mailto:281916057@qq.com">281916057@qq.com</a></li>
            </ul>
          </div>
        </div>
        <p class="wrap legal-note" data-i18n="footerCopy"></p>`;
    }
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
    const PEG = PATTERNS[name] || PATTERNS.fox;
    const cols = PEG[0].length;
    const rows = PEG.length;
    const cell = 22;
    const pad = 16;
    const width = cols * cell + pad * 2;
    const height = rows * cell + pad * 2;
    let marks = "";
    PEG.forEach((row, y) => {
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

  function renderFaq() {
    const list = document.getElementById("faq-list");
    const panel = document.getElementById("faq-panel");
    if (!list || !panel) return;
    const keys = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    list.innerHTML = keys
      .map((n) => {
        const selected = n === faqIndex;
        return `<div class="ask-item${selected ? " is-current" : ""}">
          <button type="button" id="faq-q-${n}" aria-pressed="${selected}" aria-expanded="${selected}" aria-controls="faq-a-${n}" data-q="${n}">${t("q" + n)}</button>
          <div class="faq-inline" id="faq-a-${n}">
            <p>${t("a" + n)}</p>
          </div>
        </div>`;
      })
      .join("");
    panel.innerHTML = `<h2>${t("q" + faqIndex)}</h2><p>${t("a" + faqIndex)}</p>`;
  }

  document.addEventListener("click", (event) => {
    const langBtn = event.target.closest("[data-lang-btn]");
    if (langBtn) {
      setLang(langBtn.dataset.langBtn);
      return;
    }
    const q = event.target.closest("#faq-list button[data-q]");
    if (q) {
      faqIndex = Number(q.dataset.q);
      renderFaq();
      return;
    }
    if (event.target.closest(".site-nav a")) {
      closeNav();
      return;
    }
    if (event.target.closest("#nav-backdrop") || event.target.classList.contains("nav-backdrop")) {
      closeNav();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !isNavOpen()) return;
    closeNav();
    document.querySelector(".nav-toggle")?.focus();
  });

  window.addEventListener("resize", placeNav);

  mountChrome();
  placeNav();
  drawPegboard(document.getElementById("pegboard"), "fox");
  drawPegboard(document.getElementById("loop-board"), "bloom");
  drawPegboard(document.getElementById("lost-board"), "mini");
  apply();
})();
