/* RSSN Provider Inventory: search, filtering, sorting and views for the directory page.
   Cards and table rows are rendered by Jekyll; this script shows/hides and reorders them,
   switches between the card and table views, and builds the filter panel from the
   provider data embedded in the page. */
(function () {
  "use strict";

  var dataEl = document.getElementById("provider-data");
  var taxEl = document.getElementById("taxonomy-data");
  var fieldsEl = document.getElementById("fields-data");
  if (!dataEl || !taxEl || !fieldsEl) return;

  var providers = JSON.parse(dataEl.textContent);
  var taxonomy = JSON.parse(taxEl.textContent);
  var fieldConfig = JSON.parse(fieldsEl.textContent);

  function labelOf(o) { return (o && typeof o === "object") ? (o.label || o.name) : String(o); }
  function asList(v) {
    if (v === null || v === undefined || v === "") return [];
    return Array.isArray(v) ? v.filter(function (x) { return x !== null && x !== ""; }) : [v];
  }

  var serviceDetail = {};
  (taxonomy.services || []).forEach(function (s) { serviceDetail[s.name] = s.detail || ""; });

  // Every listing field, keyed for lookup (label, type, options list), from _data/fields.yml.
  var FIELDS = {};
  (fieldConfig.sections || []).forEach(function (sec) {
    sec.fields.forEach(function (f) { FIELDS[f.key] = f; });
  });

  // Facet groups, in display order, from the "filters" list in _data/fields.yml.
  // Options follow the questionnaire order in _data/taxonomy.yml, except services, which sort by count.
  var GROUPS = [];
  (fieldConfig.filters || []).forEach(function (block) {
    block.fields.forEach(function (cfg, i) {
      var f = FIELDS[cfg.key];
      if (!f) return;
      GROUPS.push({
        key: cfg.key,
        label: f.label,
        heading: i === 0 ? block.heading : null,
        open: !!cfg.open,
        limit: cfg.limit || 0,
        byCount: cfg.key === "services" || cfg.key === "strengths",
        single: f.type === "one" && ["institution", "school", "availability", "team_type"].indexOf(cfg.key) === -1,
        order: (taxonomy[f.options] || []).map(labelOf),
        get: function (p) { return asList(p[cfg.key]); }
      });
    });
  });

  // Precompute a lowercase search string per provider: every field, write-in answers,
  // and service details, so e.g. "kubernetes" finds teams offering Containerization and Cloud Computing.
  providers.forEach(function (p) {
    var parts = [p.title, p.unit, p.contact, p.description];
    Object.keys(FIELDS).forEach(function (k) {
      parts.push(asList(p[k]).join(" "));
      if (p[k + "_other"]) parts.push(p[k + "_other"]);
    });
    asList(p.services).concat(asList(p.strengths)).forEach(function (s) { parts.push(serviceDetail[s] || ""); });
    p._haystack = parts.join(" ").toLowerCase();
  });

  // Teams that only serve their own unit ("internal: true" availability answers) are
  // hidden unless the pre-checked "outside requests only" box is unchecked.

  var state = { q: "", sel: {}, expanded: {}, showInternal: false, view: "cards", sort: "", dir: "asc" };
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
    empty: document.getElementById("empty-state"),
    emptyExtra: document.getElementById("empty-extra"),
    scope: document.getElementById("scope-toggle"),
    outsideOnly: document.getElementById("outside-only"),
    results: document.querySelector(".results"),
    controls: document.getElementById("results-controls"),
    sort: document.getElementById("sort"),
    viewButtons: document.querySelectorAll(".view-switch [data-view]"),
    expandAll: document.getElementById("expand-all"),
    table: document.getElementById("provider-table")
  };
  var defaultEmptyText = els.emptyExtra.textContent;

  var cards = {};
  els.grid.querySelectorAll(".card").forEach(function (c) { cards[c.getAttribute("data-id")] = c; });
  var rows = {};
  els.table.querySelectorAll("tbody[data-id]").forEach(function (b) { rows[b.getAttribute("data-id")] = b; });

  els.scope.hidden = false;
  els.controls.hidden = false;

  /* ---------- sorting ---------- */
  // Answer-list columns sort in questionnaire order (their order in _data/taxonomy.yml),
  // not alphabetically. "Varies"-type answers sort after the real answers and blanks come
  // last, whichever direction is chosen. Ties fall back to team name A-Z.
  var TRAILING = { "Varies based on project": true, "It's complicated": true };
  function listOrder(key) { return (taxonomy[key] || []).map(labelOf); }
  var SORTS = {
    title: function (p) { return { tier: 0, v: (p.title || "").toLowerCase() }; },
    school: function (p) { return p.schoolShort ? { tier: 0, v: p.schoolShort.toLowerCase() } : { tier: 2, v: "" }; },
    availability: answerSort("availability"),
    lead_time: answerSort("lead_time"),
    accepting: answerSort("accepting")
  };
  function answerSort(key) {
    var order = listOrder(key);
    return function (p) {
      var val = p[key];
      if (!val) return { tier: 2, v: 0 };
      if (TRAILING[val]) return { tier: 1, v: 0 };
      var i = order.indexOf(val);
      return i === -1 ? { tier: 1, v: 1 } : { tier: 0, v: i };
    };
  }
  var startIndex = {};
  providers.forEach(function (p, i) { startIndex[p.id] = i; });

  function sortedProviders() {
    var list = providers.slice();
    if (!state.sort) {
      return list.sort(function (a, b) { return startIndex[a.id] - startIndex[b.id]; });
    }
    var fn = SORTS[state.sort];
    var sign = state.dir === "desc" ? -1 : 1;
    return list.sort(function (a, b) {
      var x = fn(a), y = fn(b);
      if (x.tier !== y.tier) return x.tier - y.tier;
      if (x.v !== y.v) return (x.v < y.v ? -1 : 1) * sign;
      return a.title.localeCompare(b.title);
    });
  }

  function applyOrder() {
    sortedProviders().forEach(function (p) {
      if (cards[p.id]) els.grid.appendChild(cards[p.id]);
      if (rows[p.id]) els.table.appendChild(rows[p.id]);
    });
    els.sort.value = state.sort;
    els.table.querySelectorAll("th[data-sort]").forEach(function (th) {
      if (th.getAttribute("data-sort") === state.sort) {
        th.setAttribute("aria-sort", state.dir === "desc" ? "descending" : "ascending");
      } else {
        th.removeAttribute("aria-sort");
      }
    });
  }

  function setSort(key, dir) {
    state.sort = key;
    state.dir = dir || "asc";
    applyOrder();
    writeURL();
  }

  /* ---------- views ---------- */
  function setView(view) {
    state.view = view;
    els.results.classList.toggle("results--table", view === "table");
    els.viewButtons.forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-view") === view));
    });
    els.expandAll.hidden = view !== "table";
    writeURL();
  }

  function setExpanded(body, open) {
    var btn = body.querySelector(".row-toggle");
    var details = body.querySelector(".ptable__details");
    btn.setAttribute("aria-expanded", String(open));
    details.hidden = !open;
    body.classList.toggle("is-open", open);
  }

  function syncExpandAll() {
    var visible = Object.keys(rows).filter(function (id) { return !rows[id].hidden; });
    var anyClosed = visible.some(function (id) { return !rows[id].classList.contains("is-open"); });
    els.expandAll.textContent = anyClosed || !visible.length ? "Expand all" : "Collapse all";
  }

  /* ---------- state <-> URL ---------- */
  function readURL() {
    var params = new URLSearchParams(window.location.search);
    state.q = params.get("q") || "";
    state.showInternal = params.get("internal") === "show";
    state.view = params.get("view") === "table" ? "table" : "cards";
    state.sort = SORTS.hasOwnProperty(params.get("sort")) ? params.get("sort") : "";
    state.dir = params.get("dir") === "desc" ? "desc" : "asc";
    GROUPS.forEach(function (g) {
      state.sel[g.key] = new Set(params.getAll(g.key));
    });
  }

  function writeURL() {
    var params = new URLSearchParams();
    if (state.q) params.set("q", state.q);
    if (state.showInternal) params.set("internal", "show");
    if (state.view === "table") params.set("view", "table");
    if (state.sort) params.set("sort", state.sort);
    if (state.sort && state.dir === "desc") params.set("dir", "desc");
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

  // Internal teams count only when the box is unchecked.
  function inScope(p) {
    return state.showInternal || !p.internal;
  }

  // Providers matching the search and every group except `exceptKey`.
  // `ignoreScope` includes internal teams regardless of the toggle (to count what it hides).
  function filtered(exceptKey, ignoreScope) {
    return providers.filter(function (p) {
      return (ignoreScope || inScope(p)) && matchesText(p) && GROUPS.every(function (g) {
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
    if (g.byCount) {
      keys.sort(function (a, b) { return all[b] - all[a] || a.localeCompare(b); });
    } else if (g.order && g.order.length) {
      keys.sort(function (a, b) {
        var ia = g.order.indexOf(a), ib = g.order.indexOf(b);
        return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib) || a.localeCompare(b);
      });
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
      if (!opts.length) return g.heading ? '<h3 class="facets__heading">' + esc(g.heading) + '</h3>' : "";
      var isOpen = (g.key in openState) ? openState[g.key] : (g.open || state.sel[g.key].size > 0);
      var limit = g.limit && !state.expanded[g.key] ? g.limit : Infinity;
      // Keep selected options visible even when the list is collapsed.
      var shown = opts.filter(function (o, i) { return i < limit || state.sel[g.key].has(o.value); });
      var hiddenCount = opts.length - shown.length;

      var rows = shown.map(function (o) {
        var id = "f-" + g.key + "-" + o.value.replace(/[^a-z0-9]+/gi, "-").toLowerCase();
        var checked = state.sel[g.key].has(o.value);
        var dim = !checked && o.count === 0 ? " facet__row--empty" : "";
        var title = g.byCount && serviceDetail[o.value] ? ' title="' + esc(serviceDetail[o.value]) + '"' : "";
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

      var heading = g.heading ? '<h3 class="facets__heading">' + esc(g.heading) + '</h3>' : "";
      return heading + '<details class="facet" data-group="' + g.key + '"' + (isOpen ? " open" : "") + '>' +
        '<summary>' + esc(g.label) + '</summary><div class="facet__options">' + rows + more + '</div></details>';
    }).join("");

    els.facets.innerHTML = html;
  }

  function renderActive() {
    var pills = [];
    GROUPS.forEach(function (g) {
      state.sel[g.key].forEach(function (v) {
        pills.push('<li><button type="button" class="pill" data-group="' + g.key + '" value="' + esc(v) + '" title="' + esc(g.label) + '">' +
          (g.single ? esc(g.label) + ": " : "") + esc(v) + '<span class="visually-hidden"> (remove filter)</span><span aria-hidden="true"> ×</span></button></li>');
      });
    });
    els.active.innerHTML = pills.join("");
    els.toggle.textContent = pills.length ? "Filters (" + pills.length + ")" : "Filters";
  }

  function plural(n, word) { return n + " " + word + (n === 1 ? "" : "s"); }

  function renderResults() {
    var matches = filtered(null);
    var ids = new Set(matches.map(function (p) { return p.id; }));
    Object.keys(cards).forEach(function (id) { cards[id].hidden = !ids.has(id); });
    Object.keys(rows).forEach(function (id) { rows[id].hidden = !ids.has(id); });
    syncExpandAll();

    var forQ = state.q ? " for “" + esc(state.q) + "”" : "";
    els.emptyExtra.textContent = defaultEmptyText;

    var n = matches.length;
    var hidden = state.showInternal ? 0 : filtered(null, true).length - n;
    var label = "<strong>" + n + "</strong> provider" + (n === 1 ? "" : "s") + forQ;
    if (hidden > 0) {
      label += ' <span class="results__aside">· ' + plural(hidden, "internal-only team") + ' hidden. ' +
        '<button type="button" class="text-button" id="show-internal">Show</button></span>';
    }
    els.count.innerHTML = label;
    els.empty.hidden = n !== 0;
    if (n === 0 && hidden > 0) {
      els.emptyExtra.textContent = plural(hidden, "team") + " that only " + (hidden === 1 ? "serves its" : "serve their") +
        " own unit " + (hidden === 1 ? "matches" : "match") + ". Uncheck “Only show teams that take requests from outside their unit” to see " +
        (hidden === 1 ? "it" : "them") + ".";
    }
  }

  function setShowInternal(show) {
    state.showInternal = show;
    els.outsideOnly.checked = !show;
    render();
  }

  els.outsideOnly.addEventListener("change", function () { setShowInternal(!els.outsideOnly.checked); });
  els.count.addEventListener("click", function (e) {
    if (e.target.id === "show-internal") setShowInternal(true);
  });

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

  // "Clear all" resets search and facets but leaves the outside-requests toggle as it is.
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

  els.sort.addEventListener("change", function () { setSort(els.sort.value, "asc"); });

  els.table.querySelector("thead").addEventListener("click", function (e) {
    var th = e.target.closest("th[data-sort]");
    if (!th || !e.target.closest("button")) return;
    var key = th.getAttribute("data-sort");
    setSort(key, state.sort === key && state.dir === "asc" ? "desc" : "asc");
  });

  els.viewButtons.forEach(function (b) {
    b.addEventListener("click", function () { setView(b.getAttribute("data-view")); });
  });

  els.table.addEventListener("click", function (e) {
    var btn = e.target.closest(".row-toggle");
    if (!btn) return;
    var body = btn.closest("tbody");
    setExpanded(body, !body.classList.contains("is-open"));
    syncExpandAll();
  });

  els.expandAll.addEventListener("click", function () {
    var open = els.expandAll.textContent === "Expand all";
    Object.keys(rows).forEach(function (id) { if (!rows[id].hidden) setExpanded(rows[id], open); });
    syncExpandAll();
  });

  /* ---------- start ---------- */
  readURL();
  els.q.value = state.q;
  els.outsideOnly.checked = !state.showInternal;
  syncLayout();
  applyOrder();
  setView(state.view);
  render();
})();
