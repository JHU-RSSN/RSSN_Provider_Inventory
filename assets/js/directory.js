/* RSSN Provider Inventory: search and filtering for the directory page.
   Cards are rendered by Jekyll; this script shows/hides them and builds the
   filter panel from the provider data embedded in the page. */
(function () {
  "use strict";

  var dataEl = document.getElementById("provider-data");
  var taxEl = document.getElementById("taxonomy-data");
  if (!dataEl || !taxEl) return;

  var providers = JSON.parse(dataEl.textContent);
  var taxonomy = JSON.parse(taxEl.textContent);

  var serviceDetail = {};
  (taxonomy.services || []).forEach(function (s) { serviceDetail[s.name] = s.detail || ""; });

  // Facet groups, in display order. "order" fixes option order; otherwise options sort by count.
  var GROUPS = [
    { key: "service", label: "Services", get: function (p) { return p.services; }, open: true, limit: 6 },
    { key: "institution", label: "Institution", get: function (p) { return [p.institution]; }, open: true,
      order: taxonomy.institutions },
    { key: "school", label: "School / division", get: function (p) { return [p.school]; }, open: true },
    { key: "availability", label: "Available to", get: function (p) { return [p.availability]; }, open: true,
      order: (taxonomy.availability || []).map(function (a) { return a.label; }) },
    { key: "eligible", label: "Open to", get: function (p) { return p.eligible; }, open: false,
      order: taxonomy.eligible }
  ];

  // Precompute a lowercase search string per provider, including service details
  // so that e.g. "kubernetes" finds teams offering Containerization and Cloud Computing.
  providers.forEach(function (p) {
    p._haystack = [
      p.title, p.institution, p.school, p.unit, p.availability, p.description,
      p.services.join(" "), p.services.map(function (s) { return serviceDetail[s] || ""; }).join(" "),
      p.eligible.join(" ")
    ].join(" ").toLowerCase();
  });

  var state = { q: "", sel: {}, expanded: {} };
  GROUPS.forEach(function (g) { state.sel[g.key] = new Set(); });

  var els = {
    form: document.getElementById("search-form"),
    q: document.getElementById("q"),
    facets: document.getElementById("facets"),
    filters: document.getElementById("filters"),
    toggle: document.getElementById("filters-toggle"),
    clear: document.getElementById("clear-all"),
    count: document.getElementById("results-count"),
    active: document.getElementById("active-filters"),
    grid: document.getElementById("card-grid"),
    empty: document.getElementById("empty-state")
  };

  var cards = {};
  els.grid.querySelectorAll(".card").forEach(function (c) { cards[c.getAttribute("data-id")] = c; });

  /* ---------- state <-> URL ---------- */
  function readURL() {
    var params = new URLSearchParams(window.location.search);
    state.q = params.get("q") || "";
    GROUPS.forEach(function (g) {
      state.sel[g.key] = new Set(params.getAll(g.key));
    });
  }

  function writeURL() {
    var params = new URLSearchParams();
    if (state.q) params.set("q", state.q);
    GROUPS.forEach(function (g) {
      state.sel[g.key].forEach(function (v) { params.append(g.key, v); });
    });
    var qs = params.toString();
    var url = window.location.pathname + (qs ? "?" + qs : "");
    window.history.replaceState(null, "", url);
  }

  /* ---------- matching ---------- */
  function matchesText(p) {
    var terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
    return terms.every(function (t) { return p._haystack.indexOf(t) !== -1; });
  }

  function matchesGroup(p, g) {
    var sel = state.sel[g.key];
    if (!sel.size) return true;
    return g.get(p).some(function (v) { return sel.has(v); });
  }

  // Providers matching the search and every group except `exceptKey`.
  function filtered(exceptKey) {
    return providers.filter(function (p) {
      return matchesText(p) && GROUPS.every(function (g) {
        return g.key === exceptKey || matchesGroup(p, g);
      });
    });
  }

  /* ---------- rendering ---------- */
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function optionsFor(g) {
    // Every value any provider uses, plus anything currently selected.
    var all = {};
    providers.forEach(function (p) { g.get(p).forEach(function (v) { all[v] = 0; }); });
    state.sel[g.key].forEach(function (v) { all[v] = 0; });

    var base = filtered(g.key);
    base.forEach(function (p) {
      g.get(p).forEach(function (v) { if (v in all) all[v] += 1; });
    });

    var keys = Object.keys(all);
    if (g.order) {
      keys.sort(function (a, b) {
        var ia = g.order.indexOf(a), ib = g.order.indexOf(b);
        return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib) || a.localeCompare(b);
      });
    } else if (g.key === "service") {
      keys.sort(function (a, b) { return all[b] - all[a] || a.localeCompare(b); });
    } else {
      keys.sort(function (a, b) { return a.localeCompare(b); });
    }
    return keys.map(function (k) { return { value: k, count: all[k] }; });
  }

  function renderFacets() {
    var openState = {};
    els.facets.querySelectorAll("details").forEach(function (d) {
      openState[d.getAttribute("data-group")] = d.open;
    });

    var html = GROUPS.map(function (g) {
      var opts = optionsFor(g);
      var isOpen = (g.key in openState) ? openState[g.key] : (g.open || state.sel[g.key].size > 0);
      var limit = g.limit && !state.expanded[g.key] ? g.limit : Infinity;
      // Keep selected options visible even when the list is collapsed.
      var shown = opts.filter(function (o, i) { return i < limit || state.sel[g.key].has(o.value); });
      var hiddenCount = opts.length - shown.length;

      var rows = shown.map(function (o) {
        var id = "f-" + g.key + "-" + o.value.replace(/[^a-z0-9]+/gi, "-").toLowerCase();
        var checked = state.sel[g.key].has(o.value);
        var dim = !checked && o.count === 0 ? " facet__row--empty" : "";
        var title = g.key === "service" && serviceDetail[o.value] ? ' title="' + esc(serviceDetail[o.value]) + '"' : "";
        return '<label class="facet__row' + dim + '" for="' + id + '"' + title + '>' +
          '<input type="checkbox" id="' + id + '" data-group="' + g.key + '" value="' + esc(o.value) + '"' + (checked ? " checked" : "") + '>' +
          '<span class="facet__label">' + esc(o.value) + '</span>' +
          '<span class="facet__count">' + o.count + '</span></label>';
      }).join("");

      var more = "";
      if (g.limit && opts.length > g.limit) {
        more = '<button type="button" class="text-button facet__more" data-expand="' + g.key + '">' +
          (state.expanded[g.key] ? "Show fewer" : "Show " + hiddenCount + " more") + '</button>';
      }

      return '<details class="facet" data-group="' + g.key + '"' + (isOpen ? " open" : "") + '>' +
        '<summary>' + esc(g.label) + '</summary><div class="facet__options">' + rows + more + '</div></details>';
    }).join("");

    els.facets.innerHTML = html;
  }

  function renderActive() {
    var pills = [];
    GROUPS.forEach(function (g) {
      state.sel[g.key].forEach(function (v) {
        pills.push('<li><button type="button" class="pill" data-group="' + g.key + '" value="' + esc(v) + '">' +
          esc(v) + '<span class="visually-hidden"> (remove filter)</span><span aria-hidden="true"> ×</span></button></li>');
      });
    });
    els.active.innerHTML = pills.join("");
    els.toggle.textContent = pills.length ? "Filters (" + pills.length + ")" : "Filters";
  }

  function renderResults() {
    var matches = filtered(null);
    var ids = new Set(matches.map(function (p) { return p.id; }));
    Object.keys(cards).forEach(function (id) { cards[id].hidden = !ids.has(id); });

    var n = matches.length;
    var label = "<strong>" + n + "</strong> provider" + (n === 1 ? "" : "s");
    if (state.q) label += " for “" + esc(state.q) + "”";
    els.count.innerHTML = label;
    els.empty.hidden = n !== 0;
  }

  function render() {
    renderFacets();
    renderActive();
    renderResults();
    writeURL();
  }

  /* ---------- events ---------- */
  els.form.addEventListener("submit", function (e) {
    e.preventDefault();
    state.q = els.q.value.trim();
    render();
  });

  // Live search after a short pause while typing.
  var typingTimer;
  els.q.addEventListener("input", function () {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(function () {
      state.q = els.q.value.trim();
      renderFacets(); renderActive(); renderResults(); writeURL();
    }, 200);
  });

  els.facets.addEventListener("change", function (e) {
    var cb = e.target;
    if (!cb.matches('input[type="checkbox"]')) return;
    var sel = state.sel[cb.getAttribute("data-group")];
    if (cb.checked) sel.add(cb.value); else sel.delete(cb.value);
    var focusId = cb.id;
    render();
    var again = document.getElementById(focusId);
    if (again) again.focus();
  });

  els.facets.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-expand]");
    if (!btn) return;
    var key = btn.getAttribute("data-expand");
    state.expanded[key] = !state.expanded[key];
    renderFacets();
  });

  els.active.addEventListener("click", function (e) {
    var btn = e.target.closest(".pill");
    if (!btn) return;
    state.sel[btn.getAttribute("data-group")].delete(btn.value);
    render();
  });

  els.clear.addEventListener("click", function () {
    state.q = "";
    els.q.value = "";
    GROUPS.forEach(function (g) { state.sel[g.key].clear(); });
    render();
  });

  // Filters panel: always visible on wide screens, behind a toggle on narrow ones.
  var narrow = window.matchMedia("(max-width: 860px)");
  function syncLayout() {
    els.toggle.hidden = !narrow.matches;
    if (!narrow.matches) {
      els.filters.hidden = false;
      els.toggle.setAttribute("aria-expanded", "true");
    } else {
      var open = els.toggle.getAttribute("aria-expanded") === "true" && els.toggle.dataset.touched === "1";
      els.filters.hidden = !open;
      els.toggle.setAttribute("aria-expanded", String(open));
    }
  }
  els.toggle.addEventListener("click", function () {
    var open = els.toggle.getAttribute("aria-expanded") !== "true";
    els.toggle.dataset.touched = "1";
    els.toggle.setAttribute("aria-expanded", String(open));
    els.filters.hidden = !open;
  });
  if (narrow.addEventListener) narrow.addEventListener("change", syncLayout);

  /* ---------- start ---------- */
  readURL();
  els.q.value = state.q;
  syncLayout();
  render();
})();
