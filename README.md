# Shoot Day Commander

A Claude Skill that runs a corporate team headshot day end to end: builds the
schedule, drafts the communications, produces the day-of run sheet, and chases
image selections afterward.

Built for the 15 to 50 person on-location shoot, the kind where a five minute
scheduling error compounds into the last person being forty minutes late, and
where tracking down final picks from forty people becomes its own
administrative job.

**No database. No connectors. No pip install.** State lives in a CSV and two
Markdown files the photographer owns.

## Install

```bash
git clone https://github.com/YOURNAME/shoot-day-commander.git
cp -r shoot-day-commander ~/.claude/skills/
```

Or download the ZIP and unpack it into `~/.claude/skills/`.

Requires Python 3.8+ (standard library only). Nothing else.

## Try it in thirty seconds

```bash
cd examples
python3 ../scripts/build_schedule.py --roster roster-sample.csv --start 09:00 \
  --verify-count 9 --by-department --title "Meridian Law" --date 2026-09-14
```

That writes a run sheet and a shoot day file. Compare against
`run-sheet-sample.md` to see what a finished one looks like.

`attendee-email-sample.txt` is what a roster actually looks like when it
arrives: a coordinator's plain-text email with a signature block, a placeholder
row, a duplicate, and a stated headcount that does not match the list. Hand it
to Claude and ask it to plan a shoot day.

## Setup

Open `SKILL.md` and fill in the `client` and `outreach` blocks in the
frontmatter. Two values matter more than the rest:

- **`per_person_minutes`** decides the length of the entire day. Working
  photographers genuinely disagree on it, anywhere from 5 to 15 minutes.
  Confirm your real pace rather than accepting the default.
- **`selection_model`** is either `on-site` or `gallery-after`, and it changes
  the whole post-shoot workflow. Under `on-site` there is nothing to chase.

That is the whole setup. There is no database to build.

## How state works

One folder per shoot:

```
shoots/meridian-law-2026-09-14/
├── roster.csv      ← source of truth, one row per person
├── shoot-day.md    ← header and close-out numbers
└── run-sheet.md    ← generated, print it or pull it up on your phone
```

`roster.csv` starts as names from the client and gains `slot_time`,
`attendance`, `selection_status`, and `selected_image` as the shoot progresses.
Open it in Excel, Numbers, or Sheets and edit it by hand any time.

If you run Claude on a machine with a writable disk, these persist on their
own. In a plain chat they do not, so download `roster.csv` and `shoot-day.md`
at the end of a session and upload them at the start of the next.

## Two guarantees the skill enforces

**Nothing is sent.** Every employee-facing message is drafted and handed to you.
These go to dozens of people inside a client's company and a mistake lands on
your relationship with that client. Draft, review, send it yourself.

**Nobody is invented.** The builder refuses a row with no name, refuses a
placeholder row like "TBD" or "New Hire," flags duplicates, and refuses to build
at all when the client's stated headcount does not match the roster you parsed.
That last check catches the most common real failure: a coordinator says 42 and
sends 39, and three people are sitting in a different email.

## Scripts

| Script | What it does |
|---|---|
| `scripts/build_schedule.py` | Roster to schedule. Setup time, per-person slots, recurring buffers, optional lunch, breakdown. Writes slot times back to `roster.csv`, generates the run sheet and shoot day file, flags any day over 8 hours on site. |
| `scripts/status.py` | Attendance counts, recapture list, and selection status from `roster.csv`. `--chase` groups outstanding selections by what each person actually needs. |

Both take `--help`.

## Optional connectors

None are required.

- **Gmail** stages approved drafts in your own drafts folder. It never sends.
- **Google Drive or Notion** can mirror `roster.csv` into a live view your
  client coordinator can watch. Mirror one direction only, outward from the
  CSV. Two sources of truth is how a roster ends up wrong.

## A note on client data

`roster.csv` contains the names and email addresses of a client company's
employees. The bundled `.gitignore` excludes `shoots/`, `roster*.csv`,
`run-sheet*.md`, and `shoot-day*.md` for exactly that reason. If you fork this
for your own use, keep those rules. `LEARNINGS.md` also becomes client data once
you have run a real shoot through it.

## License

MIT. See [LICENSE](LICENSE).
