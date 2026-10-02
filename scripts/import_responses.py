#!/usr/bin/env python3
"""Turn questionnaire responses (the Microsoft Forms Excel export) into provider listings.

Written for Draft 3 of the RSSN Research IT Provider Questionnaire.

    pip install openpyxl pyyaml
    python scripts/import_responses.py responses.xlsx            # writes new listings only
    python scripts/import_responses.py responses.xlsx --overwrite

Each response row becomes _providers/<team-name>.md. Answers are matched against the
allowed values in _data/taxonomy.yml; anything that doesn't match (a write-in "Other"
answer, say) is kept in that field's "<key>_other" text so nothing is lost.

The four service grids (Q12-15) are found by their answers: any column whose answers are
all "Not offered", "Offered", or "Area of strength" is a grid row, and the service it
belongs to is the one whose name appears in the column heading.

Always review the generated files before committing. Check the school and unit
especially, since the form collects those as one free-text answer.
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

try:
    import openpyxl
    import yaml
except ImportError:
    sys.exit("This script needs openpyxl and pyyaml: pip install openpyxl pyyaml")

ROOT = Path(__file__).resolve().parent.parent

# Provider-information columns that aren't part of _data/fields.yml.
INFO_COLUMNS = {
    "respondent_name": "Name of the person completing",
    "respondent_email": "Email address of the person completing",
    "contact_name": "Primary contact name",
    "contact_email": "Primary contact email",
    "title": "Team or service name",
    "paragraph": "Is there anything else you would like to highlight",
    "website": "Website or service information URL",
    "completed": "Completion time",
}


def norm(s):
    """Lowercase, straighten quotes, collapse whitespace."""
    s = str(s).replace("’", "'").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def label_of(opt):
    if isinstance(opt, dict):
        return opt.get("label") or opt.get("name")
    return str(opt)


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
    wanted = dict(INFO_COLUMNS)
    for f in fields:
        if f.get("question"):
            wanted[f["key"]] = f["question"]
    for key, q in wanted.items():
        qn = norm(q)
        hits = [i for i, h in enumerate(heads) if h.startswith(qn)]
        if key == "institution":  # "Institution" is a prefix of nothing else, but be exact
            hits = [i for i, h in enumerate(heads) if h == "institution"] or hits
        if hits:
            cols[key] = hits[0]
    return cols


def find_grid_columns(headers, rows, services, levels, taken):
    """Map each service name to its grid column (see the module docstring).
    `taken` holds columns already matched to other questions."""
    level_set = {norm(l) for l in levels}
    out = {}
    for i, h in enumerate(headers):
        if i in taken:
            continue
        vals = {norm(r[i]) for r in rows if i < len(r) and r[i] not in (None, "")}
        if not vals <= level_set:  # an empty column (nobody answered) still counts
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
    kept = [p for p in parts if norm(p) not in drop]
    return ", ".join(kept)


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


def q(s):
    """A double-quoted YAML string (JSON strings are valid YAML)."""
    return json.dumps(str(s), ensure_ascii=False)


def yaml_value(k, v, ftype):
    """Front-matter lines for one field."""
    if ftype in ("many", "grid"):
        if not v:
            return [f"{k}: []"]
        return [f"{k}:"] + [f"  - {q(x)}" for x in v]
    if ftype == "text":
        v = (v or "").strip()
        if not v:
            return [f'{k}: ""']
        return [f"{k}: |"] + [("  " + l) if l else "" for l in v.split("\n")]
    return [f"{k}: {q(v or '')}"]


def to_markdown(rec, fields, body, header=None):
    out = ["---"]
    out.extend(header or [
        "# Imported from the RSSN Research IT Provider Questionnaire (Draft 3).",
        "# Allowed values for each list are in _data/taxonomy.yml.",
    ])
    if rec.get("sample"):
        out.append("sample: true")
    for key in ["title", "institution", "school", "unit", "website"]:
        out.append(f"{key}: {q(rec.get(key, ''))}")
    out.append("contact:")
    out.append(f"  name: {q(rec['contact']['name'])}")
    out.append(f"  email: {q(rec['contact']['email'])}")
    if rec.get("submitted_by"):
        out.append("submitted_by:")
        out.append(f"  name: {q(rec['submitted_by']['name'])}")
        out.append(f"  email: {q(rec['submitted_by']['email'])}")
    if rec.get("updated"):
        out.append(f"updated: {rec['updated']}")
    own_keys = {f["key"] for f in fields}
    for f in fields:
        k = f["key"]
        if k in ("institution", "school"):
            continue
        out.extend(yaml_value(k, rec.get(k), f["type"]))
        if rec.get(k + "_other") and f["type"] != "text" and k + "_other" not in own_keys:
            out.append(f"{k}_other: {q(rec[k + '_other'])}")
    out.append("---")
    out.append(body)
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xlsx", help="Excel export of the questionnaire responses")
    ap.add_argument("--out", default=str(ROOT / "_providers"), help="folder for listings (default: _providers)")
    ap.add_argument("--overwrite", action="store_true", help="replace listings that already exist")
    args = ap.parse_args()

    taxonomy = yaml.safe_load((ROOT / "_data/taxonomy.yml").read_text(encoding="utf-8"))
    sections = yaml.safe_load((ROOT / "_data/fields.yml").read_text(encoding="utf-8"))["sections"]
    fields = [f for s in sections for f in s["fields"]]
    aliases = taxonomy.get("aliases") or {}
    schools = taxonomy.get("schools") or []

    ws = openpyxl.load_workbook(args.xlsx).active
    rows = list(ws.iter_rows(values_only=True))
    cols = find_columns(rows[0], fields)
    missing = [f["key"] for f in fields if f.get("question") and f["key"] not in cols]
    if missing:
        print("Note: no column found for:", ", ".join(missing))
    grid = find_grid_columns(rows[0], rows[1:], taxonomy["services"], taxonomy["service_levels"], set(cols.values()))
    if len(grid) < len(taxonomy["services"]):
        absent = [s["name"] for s in taxonomy["services"] if s["name"] not in grid]
        print("Note: no service-grid column found for:", ", ".join(absent))

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for row in rows[1:]:
        cell = lambda k: (row[cols[k]] if k in cols and cols[k] < len(row) else None)
        title = (cell("title") or "").strip()
        if not title:
            continue
        rec = {"title": title}

        respondent = {"name": (cell("respondent_name") or "").strip(), "email": (cell("respondent_email") or "").strip()}
        contact = {"name": (cell("contact_name") or "").strip(), "email": (cell("contact_email") or "").strip()}
        rec["submitted_by"] = respondent
        rec["contact"] = contact if (contact["name"] or contact["email"]) else dict(respondent)

        site = (cell("website") or "").strip()
        if site and not re.match(r"https?://", site):
            site = "https://" + site
        rec["website"] = site

        done = cell("completed")
        rec["updated"] = (done.date() if isinstance(done, dt.datetime) else dt.date.today()).isoformat()

        # Institution and school: the form asks for school, department, and unit in one answer.
        inst_raw = (cell("institution") or "").strip()
        school_raw = (cell("school") or "").strip()
        inst = Matcher(taxonomy.get("institutions"), aliases).match(inst_raw)
        school, alias_hit = find_school(f"{inst_raw}, {school_raw}", schools)
        rec["institution"] = inst[0] if inst else ("JHU" if school else inst_raw)
        if school:
            rec["school"] = school
            rec["unit"] = clean_unit(school_raw, alias_hit, school)
        else:
            rec["school"] = school_raw
            rec["unit"] = ""

        # Service grids (Q12-15): Offered or Area of strength -> services; Area of strength -> strengths.
        rec["services"], rec["strengths"] = [], []
        for s in taxonomy["services"]:
            i = grid.get(s["name"])
            level = norm(row[i]) if i is not None and i < len(row) and row[i] else ""
            if level in ("offered", "area of strength"):
                rec["services"].append(s["name"])
            if level == "area of strength":
                rec["strengths"].append(s["name"])

        for f in fields:
            k = f["key"]
            if k in ("institution", "school") or f["type"] == "grid":
                continue
            raw = cell(k)
            if f["type"] == "text":
                rec[k] = paragraphs(raw) if raw else ""
                continue
            if f["type"] == "short":
                rec[k] = re.sub(r"\s+", " ", str(raw)).strip() if raw else ""
                continue
            m = Matcher(taxonomy.get(f.get("options")), aliases)
            answers = split_answers(raw) if f["type"] == "many" else ([str(raw).strip()] if raw not in (None, "") else [])
            vals, other = [], []
            for a in answers:
                hit = m.match(a)
                if hit:
                    vals.extend(x for x in hit if x not in vals)
                else:
                    other.append(a)
            order = [label_of(o) for o in (taxonomy.get(f.get("options")) or [])]
            vals.sort(key=lambda v: order.index(v) if v in order else len(order))
            rec[k] = vals if f["type"] == "many" else (vals[0] if vals else "")
            if other:
                rec[k + "_other"] = "; ".join(other)
                # Q10's "It's complicated (please explain)" arrives as the explanation itself.
                if k == "availability" and not vals:
                    rec[k] = "It's complicated"

        path = out_dir / (slugify(title) + ".md")
        if path.exists() and not args.overwrite:
            print(f"skip   {path.name} (exists; use --overwrite to replace)")
            continue
        path.write_text(to_markdown(rec, fields, paragraphs(cell("paragraph") or "")), encoding="utf-8")
        own = {f["key"] for f in fields}
        notes = [k for k in rec if k.endswith("_other") and k not in own and rec[k]]
        if len(rec["strengths"]) > 5:
            notes.append(f"{len(rec['strengths'])} areas of strength (limit is 5)")
        if "None of the above" in (rec.get("compliance") or []) and len(rec["compliance"]) > 1:
            notes.append("compliance has 'None of the above' with other choices")
        print(f"wrote  {path.name}" + (f"  (check: {', '.join(notes)})" if notes else ""))


if __name__ == "__main__":
    main()
