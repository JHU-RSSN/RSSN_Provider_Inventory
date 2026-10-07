# RSSN Provider Inventory (prototype)

A prototype GitHub Pages site for the Research Software Support Network (RSSN) service provider inventory. It lists Johns Hopkins teams that support research software, data, and computing, with search, filters, and a profile page for each team.

**Live site:** https://jhu-rssn.github.io/RSSN_Provider_Inventory/

> The site follows Draft 3 of the RSSN Research IT Provider Questionnaire. Listings without `sample: true` come from pilot responses to Draft 2 (September 2026), carried over to Draft 3's fields; questions Draft 2 didn't ask are left blank, and every team will resubmit on the final form. Listings with `sample: true` are fictional examples kept to show how the directory works; delete them once real listings cover the same ground.

## How it works

The site is built with [Jekyll](https://jekyllrb.com/), which GitHub Pages runs automatically. There's no server or database. Every push to `main` rebuilds the site in a minute or two.

- Each team is one Markdown file in `_providers/`. Jekyll turns each file into a profile page at `/providers/<file-name>/`, plus a card and a table row on the home page.
- The home page's search, filters, sorting, and Cards/Table switch run in the browser (`assets/js/directory.js`) using data Jekyll writes into the page at build time.
- `_data/fields.yml` lists every listing field, grouped the way the questionnaire groups them. It drives the profile page, the search data, the filter panel, and the import script.
- Allowed values for every list field live in `_data/taxonomy.yml`. They mirror the RSSN Research IT Provider Questionnaire.

## The listing file format

Every listing file lists every answer choice from the questionnaire, so people editing on GitHub select and unselect answers instead of typing them from memory. Choices that weren't picked are commented out with `# `, and Jekyll ignores commented lines, so the site only sees the selected answers. Each question's comment says whether it's **CHOOSE ONE** or **CHOOSE ALL THAT APPLY**:

```yaml
# Q12. Available to. CHOOSE ONE.
availability: "Hopkins-wide"
# availability: "JHU only"

# Q14. Who can engage this team. CHOOSE ALL THAT APPLY.
eligible:
  - "JHHS faculty"
  # - "JHHS staff"
```

The four service grids (Q15–18) are one `services` map that works like the form's grid: every service is followed by `not offered`, `offered`, or `strength` (offered and an area of strength; no more than five). The site works out the services and areas of strength from it (`_includes/service-levels.html`).

```yaml
services:
  "AI-Assisted Coding":              offered
  "Python or R Package Development": strength
  "Data Pipeline Automation":        not offered
```

`scripts/listing_format.py` reads and writes this format, and every script below uses it.

## Importing questionnaire responses

`scripts/import_responses.py` turns the Microsoft Forms Excel export of the Draft 3 questionnaire into listings, one file per response:

```sh
pip install openpyxl pyyaml
python scripts/import_responses.py "Research Software Support Network ... .xlsx" --dry-run   # report only
python scripts/import_responses.py "Research Software Support Network ... .xlsx"
```

Answers are matched to the values in `_data/taxonomy.yml`. Anything that doesn't match, like an "Other" answer, is kept as text in that field's `_other` key. The service grids are recognized by their answers (Not offered / Offered / Offered & Area of strength), so the exact column headings Forms uses don't matter. For each file, the script lists what to check: answers that aren't listed choices, more than five areas of strength, or "None of the above" chosen alongside other compliance answers. Review each new file before committing, especially `school` and `unit`, since the form collects those as one free-text answer.

**Teams should edit their listing on GitHub, not by resubmitting the form.** In case someone resubmits anyway, the script never simply overwrites a listing:

1. Each listing records its Forms response ID (`form_response_id`), and the script finds the listing by that ID, so a team renamed in the form still updates the same file.
2. A response is only looked at again if it changed since it was last imported (Forms' "Last modified time"). Unchanged responses are skipped.
3. `_imports/import_log.json` keeps a fingerprint of every answer as last imported. For each answer the script compares the form, the listing, and that record: an answer changed only in the form is updated; one changed only on GitHub is kept; one changed in both is a **conflict**. Conflicts keep the listing's answer and are reported on every run until someone settles them, either by editing the listing or with `--only <file-name> --form-wins` (or `--listing-wins`).

A listing that was never imported (the pilot listings, for example) has no record, so when its team submits the form, every difference is reported as a conflict. If the new response should replace the pilot data, run `--only <file-name> --form-wins`.

Commit `_imports/import_log.json` along with the listings; without it, the script can't tell form changes from GitHub edits. Jekyll ignores the `_imports` folder.

The script was tested against a mock Draft 3 export. Run it with `--dry-run` on the first real export and check the "no column found" notes before trusting the output. It hasn't been confirmed yet that Forms keeps the same response ID when someone edits a submitted response; check this the first time it happens.

If the questionnaire adds or renames an answer choice, add it to `_data/taxonomy.yml` first so it imports as a filterable value instead of a write-in.

## Adding or updating a listing by hand

Contributors don't need to clone anything. The site's [Add your service](https://jhu-rssn.github.io/RSSN_Provider_Inventory/add-your-service/) page walks them through proposing a change on github.com. Every provider profile has two buttons: "See all answers & request a change" (email, no GitHub needed) and "Suggest an edit on GitHub" (quicker for maintainers, since it arrives as a ready-to-merge pull request).

1. Copy `_includes/provider-template.md` into `_providers/` and give it a lowercase, hyphenated name, like `imaging-software-team.md`. The file name becomes the page's URL.
2. Select answers by deleting the `# ` in front of them, and mark each service `not offered`, `offered`, or `strength`.
3. Replace the placeholder text at the bottom with the team's optional paragraph (Q21, about 500 characters), or delete it.
4. Open a pull request. A reviewer merges it, and the listing goes live.

### Change requests by email (no GitHub needed)

Every profile has a **See all answers & request a change** button. It opens `/request-a-change/?team=<file-name>` (`request-a-change.html` and `assets/js/request-change.js`), which shows the team's whole listing as the questionnaire: every question, every answer choice, and the current answers selected. The visitor changes what's out of date and clicks **Prepare my email**; the page writes a plain-text summary (for example "Q23. Languages: Add: Java / Remove: PHP", or "Databases: Not offered -> Offered") and opens it in their email program, with a Copy button as a fallback. Nothing is saved or sent by the site, so there's nothing to maintain beyond the page itself. The questions and choices come from `_data/fields.yml` and `_data/taxonomy.yml`, so the page stays in step with the listing files.

Emails go to `change_requests_email` in `_config.yml`. A reviewer applies the requested changes to the listing file on GitHub (each change maps to adding or removing `# ` on a line), then checks it with `scripts/check_listings.py`.

### Reviewing a pull request

`python scripts/check_listings.py` checks every listing (or just the files you name) for the mistakes that are easy to make when editing: two answers left selected on a CHOOSE ONE question, an answer whose spelling no longer matches a choice (it would drop out of filters), a service marked with some other word, more than five strengths, or a line whose spacing broke the file. It reports line numbers and suggests the closest listed choice. It needs Python with PyYAML; if you'd rather not run it, check the same things by eye in the pull request's diff.

### Listing fields

Every field maps to a questionnaire question. The full list, with labels and question numbers, is in `_data/fields.yml`.

| Questionnaire section (Draft 3) | Fields |
| --- | --- |
| Provider information (Q1–10) | `contact.name`, `contact.email` (Q3–4), `institution`, `school`, `unit`, `title`, `website`. Q1–2 (who filled out the form) and Q5–6 (the approving team lead) aren't stored; see below. |
| Who you support (Q11–14) | `team_type`, `availability`, `availability_details` (Q13), `eligible` |
| Services & expertise (Q15–20) | `services` (Q15–18: every service as not offered / offered / strength), `services_other` (Q19), `examples` (Q20) |
| Optional paragraph (Q21) | the body text below the front matter |
| Technical capabilities (Q22–26) | `hands_on`, `languages`, `databases`, `devops`, `hosting` |
| Research experience (Q27–31) | `research_areas`, `stages`, `grant_estimates`, `pre_award`, `consult_scope` |
| Data, security & compliance (Q32–34) | `data_types`, `compliance`, `security_approach` |
| Engagement model (Q35–39) | `engagement_types`, `project_sizes`, `durations`, `takeover`, `collaborate` |
| Cost & funding (Q40–44) | `cost`, `free_limit`, `charges`, `minimum`, `funding` |
| Availability & support (Q45–48) | `accepting`, `lead_time`, `production_support`, `support_coverage` |
| Open source & sustainability (Q49–51) | `open_source`, `handoff_docs`, `maintenance` |
| Additional information (Q52) | `notes` |

### The summary

Each card and profile opens with a summary built from the answers, as Q21 promises respondents: unit and team name, team type, availability, areas of strength, cost, lead time, and whether the team is accepting new work. The wording comes from the `phrase` values in `_data/taxonomy.yml`, and the template is `_includes/summary.html`. Cards use a shorter version (team type and cost), since they already show the rest.

### Pausing new requests

`accepting` (Q45) is its own field so a team can pause or resume requests with a quick edit: select `"Not at this time"` and the card and table show it under "Taking new work," and the profile gets a banner.

Any list or single-answer field can also have a `<field>_other` text value for write-in answers. Listings also carry `updated` (date of the response or last review), `form_response_id` (links the listing to its Forms response), and `sample: true` for fictional listings.

Only answers respondents agreed to publish go into listings, since this repository and site are public. The name and email of the person who filled out the questionnaire (Q1–2) and of the team lead who approves the listing (Q5–6) stay in the Forms results: the import script prints the approver for each new or updated listing so RSSN can send it for approval, but never writes them to a file, and `scripts/check_listings.py` flags a listing that contains them. The primary contact (Q3–4) is published, as the form says.

## Adding a filter or field

1. Add the field to `_data/fields.yml` in the right section, and its allowed values to `_data/taxonomy.yml`. The profile page picks it up automatically.
2. Run `python scripts/refresh_listings.py` to add it (and any new answer choices) to every listing file, and `python scripts/make_template.py` to rebuild `_includes/provider-template.md`. Review the diff before committing. If you renamed a choice, update the listings that use the old wording first; the refresh keeps it and marks it "not one of the listed choices".
3. To filter on it, add it to the `filters` list at the bottom of `_data/fields.yml`.

## Teams that only serve their own unit

Some teams are listed so RSSN knows the capability exists, even though they don't take outside requests. Availability answers marked `internal: true` in `_data/taxonomy.yml` ("No - our services are limited to our own department/unit") flag these teams. On cards and in the table their "Available to" value is shown in plum with a lock, and their profiles open with a "Not taking outside requests" banner.

On the home page they're hidden by default behind a pre-checked "Only show teams that take requests from outside their unit" box at the top of the filters. The result count says how many are hidden, with a link to show them. "Clear all" doesn't change this box.

## Cards and table views

The home page shows cards by default. The Table button switches to a table with one row per team: name and school, top three areas of strength, available to, lead time, and taking new work. Each row's arrow opens a details row (the team's description, all strengths, languages, and data types); "Expand all" opens every visible row. Table rows come from `_includes/table-row.html`, cards from `_includes/card.html`, and both use `_includes/availability.html` and `_includes/accepting.html` for those values.

- **Filters, search, view, and sort all live in the page address** (`?view=table&sort=lead_time&dir=desc`), so they survive switching views, refreshing, and sharing a link.
- **Sorting** works from the Sort menu above either view or from the table's column headers (click again to reverse). Team and School sort A–Z. Available to, Lead time, and Taking new work sort in the order their answers are listed in `_data/taxonomy.yml`, so reordering a list there changes the sort. "Varies based on project" and "It's complicated" sort after the real answers, and blank answers ("Not reported") sort last, in either direction. Ties sort by team name.
- **Default order** lists real listings A–Z, then sample listings. Once a sort is chosen, samples mix in with the real listings.
- **Phones** (720px wide or less) show cards only; the Table button is hidden there.
- **Teams that don't do hands-on technical work** (Q22 = "No") show N/A for languages in the table and for the whole Technical capabilities section on their profile, instead of leaving those questions blank.

## Design

Colors follow the [Johns Hopkins color guidelines](https://brand.jhu.edu/visual-identity/colors/). Heritage Blue leads, and the secondary palette only appears as the thin card accents that mark each school. Type uses Source Serif 4 and Work Sans, two of the university's [open-source typefaces](https://brand.jhu.edu/visual-identity/typography/), with Georgia and Tahoma as fallbacks. All styles are in `assets/css/site.css`.

## Previewing locally (optional)

You only need this to preview changes before pushing. With Ruby installed:

```sh
bundle install
bundle exec jekyll serve
```

Then open http://localhost:4000/RSSN_Provider_Inventory/.

## Moving the repository

If the repo is renamed or transferred (for example to an RSSN organization), update `repository`, `url`, and `baseurl` in `_config.yml`, then turn on Pages again under **Settings → Pages**.
