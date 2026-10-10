# KAST setups

Steve Allen has provided me a file with the KAST setups for the Shane telescope over the past ~3 years.  We wish to examine that

## Data

The data file from Steve is `kastsetups` and is located in the `data/` folder.

## Prompts

1. Examine the data file.  See if you can figure out the structure.  I am going to ask you to generate figures and tables summarizing the most common setups used by our observers.  Before we do that, ask me questions about the data and what you think we should do in the Q&A section below.  Use Opus 5.  Log your work.

## Q&A

Questions from Claude (prompt #1). My proposed default is shown in *italics*
after each question. Please answer inline and I will proceed from there.

### A. What a row represents

**Q1.** Is each row one observing *request* (one proposal / one run), or one
*night*? I.e., if a program gets 3 nights, does it appear once or three times?
This decides whether "most common" means "most requested by programs" or "most
nights on sky". *Default: treat each row as one request and count requests.*
>A. I think it is one run, but let's not worry about that 

**Q2.** There are no dates, program IDs, PI names, or semesters in the file
(only a few dates embedded in `ADD:` notes, 2023-08 to 2026-08). Can Steve
provide those columns (at minimum a date or semester, plus a request/program
ID)? That would enable trends over time and correct handling of `ADD:` rows.
*Default: proceed without time information; no time-trend figures.*

>A. I have received a new file from Steve with more info.

**Q3.** Is the row order meaningful (chronological)? It *looks* roughly
chronological from the embedded dates, but not strictly (e.g., a 2024-11-01
note appears after 2026-02-12). *Default: assume order is not reliable.*

>A. I think it is chronological

### B. The `ADD:` and `IGNORE:` rows (43 of ~155 rows)

**Q4.** I interpret an `ADD:` row as an amendment to the *preceding* request
(a later update from the observer), not a new request. Is that right? If so, I
would:
- merge a full `ADD: Gr: ...; Dich: ...` into the preceding setup (replacing
  it), and
- apply an `ADD: Blue X = ...` note only to the BlueX value of the preceding
  setup.

Some `ADD:` rows follow other `ADD:` rows (chains of updates), which fits this
reading. *Default: yes, amendments that replace the prior row's values.*

>A. Yes, that is fine

**Q5.** `IGNORE:` (1 row) — drop it entirely? *Default: drop.*

>A. Yes, ignore

### C. Parsing / normalization

**Q6.** The grating list (e.g. `gr6 300/7500, gr1 600/5000, gMirror`) — is
this the set of gratings the observer wants *loaded* in the instrument (i.e.,
the grating turret/slots for the night), not a single configuration used? I
ask because many rows list 3–4 gratings, and red-side vs. blue-side gratings
are mixed in one list. My understanding of Kast:
- **Blue arm grisms:** 600/4310, 452/3306, 830/3460 (not present in this file!)
- **Red arm gratings:** 300/7500, 600/5000, 600/7500, 830/8460, 1200/5000, 300/4320 (gr5)

So `gr1..gr6` would all be red-side gratings, and the blue grism is simply not
recorded. Is that correct? If the blue grism choice is not captured, we should
state that clearly in any summary. *Default: treat Gr list as red-side
gratings requested to be mounted.*

**Q7.** `gMirror` in the grating list and `mirror` in the dichroic list — I
assume these mean "a flat mirror installed instead of a grating/dichroic"
(e.g., for imaging/acquisition, or a blue-only / red-only mode). Correct?
Should these be counted as a "setup" or excluded from grating/dichroic
statistics? *Default: count them, but flag them as non-dispersive.*

**Q8.** Dichroics d46, d55, d57 — I assume these are the 4600 Å, 5500 Å, and
5700 Å dichroics. Multiple dichroics in one row = both requested to be loaded
(e.g., switching during the night). OK? *Default: yes.*

**Q9.** Grating order in a row varies (`gr6, gr4, gr2` vs `gr2, gr4, gr6`),
which looks like a form change rather than a preference. Should I treat the
grating set as unordered? *Default: unordered set.*

**Q10.** There's one typo, `g66 300/7500` (in an `ADD:` row) and one
`gr6 300/75000`. Normalize both to `gr6 300/7500`? *Default: yes.*

**Q11.** `polarWheel` vs `User filter wheel` — is this a useful dimension to
report (105 vs. 5 requests)? *Default: report as a one-line statistic only.*

### D. BlueX

**Q12.** BlueX (blue camera x-stage / focus position?) takes many values
(6.25–16.9 mm, plus RedX/RedY/BlueY 0 or 10). What is it physically, and is it
tied to the grism choice (so it could stand in for the missing blue grism)? Do
you want it analyzed at all? *Default: histogram of BlueX values only, with a
note that 24 of the 110 standard rows (~22%) don't specify it.*

### E. What to produce

**Q13.** Which "setup" definition do you want tables for? Options:
1. Individual gratings (frequency of each grating being requested).
2. Individual dichroics.
3. Full combination (grating set + dichroic set) — 32 distinct combinations.
4. "Science configuration" pairs (grating × dichroic), expanding each row
   into all pairs.
*Default: 1, 2, and 3, plus a grating×dichroic co-occurrence heatmap.*

**Q14.** Output format and location: PNG figures + Markdown (or CSV/LaTeX)
tables in a new `kast/` directory, generated by a script in
`shane_telescope/`? Should I also write a parser module (e.g.
`shane_telescope/io/kast_setups.py`) returning a pandas DataFrame? *Default:
yes to both; figures in `kast/`.*

**Q15.** Audience — is this for Lick/Shane staff (e.g., to decide which
gratings stay permanently mounted) or for the PypeIt team (e.g., to prioritize
which setups get archived arc solutions / templates)? This affects emphasis.
*Default: PypeIt team — emphasize which grating/dichroic combos need
wavelength-calibration support.*

## Logging

The "Logs" section will record Claude's work.  Please use the following format:

### <Date> (Short summary of the work)

<Detailed description of the work and what you learned>

...

## Logs

### 2026-09-23 (Prompt #1: examined `kastsetups` structure; posed questions)

Examined `shane_telescope/data/kastsetups` (11.9 kB). It is a PostgreSQL
`psql` text dump of a single column named `text`: a header line, a dashed
separator, 157 rows, and a `(157 rows)` footer. One entry is a multi-line value
(embedded `\r` + `+` continuation markers), so there are ~155 logical entries.

Entry types:
- **110 standard rows**: `Gr: <list>; Dich: <list>; <wheel>.; [BlueX ...]; [free-text note]`
- **43 `ADD:` rows**: amendments, either a full new setup string (with
  slightly different formatting, e.g. `Dich: d57.` or `Dich d46, d57`) or
  just a BlueX update, sometimes with an `Updated: <date>` stamp. Dates span
  2023-08-14 to 2026-08-15, in several formats (ISO, MM/DD/YYYY, MM-DD-YYYY).
- **1 `IGNORE:` row.**
- **~3 rows with no `Gr:` field** (twilight observations, on-sky testing).

Fields in standard rows:
- Gratings: `gr1 600/5000`, `gr2 600/7500`, `gr3 830/8460`, `gr4 1200/5000`,
  `gr5 300/4320`, `gr6 300/7500`, `gMirror`. Order varies across rows
  (the later part of the file lists them in sorted order — likely a form change).
- Dichroics: `d46`, `d55`, `d57`, `mirror`.
- Filter wheel: `polarWheel` (105) or `User filter wheel` (5).
- Optional BlueX (6.25–16.9 mm, inconsistent units/format: `7.6`, `7.6 mm`,
  `+9.6mm`, `11`), occasionally with RedX/RedY/BlueY.
- Optional free-text notes (e.g., personnel/training info).

Preliminary tallies over the 110 standard rows (raw, no `ADD:` merging):
- Gratings: gr2 67, gr4 61, gr6 59, gr1 29, gMirror 24, gr3 13, gr5 3.
- Dichroics: d57 86, d55 24, mirror 23, d46 21.
- 32 distinct (grating set, dichroic set) combinations. Top: gr2/d57 (12);
  gr1+gr6+gMirror/d57+mirror (9); gr2+gr4+gr6/d57 (9); gr2/d55 (9);
  gr1+gr4+gr6/d57 (7); gr2+gr4+gr6/d46+d57 (7).

Key limitations learned: no dates/program IDs per row, the blue-side grism is
not recorded, and `ADD:` rows must be associated with a parent row (assumed:
the preceding one). Posted 15 questions in the Q&A section; no code or figures
written yet, pending answers.