#!/usr/bin/env python3
"""Bring existing listings across to the 2026 Service Provider Inventory questionnaire.

    pip install openpyxl pyyaml
    python scripts/port_listings.py --dry-run                 # report only, change nothing
    python scripts/port_listings.py                           # rewrite listings, write reports
    python scripts/port_listings.py --earlier-xlsx responses.xlsx
        # also checks the Draft 2 pilot answers in that export against the listings

For every listing in _providers:
  - each answer is renamed to the current wording (taxonomy.yml, "previous" and "previous_services");
  - an answer with no current equivalent is moved to the field's "_other" text, so nothing is lost;
  - answers that were approximated are marked "check" in the report.

For each listing that isn't a sample, a report is written to _imports/port-reports/<file>.md, listing
what changed, what needs confirming with the team, and what the team wasn't asked before (no
answer exists for it). The reports name no one but the team; approver and submitter names are never
written anywhere in the repository.

Review the git diff before committing. Listings are not re-dated: "updated" stays as it was,
because the team hasn't reviewed the new questions yet.
"""
import argparse
import re
import sys
from datetime import date

try:
    import openpyxl
except ImportError:
    openpyxl = None

from listing_format import PROVIDERS, ROOT, Config, read_listing, render, service_levels

REPORTS = ROOT / "_imports" / "port-reports"

# Earlier answers whose current value is the closest match rather than the same answer.
# The report asks the team to confirm these.
CHECK = {
    ("pre_award", "Depends on the project"),
    ("takeover", "Case-by-case"),
    ("production_support", "Case-by-case"),
    ("maintenance", "Case-by-case"),
    ("maintenance", "Yes, for systems developed by our team"),
    ("durations", "Varies significantly"),
}

# Questions the Draft 2 pilot didn't ask (their fields are blank in pilot listings).
DRAFT2_NOT_ASKED = {"team_type", "availability_details", "hands_on", "consult_scope", "services_other",
                    "free_limit", "cost", "accepting"}
# Questions Draft 3 (Microsoft Forms) didn't ask.
DRAFT3_NOT_ASKED = {"availability_details"}

# Draft 2 export columns (0-based, as in the pilot export) -> listing field.
DRAFT2_COLUMNS = {
    15: ("availability", "one"), 16: ("eligible", "many"), 18: ("languages", "many"),
    19: ("databases", "many"), 20: ("devops", "many"), 21: ("hosting", "many"),
    23: ("research_areas", "many"), 24: ("stages", "many"), 25: ("grant_estimates", "one"),
    26: ("pre_award", "one"), 27: ("data_types", "many"), 28: ("compliance", "many"),
    29: ("security_approach", "one"), 30: ("engagement_types", "many"), 31: ("project_sizes", "many"),
    32: ("durations", "many"), 33: ("takeover", "one"), 34: ("collaborate", "one"),
    35: ("funding", "many"), 36: ("charges", "many"), 37: ("minimum", "one"), 38: ("lead_time", "one"),
    39: ("production_support", "one"), 40: ("support_coverage", "many"), 41: ("open_source", "many"),
    42: ("handoff_docs", "one"), 43: ("maintenance", "one"), 45: ("examples", "text"), 46: ("notes", "text"),
}
DRAFT2_TITLE, DRAFT2_SCHOOL, DRAFT2_INSTITUTION = 12, 11, 10
DRAFT2_RETIRED = {22: "How frequently does your team work on research-related projects?"}


def norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def source_of(path):
    """Which questionnaire a listing came from, from the comment at the top of the file."""
    head = path.read_text(encoding="utf-8").split("\n", 2)[1:2]
    if head and "Pilot response to the Draft 2" in head[0]:
        return "draft2"
    return "draft3"


class Log:
    """What happened to each answer, for the report."""

    def __init__(self):
        self.changes = []     # (kind, question, was, now, note)
        self.check = []       # (question, was, now, why)
        self.moved = []       # (question, was)

    def renamed(self, q, was, now, check=False, key=None):
        if check:
            self.check.append((q, was, now, "closest current answer; confirm with the team"))
        self.changes.append(("check" if check else "renamed", q, was, now, ""))

    def service(self, was, now):
        self.changes.append(("renamed", "Service", was, now, "service name"))


def qlabel(cfg, key):
    f = cfg.by_key.get(key)
    if not f:
        return key
    return f"Q{f['q']}. {f['label']}"


def fix_one(cfg, key, value, prev, log):
    """Returns (value now, text moved to the write-in or None)."""
    opts = cfg.options(key)
    v = "" if value in (None, "") else str(value).strip()
    if v == "" or v in opts:
        return v, None
    if v in prev:
        now = prev[v]
        log.renamed(qlabel(cfg, key), v, now, check=(key, v) in CHECK)
        return now, None
    log.moved.append((qlabel(cfg, key), v))
    return "", v


def fix_many(cfg, key, values, prev, log):
    opts = cfg.options(key)
    out, moved = [], []
    for v in values or []:
        v = str(v).strip()
        if not v:
            continue
        if v in opts:
            if v not in out:
                out.append(v)
        elif v in prev:
            now = prev[v]
            log.renamed(qlabel(cfg, key), v, now, check=(key, v) in CHECK)
            if now not in out:
                out.append(now)
        else:
            moved.append(v)
            log.moved.append((qlabel(cfg, key), v))
    out.sort(key=lambda x: opts.index(x) if x in opts else len(opts))
    return out, moved


def migrate(data, body, cfg, prev_all, prev_services):
    """Returns (new data, log, the other-text notes)."""
    log = Log()
    d = dict(data)
    prev = prev_all
    # Rename the services first, so a renamed service keeps its level (and isn't read as "not offered").
    renamed_in = {}
    for name in (data.get("services") or {}) if isinstance(data.get("services"), dict) else []:
        if prev_services.get(name, name) != name:
            renamed_in[name] = prev_services[name]
            log.service(name, prev_services[name])
    src = dict(data)
    if isinstance(data.get("services"), dict):
        src["services"] = {prev_services.get(k, k): v for k, v in data["services"].items()}
    if isinstance(data.get("strengths"), list):
        src["strengths"] = [prev_services.get(x, x) for x in data["strengths"]]
    d["services"] = service_levels(src, cfg)
    d.pop("strengths", None)

    for f in cfg.stored_fields():
        k = f["key"]
        if k in ("institution", "school", "services") or f["type"] in ("grid", "text", "short"):
            continue
        p = prev.get(k, {})
        if f["type"] == "one":
            now, moved = fix_one(cfg, k, data.get(k), p, log)
            d[k] = now
            if moved:
                d[k + "_other"] = "; ".join(x for x in [data.get(k + "_other"), moved] if x)
        elif f["type"] == "many":
            vals = data.get(k) if isinstance(data.get(k), list) else ([data.get(k)] if data.get(k) else [])
            now, moved = fix_many(cfg, k, vals, p, log)
            d[k] = now
            if moved:
                d[k + "_other"] = "; ".join(x for x in [data.get(k + "_other"), "; ".join(moved)] if x)
    return d, log


def earlier_checks(xlsx_path, cfg, prev_all, prev_services):
    """Compares the Draft 2 pilot answers in the export with each listing.
    Returns {normalized team name: [messages]} and the retired-question messages."""
    if not openpyxl:
        sys.exit("This check needs openpyxl: pip install openpyxl")
    ws = openpyxl.load_workbook(xlsx_path).active
    rows = list(ws.iter_rows(values_only=True))[1:]
    out = {}
    for r in rows:
        team = norm(r[DRAFT2_TITLE])
        if not team:
            continue
        msgs = []
        for col, text in DRAFT2_RETIRED.items():
            if r[col]:
                msgs.append(("retired", f"Earlier answer to a question that is no longer asked: {text} "
                                        f"→ “{r[col]}”"))
        out[team] = (r, msgs)
    return out


def check_against_listing(r, data, cfg, prev_all):
    """Earlier answers from the Draft 2 export that didn't carry over to the listing."""
    msgs = []
    for col, (key, kind) in DRAFT2_COLUMNS.items():
        raw = r[col]
        if raw in (None, ""):
            continue
        if kind == "text":
            if not str(data.get(key) or "").strip():
                msgs.append(("text", f"{qlabel(cfg, key)}: the earlier answer is not in the listing "
                                     f"(“{str(raw)[:120]}…”)"))
            continue
        vals = [v.strip() for v in str(raw).split(";") if v.strip()] if kind == "many" else [str(raw).strip()]
        flat = cfg.taxonomy.get("aliases") or {}
        vals = [x for v in vals for x in (flat.get(v) or [v])]
        now_vals = data.get(key) if isinstance(data.get(key), list) else ([data.get(key)] if data.get(key) else [])
        for v in vals:
            if v in cfg.options(key):
                target = v
            elif v in prev_all.get(key, {}):
                target = prev_all[key][v]
            else:
                if v not in (now_vals or []) and not str(data.get(key + "_other") or "").strip():
                    msgs.append(("lost", f"{qlabel(cfg, key)}: the earlier answer “{v}” has no current choice "
                                         f"and isn't recorded in the listing. Ask whether to add it as write-in text"))
                continue
            if target not in now_vals:
                msgs.append(("differs", f"{qlabel(cfg, key)}: the earlier answer “{v}” (now "
                                        f"“{target}”) isn't in the listing. Confirm whether it still applies"))
    return msgs


def not_asked_and_blank(cfg, data, source):
    asked_out = DRAFT2_NOT_ASKED if source == "draft2" else DRAFT3_NOT_ASKED
    missing, blank = [], []
    for f in cfg.stored_fields():
        k = f["key"]
        if k in ("institution", "school", "services"):
            continue
        if k in asked_out:
            missing.append(f)
            continue
        if source == "draft2" and k == "hands_on":
            continue
        v = data.get(k)
        empty = v in (None, "", []) or (isinstance(v, str) and not v.strip())
        if empty:
            blank.append(f)
    # Answers that the listing's other answers make required
    gaps = []
    if data.get("availability") in ("Certain schools/divisions", "It's complicated") and not str(data.get("availability_details") or "").strip():
        gaps.append("Availability details (Q20): you chose “" + data.get("availability") +
                    "”, so the clarifying text is needed.")
    if str(data.get("cost")) == "Free initial help, then charged" and not str(data.get("free_limit") or "").strip():
        gaps.append("Where no-cost help ends (Q43): cost is “Free initial help, then charged”, so this is needed.")
    strong = [n for n, v in service_levels(data, cfg).items() if v == "strength"]
    if len(strong) > 5:
        gaps.append("Areas of strength: " + str(len(strong)) + " are marked (the limit is five). Ask which five "
                    "to keep: " + "; ".join(strong) + ".")
    if "None of the above" in (data.get("compliance") or []) and len(data.get("compliance") or []) > 1:
        gaps.append("Requirements and reviews (Q35): \u201cNone of the above\u201d is selected with other answers. "
                    "Ask which one is right.")
    return missing, blank, gaps


def render_report(title, fname, source, updated, log, earlier, retired, missing, blank, gaps):
    src = {"draft2": "Draft 2 pilot", "draft3": "Draft 3 (Microsoft Forms)"}[source]
    L = [f"# Port report: {title}", "",
         f"Listing file: `_providers/{fname}`  ",
         f"Earlier questionnaire: {src}  ",
         f"Listing last reviewed: {updated or 'not recorded'}  ",
         f"Report written: {date.today().isoformat()}", "",
         "## Summary", ""]
    renamed = [c for c in log.changes if c[0] == "renamed"]
    check = log.check
    moved = log.moved
    L += [f"- {len(renamed)} answer(s) renamed to the current wording (same meaning).",
          f"- {len(check)} answer(s) matched to the closest current choice; confirm with the team.",
          f"- {len(moved)} answer(s) with no current choice, kept as write-in text.",
          f"- {len(missing)} question(s) the earlier questionnaire didn't ask, so there is no answer on file.",
          f"- {len(blank)} question(s) that were asked earlier but are blank in the listing.", ""]

    L += ["## Please confirm with the team", ""]
    items = []
    for q, was, now, why in check:
        items.append(f"**{q}**: the earlier answer \u201c{was}\u201d is now \u201c{now}\u201d, the closest "
                     "current choice. Please confirm.")
    for q, was in moved:
        items.append(f"**{q}**: the earlier answer \u201c{was}\u201d has no current choice, so it is kept as "
                     "write-in text. Ask which current choice fits.")
    for kind, msg in earlier:
        if kind in ("lost", "differs", "text"):
            items.append(msg + ".")
    for g in gaps:
        items.append(g)
    L += [f"{i}. {x}" for i, x in enumerate(items, 1)] if items else ["Nothing to confirm."]
    L += [""]

    L += ["## Questions the earlier questionnaire didn't ask", ""]
    L += [f"- {qlabel(cfg_global, f['key'])}" for f in missing] or ["None."]
    L += [""]

    L += ["## Asked before, but blank in the listing", ""]
    L += [f"- {qlabel(cfg_global, f['key'])}" for f in blank] or ["None."]
    L += [""]

    retired_msgs = [m for k, m in retired]
    if retired_msgs:
        L += ["## Earlier answers to questions no longer asked", ""]
        L += [f"- {m}" for m in retired_msgs] + [""]

    L += ["## Every change made to this listing", "",
          "| Kind | Question | Earlier | Now |", "|---|---|---|---|"]
    for kind, q, was, now, note in log.changes:
        L.append(f"| {kind} | {q} | {was} | {now} |")
    L += ["", "_Generated by scripts/port_listings.py. Re-run the script to refresh it._", ""]
    return "\n".join(L)


cfg_global = None


def main():
    global cfg_global
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report only; change no listing")
    ap.add_argument("--earlier-xlsx", help="Draft 2 pilot export, to check its answers against the listings")
    args = ap.parse_args()

    cfg = Config()
    cfg_global = cfg
    tax = cfg.taxonomy
    prev_all = tax.get("previous") or {}
    prev_services = tax.get("previous_services") or {}
    earlier = earlier_checks(args.earlier_xlsx, cfg, prev_all, prev_services) if args.earlier_xlsx else {}

    if not args.dry_run:
        REPORTS.mkdir(parents=True, exist_ok=True)
    index = []
    for p in sorted(PROVIDERS.glob("*.md")):
        data, body, dups = read_listing(p)
        if dups:
            print(f"skip   {p.name}: answered more than once ({', '.join(k for k, _ in dups)}). Fix it first.")
            continue
        source = source_of(p)
        new, log = migrate(data, body, cfg, prev_all, prev_services)

        sample = bool(data.get("sample"))
        if not args.dry_run:
            p.write_text(render(new, body, cfg), encoding="utf-8", newline="\n")
        if sample:
            print(f"sample {p.name}: {len(log.changes)} renamed, {len(log.moved)} moved to write-in")
            continue

        earlier_msgs, retired = [], []
        team = norm(data.get("title"))
        if team in earlier:
            r, retired = earlier[team]
            earlier_msgs = check_against_listing(r, new, cfg, prev_all)
        missing, blank, gaps = not_asked_and_blank(cfg, new, source)
        report = render_report(data.get("title") or p.stem, p.name, source, data.get("updated"), log,
                               earlier_msgs, retired, missing, blank, gaps)
        if not args.dry_run:
            (REPORTS / (p.stem + ".md")).write_text(report, encoding="utf-8", newline="\n")
        index.append((data.get("title") or p.stem, p.stem, source, len(log.changes), len(log.check),
                      len(log.moved), len(missing), len(blank), len(earlier_msgs) + len(gaps)))
        print(f"report {p.name}: {len(log.changes)} renamed, {len(log.check)} to check, "
              f"{len(log.moved)} moved, {len(missing)} not asked, {len(blank)} blank")

    if index and not args.dry_run:
        L = ["# Provider listing port reports", "",
             "Written by scripts/port_listings.py when the listings were brought to the 2026 Service Provider "
             "Inventory questionnaire. One report per listing that isn't a sample. Use each report's "
             "“Please confirm” and “not asked” sections to follow up with the team.", "",
             "| Team | Earlier questionnaire | Renamed | To confirm | Kept as write-in | Not asked | Blank | Other items |",
             "|---|---|---|---|---|---|---|---|"]
        for title, stem, source, ren, chk, mv, miss, blank, other in index:
            src = "Draft 2 pilot" if source == "draft2" else "Draft 3 (Forms)"
            L.append(f"| [{title}]({stem}.md) | {src} | {ren} | {chk} | {mv} | {miss} | {blank} | {other} |")
        (REPORTS / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("\n(dry run: nothing was written)" if args.dry_run else "\nDone.")


if __name__ == "__main__":
    main()
