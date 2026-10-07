/* RSSN Provider Inventory: the "Request a change" page.
   Shows one team's listing as the questionnaire, with every answer choice and the team's
   current answers selected, then turns whatever the visitor changes into a plain-text
   change request to email to RSSN. Nothing is saved or sent by the site.
   Questions and choices come from _data/fields.yml and _data/taxonomy.yml, embedded in
   the page, so this page stays in step with the listing files automatically. */
(function () {
  "use strict";

  function json(id) { var el = document.getElementById(id); return el ? JSON.parse(el.textContent) : null; }
  var config = json("change-config");
  var listings = json("change-listings");
  var taxonomy = json("taxonomy-data");
  var fieldConfig = json("fields-data");
  if (!config || !listings || !taxonomy || !fieldConfig) return;

  var LEVELS = [["not offered", "Not offered"], ["offered", "Offered"], ["strength", "Area of strength"]];
  var MAX_STRENGTHS = 5;
  var MAILTO_LIMIT = 1900;  // longer mailto links get cut off by some email programs

  var picker = document.getElementById("team-picker");
  var select = document.getElementById("team-select");
  var form = document.getElementById("change-form");
  var holder = document.getElementById("change-questions");
  var countEl = document.getElementById("change-count");
  var output = document.getElementById("change-output");
  var summaryEl = document.getElementById("change-summary");
  var helpEl = document.getElementById("change-output-help");
  var mailtoEl = document.getElementById("change-mailto");
  var copyBtn = document.getElementById("change-copy");
  var copyStatus = document.getElementById("change-copy-status");

  var slug = new URLSearchParams(window.location.search).get("team") || "";
  var team = listings[slug];
  select.value = team ? slug : "";
  select.addEventListener("change", function () { if (select.value) picker.submit(); });
  if (!team) return;

  document.title = "Request a change: " + team.title + " · " + document.title.split(" · ").pop();
  var gh = document.getElementById("github-edit-link");
  if (gh && team.path) gh.href = "https://github.com/" + config.repository + "/edit/" + config.branch + "/" + team.path;

  /* ---------- helpers ---------- */
  function labelOf(o) { return (o && typeof o === "object") ? (o.label || o.name) : String(o); }
  function asList(v) {
    if (v === null || v === undefined || v === "") return [];
    return Array.isArray(v) ? v.filter(function (x) { return x !== null && x !== ""; }).map(String) : [String(v)];
  }
  function str(v) { return (v === null || v === undefined) ? "" : String(v); }
  function clean(s) { return str(s).replace(/\r\n/g, "\n").replace(/[ \t]+\n/g, "\n").trim(); }
  function el(tag, attrs, kids) {
    var e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") e.textContent = attrs[k];
      else if (k === "className") e.className = attrs[k];
      else e.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c) e.appendChild(c); });
    return e;
  }
  var uid = 0;
  function nextId(base) { uid += 1; return "chg-" + base + "-" + uid; }
  function optionsFor(f) {
    if (f.options === "schools") return (taxonomy.schools || []).map(function (s) { return s.name; });
    return (taxonomy[f.options] || []).map(labelOf);
  }
  function indent(text) { return text.split("\n").map(function (l) { return "    " + l; }).join("\n"); }

  /* Every question registers { title, block, changes() -> [lines] } */
  var questions = [];

  function questionBlock(title, kind, hint) {
    var block = el("fieldset", { className: "change-q" });
    var legend = el("legend", { className: "change-q__legend" });
    legend.appendChild(el("span", { text: title }));
    if (kind) legend.appendChild(el("span", { className: "change-q__kind", text: kind }));
    legend.appendChild(el("span", { className: "change-q__flag", text: "Changed" }));
    block.appendChild(legend);
    if (hint) block.appendChild(el("p", { className: "change-note", text: hint }));
    return block;
  }

  function choiceInput(type, name, value, checked, text, detail, nowText) {
    var id = nextId(name);
    var input = el("input", { type: type, name: name, id: id, value: value });
    input.checked = !!checked;
    input.defaultChecked = !!checked;
    var label = el("label", { className: "change-choice" + (checked ? " is-current" : ""), "for": id }, [input]);
    var textWrap = el("span", { className: "change-choice__text" });
    textWrap.appendChild(el("span", { text: text }));
    if (checked) textWrap.appendChild(el("span", { className: "change-choice__now", text: nowText || "current answer" }));
    if (detail) textWrap.appendChild(el("span", { className: "change-choice__detail", text: detail }));
    label.appendChild(textWrap);
    return { label: label, input: input };
  }

  function textInput(id, value, multiline, labelText) {
    var wrap = el("div", { className: "change-text" });
    if (labelText) wrap.appendChild(el("label", { className: "change-q__label", "for": id, text: labelText }));
    var input = multiline ? el("textarea", { id: id, rows: Math.min(10, Math.max(3, str(value).split("\n").length + 1)) })
                          : el("input", { id: id, type: "text" });
    input.value = str(value);
    wrap.appendChild(input);
    return { wrap: wrap, input: input };
  }

  function otherPart(block, f, name) {
    if (!f.other && !team[f.key + "_other"]) return null;
    var t = textInput(nextId(name + "-other"), team[f.key + "_other"], false, "Other (write in)");
    block.appendChild(t.wrap);
    var orig = clean(team[f.key + "_other"]);
    return function () {
      var now = clean(t.input.value);
      return now === orig ? [] : ["  Other (write-in): " + (orig ? '"' + orig + '"' : "(blank)") + " -> " + (now ? '"' + now + '"' : "(blank)")];
    };
  }

  /* ---------- question types ---------- */
  function addOne(title, key, value, opts, f, hint, allowWritein) {
    var block = questionBlock(title, "Choose one", hint);
    var name = key;
    var orig = str(value);
    var choices = opts.slice();
    if (orig && choices.indexOf(orig) === -1) choices.push(orig);
    if (!orig) choices.push("");
    var inputs = choices.map(function (o) {
      var c = choiceInput("radio", name, o, o === orig, o || "No answer");
      block.appendChild(c.label);
      return c.input;
    });
    var writein = null;
    if (allowWritein) {
      writein = textInput(nextId(name + "-other"), "", false, "Not listed? Write it in");
      block.appendChild(writein.wrap);
    }
    var other = f ? otherPart(block, f, name) : null;
    questions.push({ block: block, title: title, changes: function () {
      var picked = inputs.filter(function (i) { return i.checked; })[0];
      var now = writein && clean(writein.input.value) ? clean(writein.input.value) : (picked ? picked.value : "");
      var lines = now === orig ? [] : ["  Was: " + (orig || "(no answer)"), "  Now: " + (now || "(no answer)")];
      return lines.concat(other ? other() : []);
    }});
    return block;
  }

  function addMany(title, f, hint) {
    var block = questionBlock(title, "Choose all that apply", hint);
    var orig = asList(team[f.key]);
    var choices = optionsFor(f);
    orig.forEach(function (v) { if (choices.indexOf(v) === -1) choices.push(v); });
    var inputs = choices.map(function (o) {
      var c = choiceInput("checkbox", f.key, o, orig.indexOf(o) !== -1, o);
      block.appendChild(c.label);
      return c.input;
    });
    var other = otherPart(block, f, f.key);
    questions.push({ block: block, title: title, changes: function () {
      var add = [], remove = [];
      inputs.forEach(function (i) {
        var was = orig.indexOf(i.value) !== -1;
        if (i.checked && !was) add.push(i.value);
        if (!i.checked && was) remove.push(i.value);
      });
      var lines = [];
      if (add.length) lines.push("  Add: " + add.join("; "));
      if (remove.length) lines.push("  Remove: " + remove.join("; "));
      return lines.concat(other ? other() : []);
    }});
    return block;
  }

  function addText(title, key, value, multiline, hint) {
    var block = questionBlock(title, multiline ? "Free text" : null, hint);
    var t = textInput(nextId(key), value, multiline, null);
    t.input.setAttribute("aria-label", title);
    block.appendChild(t.wrap);
    var orig = clean(value);
    questions.push({ block: block, title: title, changes: function () {
      var now = clean(t.input.value);
      if (now === orig) return [];
      if (!multiline) return ["  Was: " + (orig || "(blank)"), "  Now: " + (now || "(blank)")];
      return now ? ["  New text:", indent(now)] : ["  Remove this text"];
    }});
    return block;
  }

  function addServices(title, f) {
    var block = questionBlock(title, "One choice per service",
      "For each service, choose Not offered, Offered, or Area of strength (offered, and one of your team's strongest areas). Mark no more than five areas of strength.");
    var levels = team.services && typeof team.services === "object" && !Array.isArray(team.services) ? team.services : {};
    var counter = el("p", { className: "change-strengths", "aria-live": "polite" });
    block.appendChild(counter);
    var rows = [];
    (taxonomy.service_groups || []).forEach(function (g) {
      block.appendChild(el("h3", { className: "change-group", text: g }));
      (taxonomy.services || []).filter(function (s) { return s.group === g; }).forEach(function (s) {
        var orig = str(levels[s.name] || "not offered").toLowerCase().trim();
        var row = el("div", { className: "change-svc", role: "radiogroup", "aria-label": s.name });
        var head = el("div", { className: "change-svc__name" });
        head.appendChild(el("span", { text: s.name }));
        if (s.detail) head.appendChild(el("span", { className: "change-choice__detail", text: s.detail }));
        row.appendChild(head);
        var opts = el("div", { className: "change-svc__levels" });
        var inputs = LEVELS.map(function (lv) {
          var c = choiceInput("radio", "svc-" + s.name, lv[0], lv[0] === orig, lv[1], null, "current");
          opts.appendChild(c.label);
          return c.input;
        });
        row.appendChild(opts);
        block.appendChild(row);
        rows.push({ name: s.name, orig: orig, inputs: inputs });
      });
    });
    function current(r) { var i = r.inputs.filter(function (x) { return x.checked; })[0]; return i ? i.value : r.orig; }
    function word(v) { return LEVELS.filter(function (l) { return l[0] === v; }).map(function (l) { return l[1]; })[0] || v; }
    function updateCounter() {
      var n = rows.filter(function (r) { return current(r) === "strength"; }).length;
      counter.textContent = "Areas of strength: " + n + " of " + MAX_STRENGTHS + (n > MAX_STRENGTHS ? ". That's more than five; please pick your top five." : "");
      counter.classList.toggle("is-over", n > MAX_STRENGTHS);
    }
    updateCounter();
    block.addEventListener("change", updateCounter);
    questions.push({ block: block, title: title, changes: function () {
      return rows.filter(function (r) { return current(r) !== r.orig; }).map(function (r) {
        return "  " + r.name + ": " + word(r.orig) + " -> " + word(current(r));
      });
    }});
    return block;
  }

  function section(title, blocks) {
    var s = el("section", { className: "change-section" });
    s.appendChild(el("h2", { text: title }));
    blocks.forEach(function (b) { if (b) s.appendChild(b); });
    holder.appendChild(s);
  }

  /* ---------- build the page ---------- */
  var byKey = {};
  (fieldConfig.sections || []).forEach(function (sec) { sec.fields.forEach(function (f) { byKey[f.key] = f; }); });
  var contact = team.contact || {};

  var intro = el("p", { className: "change-team" });
  intro.appendChild(document.createTextNode("Listing: "));
  intro.appendChild(el("a", { href: config.siteUrl.replace(/\/$/, "") + team.url, text: team.title }));
  holder.appendChild(intro);

  section("Provider information", [
    addText("Q9. Team or service name", "title", team.title, false),
    addOne("Q" + byKey.institution.q + ". Institution", "institution", team.institution, optionsFor(byKey.institution), null),
    addOne("Q" + byKey.school.q + ". School, division, or central office", "school", team.school, optionsFor(byKey.school), null, null, true),
    addText("Department or unit", "unit", team.unit, false),
    addText("Q10. Website", "website", team.website, false),
    addText("Q3. Primary contact name (shown on the site)", "contact-name", contact.name, false),
    addText("Q4. Primary contact email (shown on the site)", "contact-email", contact.email, false)
  ]);

  (fieldConfig.sections || []).forEach(function (sec) {
    var blocks = [];
    sec.fields.forEach(function (f) {
      if (f.derived || f.key === "institution" || f.key === "school") return;
      var title = "Q" + f.q + ". " + f.label;
      var hint = null;
      if (f.key === "hands_on" && team.hands_on === "No") hint = "Your team answered No, so the questionnaire skipped Q23–26. If that's changed, choose Yes and fill them in.";
      if (f.type === "grid") blocks.push(addServices("Q" + f.q + ". Services", f));
      else if (f.type === "one") blocks.push(addOne(title, f.key, team[f.key], optionsFor(f), f, hint));
      else if (f.type === "many") blocks.push(addMany(title, f, hint));
      else blocks.push(addText(title, f.key, team[f.key], f.type === "text", hint));
      if (f.key === "examples") {
        blocks.push(addText("Q21. Paragraph shown beneath your summary", "body", team.body, true,
          "Optional. About 500 characters: your team's size, what sets you apart, or the projects you're best suited for."));
      }
    });
    if (blocks.length) section(sec.title, blocks);
  });

  form.hidden = false;

  /* ---------- tracking changes ---------- */
  function collect() {
    var out = [];
    questions.forEach(function (q) {
      var lines = q.changes();
      q.block.classList.toggle("is-changed", lines.length > 0);
      if (lines.length) out.push({ title: q.title, lines: lines });
    });
    return out;
  }
  function refresh() {
    var n = collect().length;
    countEl.textContent = n === 0 ? "No changes yet" : (n === 1 ? "1 question changed" : n + " questions changed");
  }
  form.addEventListener("change", refresh);
  form.addEventListener("input", refresh);
  form.addEventListener("submit", function (e) { e.preventDefault(); });

  document.getElementById("change-prepare").addEventListener("click", function () {
    var changes = collect();
    var extra = clean(document.getElementById("change-else").value);
    var name = clean(document.getElementById("change-name").value);
    var email = clean(document.getElementById("change-email").value);
    var listingUrl = config.siteUrl.replace(/\/$/, "") + team.url;
    var lines = ["Please update this RSSN listing.", "", "Team: " + team.title, "Listing: " + listingUrl, ""];
    if (changes.length) {
      changes.forEach(function (c) { lines.push(c.title); lines = lines.concat(c.lines); lines.push(""); });
    } else {
      lines.push("(No answers changed on the form.)", "");
    }
    if (extra) lines.push("Anything else:", indent(extra), "");
    if (name || email) lines.push("Requested by: " + [name, email].filter(Boolean).join(", "));
    var body = lines.join("\n").trim() + "\n";
    var subject = "RSSN listing change: " + team.title;

    summaryEl.value = body;
    var href = "mailto:" + encodeURIComponent(config.email || "").replace(/%40/g, "@") +
      "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
    var to = config.email ? " to " + config.email : " to RSSN";
    if (!changes.length && !extra) {
      helpEl.textContent = "You haven't changed anything yet. Change the answers above, or describe the change under Anything else.";
    } else if (href.length > MAILTO_LIMIT) {
      helpEl.textContent = "This request is too long to open in an email automatically. Copy the text below and paste it into an email" + to + ", with the subject \"" + subject + "\".";
    } else {
      helpEl.textContent = "Check the summary, then open it in your email program and send it" + to + ". If the button doesn't open your email, copy the text instead.";
    }
    mailtoEl.href = href;
    mailtoEl.hidden = href.length > MAILTO_LIMIT || (!changes.length && !extra);
    output.hidden = false;
    output.focus();
  });

  copyBtn.addEventListener("click", function () {
    function done(ok) { copyStatus.textContent = ok ? "Copied." : "Couldn't copy. Select the text and copy it."; }
    if (navigator.clipboard) {
      navigator.clipboard.writeText(summaryEl.value).then(function () { done(true); }, function () { done(false); });
    } else {
      summaryEl.select();
      try { done(document.execCommand("copy")); } catch (e) { done(false); }
    }
  });

  refresh();
})();
