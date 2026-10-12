#!/usr/bin/env python3
"""Make a PDF approval sheet for each questionnaire response, to email to the team's approver.

    pip install openpyxl pyyaml
    python scripts/approval_sheet.py responses.xlsx                 # new and changed responses
    python scripts/approval_sheet.py responses.xlsx --all           # every response
    python scripts/approval_sheet.py responses.xlsx --only biomedical-imaging-analysis-core

Each sheet shows every question and every answer choice, with the team's answers ticked, the
same way the site's request-a-change page does. For a team that already has a listing, the
top of the sheet lists what differs from the live listing, so the approver can check just those.
A response that matches the live listing is skipped unless you pass --all.

The sheet is written to approvals/ (or --out) as HTML and printed to PDF with a browser that is
already on the computer: Microsoft Edge or Google Chrome. If neither is found, the HTML is kept
so it can be opened in a browser and printed to PDF from there (File > Print > Save as PDF).

PRIVACY: sheets include the names and emails of the person who filled out the form (Q2-3) and
the approver (Q6-7). They belong in the private repository only and are never published. The
approvals/ folder is in .gitignore, but the repository's access should be limited regardless.
Nothing here sends email; send each PDF to the approver named in the sheet.
"""
import argparse
import datetime as dt
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import import_responses as ir  # noqa: E402  (same parsing and comparison as the import)
from listing_format import MAX_STRENGTHS, ROOT, Config, read_listing, show  # noqa: E402

DEFAULT_OUT = ROOT / "approvals"
SERVICE_COLUMNS = [("not offered", "Not offered"), ("offered", "Offered"), ("strength", "Area of strength")]


def esc(s):
    return html.escape("" if s is None else str(s))


def cell(row, cols, key):
    i = cols.get(key)
    if i is None or i >= len(row) or row[i] in (None, ""):
        return ""
    return re.sub(r"\s+", " ", str(row[i])).strip()


# ---------- reading the export ----------

def load(xlsx):
    cfg = Config()
    heads, rows = ir.read_export(xlsx)
    cols = ir.find_columns(heads, cfg.stored_fields())
    if "response_id" not in cols:
        sys.exit("No ResponseId column found. Export the responses from Qualtrics (Use choice text).")
    grid = ir.find_grid_columns(heads, rows, cfg.services, set(cols.values()))
    return cfg, rows, cols, grid


# ---------- comparing with the live listing ----------

def label_map(cfg):
    m = {"contact": "Primary contact (Q4-5)", "institution": "Institution (Q8)", "school": "School or division (Q9)",
         "unit": "Department or unit (Q9)", "title": "Team or service name (Q10)", "website": "Website (Q11)",
         "body": "Optional paragraph (Q23)"}
    for f in cfg.stored_fields():
        m.setdefault(f["key"], f"Q{f['q']}. {f['label']}")
        if f["type"] in ("one", "many"):
            m[f["key"] + "_other"] = m[f["key"]] + ", write-in"
    return m


def differences(form, form_body, cur, cur_body, cfg, present):
    """[(question, live listing, form)] for every answer that differs. Empty for a new team."""
    labels = label_map(cfg)
    live = ir.values(cur, cur_body, cfg)
    new = {k: v for k, v in ir.values(form, form_body, cfg).items() if k in present}
    out = []
    for k, fv in new.items():
        cv = live.get(k)
        if fv == cv:
            continue
        if k.startswith("services:"):
            name = k.split(":", 1)[1]
            label = f"Services: {name}"
        else:
            label = labels.get(k, k)
        out.append((label, show(cv), show(fv)))
    return out


# ---------- notes for the approver ----------

def check_notes(form, cfg):
    notes = []
    n_strong = sum(1 for v in form["services"].values() if v == "strength")
    if n_strong > MAX_STRENGTHS:
        notes.append(f"{n_strong} areas of strength were chosen; the limit is {MAX_STRENGTHS}. Please choose up to {MAX_STRENGTHS}.")
    labels = label_map(cfg)
    for f in cfg.stored_fields():
        k = f["key"]
        if f["type"] in ("one", "many") and form.get(k + "_other"):
            notes.append(f"Write-in for {labels.get(k, k)}: “{form[k + '_other']}”. It isn't one of the "
                         f"listed choices, so it appears as a write-in on the site.")
    if form.get("school") and form["school"] not in {s["name"] for s in cfg.taxonomy["schools"]}:
        notes.append(f"The school “{form['school']}” isn't one of the listed schools. Please check the school "
                     f"and unit, since the form collects them as one answer.")
    if "None of the above" in (form.get("compliance") or []) and len(form["compliance"]) > 1:
        notes.append("Requirements and reviews: “None of the above” is chosen along with other answers.")
    if not (form.get("contact") or {}).get("email"):
        notes.append("No primary contact email was given (Q5). The listing will have no contact email until one is added.")
    return notes


# ---------- the sheet ----------

CSS = """
@page { size: Letter; margin: 0.6in 0.6in 0.7in; }
* { box-sizing: border-box; }
body { font-family: "Work Sans", Tahoma, Arial, sans-serif; font-size: 10pt; line-height: 1.4; color: #1b1b1b; margin: 0; }
h1, h2, h3 { font-family: "Source Serif 4", Georgia, serif; color: #002D72; margin: 0; font-weight: 600; }
h1 { font-size: 20pt; line-height: 1.2; margin-top: 2px; }
h2 { font-size: 13pt; border-bottom: 2px solid #002D72; padding-bottom: 3px; margin: 18px 0 8px; break-after: avoid; }
h3 { font-size: 10.5pt; margin: 0; }
.kicker { font-size: 8pt; letter-spacing: .08em; text-transform: uppercase; color: #5a6270; margin: 0; }
.sub { color: #3d4450; margin: 2px 0 10px; }
.meta { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 18px; margin: 0 0 10px; border-top: 1px solid #c9d1de; padding-top: 8px; }
.meta div { break-inside: avoid; }
dt { font-size: 7.5pt; text-transform: uppercase; letter-spacing: .05em; color: #5a6270; }
dd { margin: 1px 0 0; }
.status { background: #eef3fa; border-left: 4px solid #002D72; padding: 7px 10px; margin: 10px 0 0; }
.status--update { background: #fff6e6; border-color: #C9731C; }
.notes { border: 1px solid #C9731C; background: #fffaf2; padding: 6px 12px 6px 26px; margin: 10px 0 0; }
.notes li { margin: 3px 0; }
table { width: 100%; border-collapse: collapse; margin-top: 6px; }
th, td { text-align: left; vertical-align: top; padding: 4px 6px; border-bottom: 1px solid #dde3ec; }
.changes th { font-size: 8pt; text-transform: uppercase; letter-spacing: .04em; color: #5a6270; }
.changes td:first-child { width: 30%; font-weight: 600; }
.changes td:nth-child(2) { color: #6b3d00; }
.changes td:nth-child(3) { color: #0a4a2a; }
.q { break-inside: avoid; padding: 6px 0 8px; border-bottom: 1px solid #eef1f5; }
.q--long { break-inside: auto; }
.hint { font-size: 8pt; color: #5a6270; margin: 1px 0 4px; }
.choices { list-style: none; margin: 0; padding: 0; columns: 2; column-gap: 24px; }
.choices li { break-inside: avoid; padding: 1px 0; }
.choices .box { display: inline-block; width: 1.25em; font-size: 11pt; line-height: 1; }
.choices .on { color: #002D72; font-weight: 600; }
.choices .off { color: #8a8f98; }
.answer { margin: 0; }
.other { margin: 4px 0 0; }
.blank { color: #8a8f98; font-style: italic; }
.skipped { color: #5a6270; font-style: italic; margin: 0; }
.prose p { margin: 0 0 6px; }
.grid th { font-size: 8pt; text-transform: uppercase; letter-spacing: .03em; color: #5a6270; text-align: center; }
.grid th:first-child { text-align: left; }
.grid td.mark { text-align: center; color: #002D72; font-size: 11pt; width: 15%; }
.grid tr.grp th { background: #f2f5f9; color: #002D72; font-family: "Work Sans", Tahoma, Arial, sans-serif; text-transform: none; font-size: 9pt; letter-spacing: 0; text-align: left; }
.grid tr { break-inside: avoid; }
.grid tr.strength td { background: #eef3fa; }
.svc { font-weight: 600; display: block; }
.detail { color: #5a6270; font-size: 8pt; }
.foot { margin-top: 20px; border-top: 1px solid #c9d1de; padding-top: 8px; color: #5a6270; font-size: 8.5pt; }
.facts { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 18px; margin: 4px 0 0; }
.facts div { break-inside: avoid; }
"""


def field_block(f, form, cfg):
    k, t = f["key"], f["type"]
    head = f"Q{f['q']}. {f['label']}"
    if t in ("one", "many"):
        sel = form.get(k)
        sel = sel if isinstance(sel, list) else ([sel] if sel else [])
        hint = "Choose one" if t == "one" else "Choose all that apply"
        items = []
        for o in cfg.options(k):
            on = o in sel
            items.append(f'<li class="{"on" if on else "off"}"><span class="box">{"☑" if on else "☐"}</span>{esc(o)}</li>')
        other = form.get(k + "_other")
        extra = f'<p class="other"><strong>Write-in:</strong> {esc(other)}</p>' if other else ""
        none = "" if sel or other else '<p class="answer blank">Nothing selected</p>'
        return (f'<div class="q"><h3>{esc(head)}</h3><p class="hint">{hint}</p>'
                f'<ul class="choices">{"".join(items)}</ul>{none}{extra}</div>')
    value = form.get(k) or ""
    if t == "text" and value:
        paras = "".join(f"<p>{esc(p)}</p>" for p in str(value).split("\n\n"))
        val = f'<div class="prose">{paras}</div>'
    elif value:
        val = f'<p class="answer">{esc(value)}</p>'
    else:
        val = '<p class="answer blank">Not answered</p>'
    return f'<div class="q"><h3>{esc(head)}</h3>{val}</div>'


def grid_block(cfg, levels):
    rows = []
    for g in cfg.taxonomy.get("service_groups") or []:
        rows.append(f'<tr class="grp"><th colspan="4">{esc(g)}</th></tr>')
        for s in cfg.services:
            if s["group"] != g:
                continue
            lvl = levels.get(s["name"], "not offered")
            marks = "".join(f'<td class="mark">{"●" if lvl == col else ""}</td>' for col, _ in SERVICE_COLUMNS)
            cls = ' class="strength"' if lvl == "strength" else ""
            detail = f'<span class="detail">{esc(s.get("detail"))}</span>' if s.get("detail") else ""
            rows.append(f'<tr{cls}><td><span class="svc">{esc(s["name"])}</span>{detail}</td>{marks}</tr>')
    heads = "".join(f"<th>{esc(label)}</th>" for _, label in SERVICE_COLUMNS)
    n = sum(1 for v in levels.values() if v == "strength")
    return (f'<div class="q q--long"><h3>Q16-19. Services and areas of strength</h3>'
            f'<p class="hint">Mark each service. Areas of strength: {n} of {MAX_STRENGTHS} allowed.</p>'
            f'<table class="grid"><thead><tr><th>Service</th>{heads}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def sheet_html(form, body, cfg, meta):
    rid = meta["rid"]
    contact = form.get("contact") or {}
    facts = [
        ("Primary contact (Q4-5)", " · ".join(x for x in (contact.get("name"), contact.get("email")) if x) or "Not given"),
        ("Institution (Q8)", form.get("institution") or "Not given"),
        ("School or division (Q9)", form.get("school") or "Not given"),
        ("Department or unit (Q9)", form.get("unit") or "Not given"),
        ("Team or service name (Q10)", form.get("title") or "Not given"),
        ("Website (Q11)", form.get("website") or "Not given"),
    ]
    facts_html = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in facts)

    if meta["status"] == "new":
        status = ("<strong>New team.</strong> This team is not on the site yet. Please check every answer below, "
                  "then reply to RSSN to approve the listing or to note corrections.")
        status_cls = ""
    elif meta["status"] == "update":
        status = (f"<strong>Changes to the live listing.</strong> {len(meta['diffs'])} answer(s) differ from what "
                  f"the site shows now. The changes are listed first, followed by all answers. Please check the "
                  f"changes, then reply to RSSN to approve or to note corrections.")
        status_cls = " status--update"
    else:
        status = "This response matches the live listing. Nothing needs to change."
        status_cls = ""

    parts = [f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Approval sheet: {esc(form.get('title'))}</title><style>{CSS}</style></head><body>
<p class="kicker">Listing approval sheet · RSSN Service Provider Inventory questionnaire, 2026</p>
<h1>{esc(form.get('title'))}</h1>
<p class="sub">{esc(' · '.join(x for x in (form.get('school'), form.get('unit')) if x))}</p>
<dl class="meta">
  <div><dt>Response</dt><dd>#{esc(rid)}, submitted {esc(meta['when'])}</dd></div>
  <div><dt>Approver (Q6-7)</dt><dd>{esc(meta['approver'])}</dd></div>
  <div><dt>Submitted by (Q2-3)</dt><dd>{esc(meta['submitter'])}</dd></div>
  <div><dt>Sheet made</dt><dd>{esc(meta['made'])}</dd></div>
</dl>
<div class="status{status_cls}">{status}</div>"""]

    if meta["notes"]:
        items = "".join(f"<li>{esc(n)}</li>" for n in meta["notes"])
        parts.append(f'<div class="notes"><strong>Check before approving</strong><ul>{items}</ul></div>')

    if meta["status"] == "update":
        rows = "".join(f"<tr><td>{esc(q)}</td><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for q, a, b in meta["diffs"])
        parts.append(f'<h2>What changes on the live listing</h2><table class="changes"><thead><tr>'
                     f'<th>Question</th><th>Live now</th><th>Form says</th></tr></thead><tbody>{rows}</tbody></table>')

    parts.append("<h2>All answers</h2>")
    skip_technical = form.get("hands_on") == "No"
    for sec in cfg.sections:
        blocks = []
        if sec["id"] == "organization":
            parts.append(f"<h2>{esc(sec['title'])}</h2><div class=\"facts\">{facts_html}</div>")
            continue
        if sec["id"] == "additional":  # Q23 is the optional paragraph, which comes before Q54
            blocks.append(f'<div class="q"><h3>Q23. Is there anything else you would like to highlight?</h3>'
                          + (f'<div class="prose">' + "".join(f"<p>{esc(p)}</p>" for p in body.split("\n\n")) + "</div>"
                             if body else '<p class="answer blank">Not answered</p>')
                          + "</div>")
        for f in sec["fields"]:
            if f.get("derived") or f["key"] in ("institution", "school"):
                continue
            if f["key"] == "services":
                blocks.append(grid_block(cfg, form.get("services") or {}))
                continue
            if sec["id"] == "technical" and skip_technical and f["key"] != "hands_on":
                blocks.append(f'<div class="q"><h3>Q{f["q"]}. {esc(f["label"])}</h3>'
                              f'<p class="skipped">Skipped: the team doesn\'t do hands-on technical work (Q24 is "No").</p></div>')
                continue
            blocks.append(field_block(f, form, cfg))
        parts.append(f"<h2>{esc(sec['title'])}</h2>" + "".join(blocks))

    parts.append(f"""<div class="foot">
<p>Please reply to RSSN to approve this listing, or to note any corrections. Once approved, RSSN publishes the
answers on the Research IT Provider Inventory site.</p>
<p>This sheet is confidential: it contains the names and email addresses of the people involved.
Generated from response #{esc(rid)} on {esc(meta['made'])}.</p></div></body></html>""")
    return "".join(parts)


# ---------- printing to PDF ----------

def find_browser():
    """A Chromium-based browser already on the computer, or None."""
    found = []
    if os.name == "nt":
        for env in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            base = os.environ.get(env)
            if base:
                found += [Path(base, "Microsoft", "Edge", "Application", "msedge.exe"),
                          Path(base, "Google", "Chrome", "Application", "chrome.exe")]
    for name in ("msedge", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(name)
        if p:
            found.append(Path(p))
    return next((p for p in found if p.exists()), None)


def html_to_pdf(html_path, pdf_path, browser):
    cmd = [str(browser), "--headless", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()]
    if hasattr(os, "geteuid") and os.geteuid() == 0:  # running as root in a container
        cmd.insert(1, "--no-sandbox")
    try:
        subprocess.run(cmd, capture_output=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return pdf_path.exists() and pdf_path.stat().st_size > 0


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xlsx", help="Excel export of the questionnaire responses")
    ap.add_argument("--only", nargs="+", metavar="NAME_OR_ID",
                    help="only these responses (listing file name without .md, or response ID)")
    ap.add_argument("--all", action="store_true", help="include responses that match the live listing")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"folder for the sheets (default: {DEFAULT_OUT.name}/)")
    ap.add_argument("--html", action="store_true", help="keep the HTML next to each PDF")
    ap.add_argument("--browser", type=Path, help="path to msedge.exe or chrome.exe, if it isn't found automatically")
    args = ap.parse_args()

    cfg, rows, cols, grid = load(args.xlsx)
    by_id, by_stem = ir.existing_listings()
    log = ir.load_log()
    browser = args.browser if args.browser else find_browser()
    if browser is None:
        print("No Edge or Chrome found, so the sheets will be HTML. Open each one in a browser and "
              "choose Print > Save as PDF.")
    args.out.mkdir(parents=True, exist_ok=True)
    made = dt.date.today().isoformat()
    counts = {"new": 0, "update": 0, "same": 0}

    for row in rows:
        form, body, present = ir.parse_row(row, cols, grid, cfg)
        if not form["title"]:
            continue
        rid = form.get("form_response_id", "")
        path, _ = ir.locate(form, rid, log["responses"].get(rid), by_id, by_stem)
        if args.only and path.stem not in args.only and rid not in args.only:
            continue

        when = form.pop("_response_time")
        approver = form.pop("_approver")
        if path.exists():
            cur, cur_body, _ = read_listing(path)
            diffs = differences(form, body, cur, cur_body, cfg, present)
            status = "update" if diffs else "same"
        else:
            diffs, status = [], "new"
        counts[status] += 1
        if status == "same" and not args.all:
            continue

        meta = {
            "rid": rid or "(no ID)",
            "when": when.strftime("%B %-d, %Y") if when else "unknown date",
            "approver": approver,
            "submitter": " ".join(x for x in (cell(row, cols, "respondent_name"),
                                              cell(row, cols, "respondent_email") and f"<{cell(row, cols, 'respondent_email')}>") if x) or "Not given",
            "made": made,
            "status": status,
            "diffs": diffs,
            "notes": check_notes(form, cfg),
        }
        stem = f"approval-{path.stem}-{rid or 'no-id'}"
        html_path = args.out / f"{stem}.html"
        pdf_path = args.out / f"{stem}.pdf"
        html_path.write_text(sheet_html(form, body, cfg, meta), encoding="utf-8", newline="\n")
        if browser and html_to_pdf(html_path, pdf_path, browser):
            result = pdf_path.name
            if not args.html:
                html_path.unlink()
        else:
            result = html_path.name + " (HTML)"
        print(f"{status:6}   {form['title']}  ->  {args.out.name}/{result}")
        print(f"         send to: {approver}")
        if status == "update":
            print(f"         {len(diffs)} answer(s) differ from the live listing")
        for n in meta["notes"]:
            print(f"         check: {n}")

    print(f"\n{counts['new']} new, {counts['update']} with changes, {counts['same']} matching the live listing"
          + (" (skipped; use --all to include them)." if counts["same"] and not args.all else "."))


if __name__ == "__main__":
    main()
