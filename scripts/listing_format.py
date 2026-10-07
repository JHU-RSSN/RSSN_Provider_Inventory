"""Read and write provider listing files (_providers/*.md) in the "every option listed" format.

Shared by import_responses.py, refresh_listings.py, check_listings.py, and make_template.py.

Every answer choice from _data/taxonomy.yml is written into the file. Choices a team
didn't pick are commented out with "# ", so editing a listing on GitHub means adding or
removing "# " rather than typing an answer from memory:

    # Q14. Who can engage this team. CHOOSE ALL THAT APPLY.
    eligible:
      - "JHHS faculty"
      # - "JHHS staff"

    # Q12. Available to. CHOOSE ONE.
    availability: "Hopkins-wide"
    # availability: "JHU only"

The four service grids (Q15-18) are one map, with one word per service, the way the
form's grid works:

    services:
      "AI-Assisted Coding":              offered
      "Python or R Package Development": strength
      "Data Pipeline Automation":        not offered

Jekyll ignores the commented lines, so the site only ever sees the chosen answers.
"""
import datetime as dt
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROVIDERS = ROOT / "_providers"

# Words a listing uses for each service, and the Forms grid answers they come from.
LEVELS = ["not offered", "offered", "strength"]
LEVEL_FROM_FORM = {
    "not offered": "not offered",
    "offered": "offered",
    "offered & area of strength": "strength",
    "offered and area of strength": "strength",
    "area of strength": "strength",  # Draft 2 / early Draft 3 wording
    "strength": "strength",
}
MAX_STRENGTHS = 5

# Front-matter keys handled outside fields.yml, in the order they're written.
HEADER_KEYS = ["sample", "form_response_id", "title", "institution", "school", "unit", "website",
               "contact", "updated"]

# Questionnaire answers that respondents didn't agree to publish: who filled out the form
# (Q1-2) and the approving team lead (Q5-6). The repository is public, so these are never
# written to listing files, even though older listings had them.
PRIVATE_KEYS = ["submitted_by", "approved_by"]


# ---------- configuration ----------

class Config:
    def __init__(self, root=ROOT):
        self.taxonomy = yaml.safe_load((root / "_data/taxonomy.yml").read_text(encoding="utf-8"))
        self.sections = yaml.safe_load((root / "_data/fields.yml").read_text(encoding="utf-8"))["sections"]
        self.fields = [f for s in self.sections for f in s["fields"]]
        self.by_key = {f["key"]: f for f in self.fields}
        self.services = self.taxonomy["services"]
        self.service_names = [s["name"] for s in self.services]

    def options(self, key):
        """Allowed values (labels) for a one/many field."""
        f = self.by_key.get(key)
        if not f or not f.get("options"):
            return []
        if f["options"] == "schools":
            return [s["name"] for s in self.taxonomy["schools"]]
        return [label_of(o) for o in self.taxonomy.get(f["options"]) or []]

    def stored_fields(self):
        """fields.yml entries that are stored in listing files (not derived ones)."""
        return [f for f in self.fields if not f.get("derived")]


def label_of(opt):
    if isinstance(opt, dict):
        return opt.get("label") or opt.get("name")
    return str(opt)


# ---------- reading ----------

class _DupLoader(yaml.SafeLoader):
    """SafeLoader that records duplicate keys instead of silently keeping the last one.
    A duplicate usually means two lines of a "choose one" question were uncommented."""


def _construct_mapping(loader, node, deep=False):
    seen = {}
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            loader.duplicates.append((key, key_node.start_mark.line + 1))
        seen[key] = True
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


_DupLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)

FRONT = re.compile(r"\A---\s*\n(.*?\n)---\s*\n?(.*)\Z", re.S)


def split_front_matter(text):
    m = FRONT.match(text.replace("\r\n", "\n"))
    if not m:
        raise ValueError("no front matter (the file must start with a line of three dashes)")
    return m.group(1), m.group(2)


def read_listing(path):
    """Return (data, body, duplicates). duplicates is a list of (key, line number in the file)."""
    front, body = split_front_matter(Path(path).read_text(encoding="utf-8"))
    loader = _DupLoader(front)
    loader.duplicates = []
    try:
        data = loader.get_single_data() or {}
    finally:
        loader.dispose()
    # Line numbers are within the front matter; the file has one "---" line before it.
    dups = [(k, line + 1) for k, line in loader.duplicates]
    return data, body.strip("\n"), dups


def service_levels(data, cfg):
    """The listing's services as {service name: level}, reading either the current map
    format or the older services/strengths lists. Unknown words are kept as written."""
    raw = data.get("services")
    out = {}
    if isinstance(raw, dict):
        for name, level in raw.items():
            word = re.sub(r"\s+", " ", str(level if level is not None else "")).strip().lower()
            out[str(name)] = LEVEL_FROM_FORM.get(word, word or "not offered")
    else:
        offered = set(as_list(raw))
        strong = set(as_list(data.get("strengths")))
        for name in cfg.service_names:
            out[name] = "strength" if name in strong else ("offered" if name in offered else "not offered")
        for name in sorted((offered | strong) - set(cfg.service_names)):
            out[name] = "strength" if name in strong else "offered"
    for name in cfg.service_names:
        out.setdefault(name, "not offered")
    return out


def as_list(v):
    if v is None or v == "":
        return []
    return [x for x in v if x not in (None, "")] if isinstance(v, list) else [v]


# ---------- writing ----------

def q(s):
    """A double-quoted YAML string (JSON strings are valid YAML)."""
    return json.dumps("" if s is None else str(s), ensure_ascii=False)


EDIT_HELP = [
    "# HOW TO EDIT THIS LISTING",
    "#   Every answer choice from the questionnaire is listed below. A line that starts with",
    "#   \"# \" is NOT selected; a line without it IS selected.",
    "#   - CHOOSE ALL THAT APPLY: delete the \"# \" in front of a line to select it; type \"# \"",
    "#     in front of it to unselect it. Leave the spaces before the \"# \" alone.",
    "#   - CHOOSE ONE: exactly one line for the question should be missing its \"# \".",
    "#   - SERVICES: after each service, write one of: not offered, offered, strength",
    "#     (strength = offered and an area of strength; no more than five).",
    "#   - Keep the quotation marks and spelling of every answer exactly as they are.",
    "#     Write-in (\"Other\") answers go in the matching _other line, inside the quotes.",
    "#   - Update the \"updated:\" date to today when you change anything.",
    "#   Allowed values: _data/taxonomy.yml. Reviewers can run scripts/check_listings.py.",
]


def _text_lines(key, value):
    value = ("" if value is None else str(value)).replace("\r\n", "\n").strip()
    if not value:
        return [f"{key}: \"\""]
    return [f"{key}: |"] + [("  " + l) if l.strip() else "" for l in value.split("\n")]


def _one_lines(key, value, options, indent=""):
    value = "" if value is None else str(value)
    lines = []
    for opt in options:
        lines.append(f"{indent}{'' if opt == value else '# '}{key}: {q(opt)}")
    if value and value not in options:
        lines.append(f"{indent}{key}: {q(value)}   # not one of the listed choices")
    return lines


def _many_lines(key, values, options):
    values = as_list(values)
    lines = [f"{key}:"]
    for opt in options:
        lines.append(f"  {'' if opt in values else '# '}- {q(opt)}")
    for v in values:
        if v not in options:
            lines.append(f"  - {q(v)}   # not one of the listed choices")
    return lines


def _service_lines(levels, cfg):
    width = max(len(q(n)) for n in levels) + 1
    lines = ["services:"]
    groups = cfg.taxonomy.get("service_groups") or []
    for g in groups:
        lines.append(f"  # {g}")
        for s in cfg.services:
            if s["group"] == g:
                lines.append(f"  {(q(s['name']) + ':').ljust(width)} {levels.get(s['name'], 'not offered')}")
    extra = [n for n in levels if n not in cfg.service_names]
    if extra:
        lines.append("  # Not in the questionnaire's list (check _data/taxonomy.yml)")
        for n in extra:
            lines.append(f"  {(q(n) + ':').ljust(width)} {levels[n]}")
    return lines


def _person(key, person):
    person = person or {}
    return [f"{key}:", f"  name: {q(person.get('name', ''))}", f"  email: {q(person.get('email', ''))}"]


def render(rec, body, cfg, intro=None):
    """Front matter + body text for one listing. `rec` holds front-matter values by key;
    services may be a {name: level} map or the older services/strengths lists."""
    L = ["---"]
    L.extend(intro or ["# RSSN provider listing, from the RSSN Research IT Provider Questionnaire (Draft 3)."])
    L.append("#")
    L.extend(EDIT_HELP)
    if rec.get("sample"):
        L.append("")
        L.append("sample: true")
    if rec.get("form_response_id"):
        L.append("")
        L.append("# Links this listing to its Microsoft Forms response. Please don't change it.")
        L.append(f"form_response_id: {q(rec['form_response_id'])}")
    L += ["", "# Q9. Team or service name, as researchers should see it", f"title: {q(rec.get('title'))}"]

    f = cfg.by_key["institution"]
    L += ["", f"# Q{f['q']}. {f['label']}. CHOOSE ONE."]
    L += _one_lines("institution", rec.get("institution"), cfg.options("institution"))

    f = cfg.by_key["school"]
    L += ["", f"# Q{f['q']}. School, division, or central office. CHOOSE ONE, or if yours isn't listed,",
          "# write it on its own line the same way. Listed ones get a colored card accent."]
    L += _one_lines("school", rec.get("school"), cfg.options("school"))
    L += ["# Department or unit within that school (free text)", f"unit: {q(rec.get('unit'))}"]
    L += ["", "# Q10. Website or service information URL (optional)", f"website: {q(rec.get('website'))}"]
    L += ["", "# Q3-4. Primary contact, shown on the public site"] + _person("contact", rec.get("contact"))
    updated = rec.get("updated")
    if isinstance(updated, (dt.date, dt.datetime)):
        updated = updated.isoformat()[:10]
    L += ["", "# Date this listing was last reviewed (YYYY-MM-DD)", f"updated: {updated or ''}".rstrip()]

    written = set(HEADER_KEYS) | set(PRIVATE_KEYS)
    for sec in cfg.sections:
        fields = [x for x in sec["fields"] if x["key"] not in ("institution", "school") and not x.get("derived")]
        if not fields:
            continue
        L += ["", f"# ===== {sec['title']} ====="]
        for f in fields:
            k, t = f["key"], f["type"]
            written.add(k)
            L.append("")
            if t == "grid":
                L.append(f"# Q{f['q']}. Services. After each service write: not offered, offered, or strength.")
                L.append(f"# strength = offered AND an area of strength. No more than {MAX_STRENGTHS} strengths in all.")
                L += _service_lines(service_levels(rec, cfg), cfg)
            elif t == "one":
                L.append(f"# Q{f['q']}. {f['label']}. CHOOSE ONE.")
                L += _one_lines(k, rec.get(k), cfg.options(k))
            elif t == "many":
                note = ""
                if k in ("languages", "databases", "devops", "hosting"):
                    note = " (leave all unselected if Q22 is \"No\")"
                L.append(f"# Q{f['q']}. {f['label']}. CHOOSE ALL THAT APPLY{note}.")
                L += _many_lines(k, rec.get(k), cfg.options(k))
            elif t == "short":
                L.append(f"# Q{f['q']}. {f['label']} (one line of free text)")
                L.append(f"{k}: {q(rec.get(k))}")
            else:  # text
                L.append(f"# Q{f['q']}. {f['label']} (free text; Markdown is fine)")
                L += _text_lines(k, rec.get(k))
            if t not in ("one", "many"):
                continue
            other = k + "_other"
            written.add(other)
            if f.get("other") or rec.get(other):
                L.append(f"# Q{f['q']}. \"Other\" write-in answer, if any")
                L.append(f"{other}: {q(rec.get(other))}")
    written.add("strengths")

    extra = [k for k in rec if k not in written and rec.get(k) not in (None, "", [])]
    if extra:
        L += ["", "# ===== Other fields (not part of the current questionnaire) ====="]
        for k in extra:
            v = rec[k]
            if isinstance(v, list):
                L += [f"{k}:"] + [f"  - {q(x)}" for x in v]
            elif isinstance(v, dict):
                L.append(f"{k}: {json.dumps(v, ensure_ascii=False, default=str)}")
            elif isinstance(v, str) and "\n" in v:
                L += _text_lines(k, v)
            else:
                L.append(f"{k}: {q(v) if isinstance(v, str) else json.dumps(v, default=str)}")
    L.append("---")
    body = (body or "").strip("\n")
    return "\n".join(L) + "\n" + (body + "\n" if body else "")


# ---------- comparing (used by the import script's safety checks) ----------

def field_keys(cfg):
    """Every value the import script writes, in a stable order, for change detection."""
    keys = ["title", "institution", "school", "unit", "website", "contact"]
    for f in cfg.stored_fields():
        if f["key"] in ("institution", "school"):
            continue
        keys.append(f["key"])
        if f["type"] in ("one", "many"):
            keys.append(f["key"] + "_other")
    return keys + ["body"]


def comparable(key, rec, cfg, body=None):
    """A value normalized so that formatting differences don't count as edits."""
    if key == "body":
        v = body if body is not None else rec.get("body", "")
        return re.sub(r"\s+", " ", str(v or "")).strip()
    if key == "services":
        return {n: l for n, l in sorted(service_levels(rec, cfg).items())}
    v = rec.get(key)
    if key == "contact":
        v = v or {}
        return {"name": str(v.get("name") or "").strip(), "email": str(v.get("email") or "").strip()}
    if isinstance(v, dict):
        return {k: re.sub(r"\s+", " ", str(x or "")).strip() for k, x in sorted(v.items())}
    if isinstance(v, list) or (cfg.by_key.get(key, {}).get("type") == "many"):
        return sorted(str(x).strip() for x in as_list(v))
    return re.sub(r"\s+", " ", str(v if v is not None else "")).strip()


def fingerprint(value):
    import hashlib
    return hashlib.sha1(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]


def show(value, limit=90):
    """Short human-readable form of a comparable value, for reports."""
    if isinstance(value, dict):
        if value and all(v in LEVELS for v in value.values()):
            on = [f"{k} ({v})" for k, v in value.items() if v != "not offered"]
            s = "; ".join(on) or "(none offered)"
        else:
            s = ", ".join(f"{k}: {v}" for k, v in value.items())
    elif isinstance(value, list):
        s = "; ".join(value) or "(none)"
    else:
        s = value or "(blank)"
    return s if len(s) <= limit else s[: limit - 1] + "…"
