#!/usr/bin/env python3
"""Turn questionnaire responses (the Microsoft Forms Excel export) into provider listings.

Written for Draft 3 of the RSSN Research IT Provider Questionnaire, as built in Forms.

    pip install openpyxl pyyaml
    python scripts/import_responses.py responses.xlsx --dry-run   # report only, change nothing
    python scripts/import_responses.py responses.xlsx             # write new and updated listings

Each response becomes _providers/<team-name>.md, in the format described in
scripts/listing_format.py (every answer choice listed; unselected ones commented out).
Answers are matched against the allowed values in _data/taxonomy.yml; anything that doesn't
match (a write-in "Other" answer, say) goes in that field's "<key>_other" text.

SAFETY CHECKS FOR RESPONSES THAT ALREADY HAVE A LISTING
Teams are asked to edit their listing on GitHub, but a team could also edit and resubmit
its form. So the script never simply overwrites a listing:

  1. Each listing records its Forms response ID (form_response_id), and the script finds
     the listing by that ID, so renaming the team in the form updates the same file.
  2. A response is only looked at again if it changed since it was last imported.
     Unchanged responses are skipped.
  3. _imports/import_log.json records a fingerprint of every answer as last imported.
     For each answer, the script compares the form, the listing, and that record:
       - changed only in the form        -> the form's answer is used
       - changed only on GitHub          -> the listing's answer is kept
       - changed in both, differently    -> CONFLICT: the listing's answer is kept and the
                                            conflict is reported every run until settled
     A listing that was never imported (the pilot listings, for example) has no record,
     so every difference from the form is reported as a conflict.

  Settle the conflicts for one listing with
     --only <file-name-or-response-id> --form-wins      use the form's answers
     --only <file-name-or-response-id> --listing-wins   keep the listing's answers
  or edit the listing by hand to the answer you want and re-run.

PRIVACY: only answers respondents agreed to publish go into listings. The names and emails
of the person who filled out the form (Q1-2) and the approving team lead (Q5-6) are never
written to the repository; the approver is printed in the report for RSSN's follow-up.

Commit _imports/import_log.json along with the listings, and review the git diff before
committing. Check the school and unit especially, since the form collects them as one answer.

The four service grids (Q15-18) are found by their answers: any column whose answers are
all "Not offered", "Offered", or "Offered & Area of strength" is a grid row, and the service
it belongs to is the one whose name appears in the column heading.
"""
import argparse
import datetime as dt
import json
import re
import sys

try:
    import openpyxl
    import yaml  # noqa: F401  (listing_format needs it)
except ImportError:
    sys.exit("This script needs openpyxl and pyyaml: pip install openpyxl pyyaml")

from listing_format import (LEVEL_FROM_FORM, MAX_STRENGTHS, PRIVATE_KEYS, PROVIDERS, ROOT, Config, comparable,
                            field_keys, fingerprint, label_of, read_listing, render, service_levels, show)

LOG_PATH = ROOT / "_imports" / "import_log.json"

# Columns that aren't part of _data/fields.yml, matched by the start of the heading.
INFO_COLUMNS = {
    "respondent_name": "Name of the person completing",
    "respondent_email": "Email address of the person completing",
    "contact_name": "Primary contact name",
    "contact_email": "Primary contact email",
    "approver_name": "Name of the team lead or director",
    "approver_email": "Email address of the team lead or director",
    "title": "Team or service name",
    "paragraph": "Is there anything else you would like to highlight",
    "website": "Website or service information URL",
}
# Forms' own columns, matched exactly.
FORMS_COLUMNS = {"response_id": "id", "completed": "completion time", "modified": "last modified time"}


def norm(s):
    """Lowercase, straighten quotes and dashes, collapse whitespace."""
    s = str(s)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip().lower()


def split_answers(cell):
    """Split a multi-select cell on ';', ignoring semicolons inside parentheses."""
    if cell is None:
        return []
    parts, buf, depth = [], "", 0
    for ch in str(cell):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == ";" and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    parts.append(buf)
    return [re.sub(r"\s+", " ", p).strip() for p in parts if p.strip()]


class Matcher:
    """Maps a questionnaire answer to its canonical listing value."""

    def __init__(self, options, aliases):
        self.lookup = {}
        for opt in options or []:
            label = label_of(opt)
            keys = [label]
            if isinstance(opt, dict) and opt.get("answer"):
                keys.append(opt["answer"])
            for k in keys:
                self.lookup[norm(k)] = [label]
        for raw, vals in (aliases or {}).items():
            vals = [v for v in vals if norm(v) in self.lookup]
            if vals:
                self.lookup[norm(raw)] = vals

    def match(self, answer):
        a = norm(answer)
        if a in self.lookup:
            return self.lookup[a]
        # Service answers carry their description in parentheses: "Databases (Data migration; ...)"
        head = norm(re.split(r"\s*\(", str(answer), maxsplit=1)[0])
        if head in self.lookup:
            return self.lookup[head]
        # "Yes - other criteria (please specify)" style prefixes
        for k, v in self.lookup.items():
            if len(k) > 12 and a.startswith(k):
                return v
        return None


def find_columns(headers, fields):
    cols = {}
    heads = [norm(h or "") for h in headers]
    for key, name in FORMS_COLUMNS.items():
        if name in heads:
            cols[key] = heads.index(name)
    wanted = dict(INFO_COLUMNS)
    for f in fields:
        if f.get("question"):
            wanted[f["key"]] = f["question"]
    for key, qtext in wanted.items():
        qn = norm(qtext)
        hits = [i for i, h in enumerate(heads) if h.startswith(qn) and i not in cols.values()]
        if key == "institution":  # be exact: "Institution" could start other headings
            hits = [i for i, h in enumerate(heads) if h == "institution"] or hits
        if hits:
            cols[key] = hits[0]
    return cols


def find_grid_columns(headers, rows, services, taken):
    """Map each service name to its grid column (see the module docstring).
    `taken` holds columns already matched to other questions."""
    out = {}
    for i, h in enumerate(headers):
        if i in taken:
            continue
        vals = {norm(r[i]) for r in rows if i < len(r) and r[i] not in (None, "")}
        if not vals <= set(LEVEL_FROM_FORM):  # an empty column (nobody answered) still counts
            continue
        hn = norm(h or "")
        for s in services:
            if norm(s["name"]) in hn and s["name"] not in out:
                out[s["name"]] = i
                break
    return out


def find_school(text, schools):
    for s in schools:
        for name in [s["name"]] + list(s.get("aliases") or []):
            if re.search(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", text, re.I):
                return s["name"], name
    return None, None


def clean_unit(raw, alias_hit, school_name):
    """Drop the school name from a combined 'School, Department, Center' answer."""
    parts = [p.strip() for p in re.split(r"\s*,\s*", raw) if p.strip()]
    drop = {norm(school_name)} | ({norm(alias_hit)} if alias_hit else set())
    return ", ".join(p for p in parts if norm(p) not in drop)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "provider"


def paragraphs(text):
    """Keep the respondent's line breaks as Markdown paragraphs; fix '1.Item' lists."""
    text = str(text).replace("\r\n", "\n").strip()
    text = re.sub(r"^(\d+)\.(?=\S)", r"\1. ", text, flags=re.M)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines and all(re.match(r"\d+\.\s", l) for l in lines):
        return "\n".join(lines)
    return "\n\n".join(lines)


def as_time(v):
    if isinstance(v, dt.datetime):
        return v
    if v in (None, ""):
        return None
    for fmt in ("%m/%d/%y %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%m/%d/%y %H:%M", "%m/%d/%Y %H:%M"):
        try:
            return dt.datetime.strptime(str(v).strip(), fmt)
        except ValueError:
            pass
    return None


# ---------- one response -> one record ----------

def parse_row(row, cols, grid, cfg):
    """Returns (rec, body, present). `present` holds the comparison keys the spreadsheet
    has columns for, so a missing column never blanks out an answer in a listing."""
    tax = cfg.taxonomy
    aliases = tax.get("aliases") or {}
    cell = lambda k: (row[cols[k]] if k in cols and cols[k] < len(row) else None)
    text = lambda k: re.sub(r"\s+", " ", str(cell(k) or "")).strip()
    rec = {"title": text("title")}
    present = {"title"} | ({"body"} if "paragraph" in cols else set())

    rid = cell("response_id")
    if rid not in (None, ""):
        rec["form_response_id"] = str(int(rid)) if isinstance(rid, (int, float)) and float(rid).is_integer() else str(rid).strip()
    when = as_time(cell("modified")) or as_time(cell("completed"))
    rec["_response_time"] = when
    rec["updated"] = (when.date() if when else dt.date.today()).isoformat()

    # Only the primary contact (Q3-4) is published. Who filled out the form (Q1-2) and the
    # approver (Q5-6) stay out of the listing; the approver is printed for RSSN's follow-up.
    rec["contact"] = {"name": text("contact_name"), "email": text("contact_email")}
    if "contact_name" in cols:
        present.add("contact")
    approver = " ".join(x for x in (text("approver_name"), text("approver_email") and f"<{text('approver_email')}>") if x)
    submitter = " ".join(x for x in (text("respondent_name"), text("respondent_email") and f"<{text('respondent_email')}>") if x)
    rec["_approver"] = approver or ("(none given; submitted by " + submitter + ")" if submitter else "(none given)")

    site = text("website")
    if site and not re.match(r"https?://", site):
        site = "https://" + site
    rec["website"] = site
    if "website" in cols:
        present.add("website")

    # Institution and school: the form asks for school, department, and unit in one answer.
    inst_raw, school_raw = text("institution"), text("school")
    inst = Matcher(tax.get("institutions"), aliases).match(inst_raw)
    school, alias_hit = find_school(f"{inst_raw}, {school_raw}", tax.get("schools") or [])
    rec["institution"] = inst[0] if inst else ("JHU" if school else inst_raw)
    if school:
        rec["school"], rec["unit"] = school, clean_unit(school_raw, alias_hit, school)
    else:
        rec["school"], rec["unit"] = school_raw, ""
    if "institution" in cols:
        present.add("institution")
    if "school" in cols:
        present |= {"school", "unit"}

    # Service grids (Q15-18): one level per service.
    levels = {}
    for s in cfg.services:
        i = grid.get(s["name"])
        if i is None:
            continue
        raw = norm(row[i]) if i < len(row) and row[i] not in (None, "") else "not offered"
        levels[s["name"]] = LEVEL_FROM_FORM.get(raw, "not offered")
        present.add("services:" + s["name"])
    rec["services"] = levels

    for f in cfg.stored_fields():
        k = f["key"]
        if k in ("institution", "school") or f["type"] == "grid":
            continue
        if k in cols:
            present.add(k)
            if f["type"] in ("one", "many"):
                present.add(k + "_other")
        raw = cell(k)
        if f["type"] == "text":
            rec[k] = paragraphs(raw) if raw else ""
            continue
        if f["type"] == "short":
            rec[k] = re.sub(r"\s+", " ", str(raw)).strip() if raw else ""
            continue
        m = Matcher(tax.get(f.get("options")), aliases)
        answers = split_answers(raw) if f["type"] == "many" else ([str(raw).strip()] if raw not in (None, "") else [])
        vals, other = [], []
        for a in answers:
            hit = m.match(a)
            if hit:
                vals.extend(x for x in hit if x not in vals)
            else:
                other.append(a)
        order = cfg.options(k)
        vals.sort(key=lambda v: order.index(v) if v in order else len(order))
        rec[k] = vals if f["type"] == "many" else (vals[0] if vals else "")
        rec[k + "_other"] = "; ".join(other)
    body = paragraphs(cell("paragraph") or "")
    return rec, body, present


# ---------- comparing a response with a listing ----------

def values(rec, body, cfg):
    """{comparison key: comparable value}, with one key per service."""
    out = {}
    for k in field_keys(cfg):
        if k == "services":
            for name, level in service_levels(rec, cfg).items():
                out["services:" + name] = level
        else:
            out[k] = comparable(k, rec, cfg, body)
    return out


def take_from_form(merged, key, form, form_body, state):
    """Copy one answer from the form record into the listing being built."""
    if key == "body":
        state["body"] = form_body
    elif key.startswith("services:"):
        name = key.split(":", 1)[1]
        state["levels"][name] = form["services"][name]
    else:
        merged[key] = form.get(key)


def load_log():
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    return {"_about": "Written by scripts/import_responses.py: a fingerprint of each Forms response's answers as "
                      "last imported, used to tell form changes from GitHub edits. Commit it with the listings.",
            "responses": {}}


def existing_listings():
    """({response id: path}, {file stem: path}) for the listings in _providers."""
    by_id, by_stem = {}, {}
    for p in sorted(PROVIDERS.glob("*.md")):
        by_stem[p.stem] = p
        try:
            data = read_listing(p)[0]
        except Exception:
            continue
        if data.get("form_response_id"):
            by_id[str(data["form_response_id"])] = p
    return by_id, by_stem


def locate(form, rid, entry, by_id, by_stem):
    """The listing file for a response: by response ID, then the log, then the team name.
    Returns (path, matched_by_name)."""
    if rid in by_id:
        return by_id[rid], False
    if entry and (PROVIDERS / entry["file"]).exists():
        return PROVIDERS / entry["file"], False
    stem = slugify(form["title"])
    cand = by_stem.get(stem)
    if cand:
        other_id = str(read_listing(cand)[0].get("form_response_id") or "")
        if not other_id or other_id == rid:
            return cand, True
        n = 2
        while f"{stem}-{n}" in by_stem:
            n += 1
        print(f"note   response {rid} ({form['title']}) has the same team name as {cand.name}, which came from "
              f"response {other_id}. Using {stem}-{n}.md. If one team submitted twice, delete one of them.")
        stem = f"{stem}-{n}"
    return PROVIDERS / f"{stem}.md", False


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xlsx", help="Excel export of the questionnaire responses")
    ap.add_argument("--dry-run", action="store_true", help="report what would change; write nothing")
    ap.add_argument("--only", nargs="+", metavar="NAME_OR_ID",
                    help="only these listings (file name without .md, or Forms response ID)")
    side = ap.add_mutually_exclusive_group()
    side.add_argument("--form-wins", action="store_true", help="settle conflicts with the form's answers")
    side.add_argument("--listing-wins", action="store_true", help="settle conflicts by keeping the listing's answers")
    args = ap.parse_args()
    if (args.form_wins or args.listing_wins) and not args.only:
        sys.exit("--form-wins and --listing-wins need --only, so conflicts are settled one listing at a time.")

    cfg = Config()
    log = load_log()
    ws = openpyxl.load_workbook(args.xlsx).active
    rows = list(ws.iter_rows(values_only=True))
    cols = find_columns(rows[0], cfg.stored_fields())
    if "response_id" not in cols:
        sys.exit("No 'ID' column found. Export the responses from Forms with 'Open results in Excel'.")
    missing = [f["key"] for f in cfg.stored_fields() if f.get("question") and f["key"] not in cols]
    if missing:
        print("Note: no column found for:", ", ".join(missing), "(listings keep whatever they have for those)")
    grid = find_grid_columns(rows[0], rows[1:], cfg.services, set(cols.values()))
    if len(grid) < len(cfg.services):
        print("Note: no service-grid column found for:",
              ", ".join(s["name"] for s in cfg.services if s["name"] not in grid))

    by_id, by_stem = existing_listings()
    PROVIDERS.mkdir(parents=True, exist_ok=True)
    counts = {"new": 0, "updated": 0, "unchanged": 0, "conflicts": 0}

    for row in rows[1:]:
        form, form_body, present = parse_row(row, cols, grid, cfg)
        if not form["title"]:
            continue
        rid = form.get("form_response_id", "")
        entry = log["responses"].get(rid)
        path, by_name = locate(form, rid, entry, by_id, by_stem)
        if args.only and path.stem not in args.only and rid not in args.only:
            continue

        when = form.pop("_response_time")
        approver = form.pop("_approver")
        when_s = when.isoformat(timespec="seconds") if when else ""
        form_vals = {k: v for k, v in values(form, form_body, cfg).items() if k in present}
        notes = []
        n_strong = sum(1 for v in form["services"].values() if v == "strength")
        if n_strong > MAX_STRENGTHS:
            notes.append(f"{n_strong} areas of strength (the limit is {MAX_STRENGTHS})")
        odd = [k for k in form if k.endswith("_other") and form[k] and not cfg.by_key.get(k[:-6], {}).get("other")]
        if odd:
            notes.append("answers that aren't listed choices, kept as write-ins: " + ", ".join(odd))
        if "None of the above" in (form.get("compliance") or []) and len(form["compliance"]) > 1:
            notes.append("compliance has 'None of the above' with other choices")

        # ----- a new listing -----
        if not path.exists():
            form["form_response_id"] = rid
            counts["new"] += 1
            print(f"new      {path.name}\n         send for approval to: {approver}")
            if not form["contact"]["email"]:
                notes.append("no primary contact email (Q4); the listing's contact is blank")
            for n in notes:
                print(f"         check: {n}")
            if not args.dry_run:
                path.write_text(render(form, form_body, cfg), encoding="utf-8", newline="\n")
                log["responses"][rid] = {"file": path.name, "response_time": when_s, "conflicts": [],
                                         "answers": {k: fingerprint(v) for k, v in form_vals.items()}}
            by_stem[path.stem], by_id[rid] = path, path
            continue

        # ----- an existing listing -----
        settling = args.form_wins or args.listing_wins
        if entry and when_s and when_s <= entry.get("response_time", "") and not entry.get("conflicts") and not settling:
            counts["unchanged"] += 1
            continue

        cur, cur_body, dups = read_listing(path)
        if dups:
            print(f"skip     {path.name}: {', '.join(k for k, _ in dups)} answered more than once in the listing. "
                  f"Fix it (python scripts/check_listings.py) and re-run.")
            continue
        cur_vals = values(cur, cur_body, cfg)
        base = (entry or {}).get("answers", {})
        merged = dict(cur)
        state = {"body": cur_body, "levels": service_levels(cur, cfg)}
        took, kept, conflicts, new_base = [], [], [], dict(base)

        for k, fv in form_vals.items():
            cv = cur_vals.get(k)
            fp_form = fingerprint(fv)
            if fv == cv:
                new_base[k] = fp_form
                continue
            form_changed = base.get(k) != fp_form
            listing_edited = k not in base or base[k] != fingerprint(cv)
            if form_changed and not listing_edited or (form_changed and args.form_wins):
                take_from_form(merged, k, form, form_body, state)
                took.append(k)
                new_base[k] = fp_form
            elif not form_changed:
                kept.append(k)  # edited on GitHub since the import; the form still has the old answer
            elif args.listing_wins:
                kept.append(k)
                new_base[k] = fp_form
            else:
                conflicts.append((k, cv, fv))  # record left as it was, so this is reported again next run

        merged["services"] = state["levels"]
        merged.pop("strengths", None)
        merged["form_response_id"] = rid
        private = [k for k in PRIVATE_KEYS if cur.get(k)]
        if took:
            old = str(cur.get("updated") or "")
            merged["updated"] = max(old, form["updated"])

        label = path.name + (" (matched by team name; first import for this listing)" if by_name else "")
        if cur.get("updated") and when and str(cur["updated"]) > when.date().isoformat():
            notes.append(f"the listing was edited ({cur['updated']}) after this response was last saved ({when.date()})")
        if took:
            counts["updated"] += 1
            print(f"update   {label}\n         from the form: {', '.join(took)}\n         approver: {approver}")
        elif conflicts:
            print(f"conflict {label}")
        else:
            counts["unchanged"] += 1
            print(f"same     {label}")
        if kept:
            print(f"         kept edits made on GitHub: {', '.join(kept)}")
        if conflicts:
            counts["conflicts"] += 1
            unrecorded = all(k not in base for k, _, _ in conflicts)
            print(f"         {len(conflicts)} answer(s) differ between the listing and the form"
                  + (", and there's no import record to tell which is newer." if unrecorded else
                     ", and both changed since the last import.") + " Kept the listing's answers:")
            for k, cv, fv in conflicts:
                print(f"           {k}\n             listing: {show(cv)}\n             form:    {show(fv)}")
            print(f"         To settle: add --only {path.stem} --form-wins (or --listing-wins), "
                  f"or edit the listing and re-run.")
        for n in notes:
            print(f"         check: {n}")

        if args.dry_run:
            continue
        if took or private or str(cur.get("form_response_id") or "") != rid:
            path.write_text(render(merged, state["body"], cfg), encoding="utf-8", newline="\n")
        log["responses"][rid] = {"file": path.name, "response_time": when_s,
                                 "conflicts": [k for k, _, _ in conflicts], "answers": new_base}

    if not args.dry_run:
        LOG_PATH.parent.mkdir(exist_ok=True)
        LOG_PATH.write_text(json.dumps(log, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
                            encoding="utf-8", newline="\n")
    print(f"\n{counts['new']} new, {counts['updated']} updated, {counts['unchanged']} unchanged, "
          f"{counts['conflicts']} with conflicts to settle." + ("  (Dry run: nothing was written.)" if args.dry_run else ""))


if __name__ == "__main__":
    main()
