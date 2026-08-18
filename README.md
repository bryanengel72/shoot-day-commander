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

You do not need to know how to code, and you do not need to open a terminal.
Downloading this is three clicks and a copy-paste.

### Step 1 — Download the ZIP

At the top of this page there is a big blue button that says **`<> Code`**.

1. Click **`<> Code`**.
2. In the little menu that drops down, click **Download ZIP** (it is the last
   item, at the bottom).
3. The file lands in your **Downloads** folder as
   `shoot-day-commander-main.zip`.

Do not click the green "Open with GitHub Desktop" or any of the `git` links.
You want **Download ZIP** and nothing else.

### Step 2 — Unzip it and fix the folder name

Double-click the ZIP. You get a folder called **`shoot-day-commander-main`**.

Rename that folder to **`shoot-day-commander`** — delete the `-main` off the
end. This matters. Claude looks for the folder by name.

### Step 3 — Drop it into your Claude skills folder

Claude keeps skills in a hidden folder called `.claude/skills` inside your home
folder. Here is how to get there without a terminal.

**On a Mac**

1. Open **Finder**.
2. In the menu bar at the top, click **Go**, then **Go to Folder...**
   (or press `Shift` + `Command` + `G`).
3. Type this exactly and press Return:

   ```
   ~/.claude/skills
   ```

4. Drag your `shoot-day-commander` folder into the window that opens.

If step 3 says the folder does not exist, go to `~/.claude` instead, then make
a new folder inside it named `skills` (all lowercase), and drag
`shoot-day-commander` into that.

**On Windows**

1. Open **File Explorer**.
2. Click the address bar at the top, type this exactly, and press Enter:

   ```
   %USERPROFILE%\.claude\skills
   ```

3. Drag your `shoot-day-commander` folder into the window that opens.

If that folder does not exist, go to `%USERPROFILE%\.claude`, create a new
folder named `skills`, and drag `shoot-day-commander` into that.

### Step 4 — Check that it worked

You should end up with this, and the `SKILL.md` file needs to be sitting right
inside `shoot-day-commander` — not one folder deeper:

```
.claude/skills/shoot-day-commander/SKILL.md
```

A common mix-up: unzipping sometimes gives you a folder inside a folder, so you
get `shoot-day-commander/shoot-day-commander/SKILL.md`. If that happened, drag
the inner folder out and delete the empty outer one.

Now quit Claude and open it again. Ask it:

> Do you have the Shoot Day Commander skill?

If it says yes, you are done.

### If it does not show up

- **Check the folder name.** It has to be `shoot-day-commander` exactly, all
  lowercase, with the hyphens. Not `shoot-day-commander-main`, not
  `Shoot Day Commander`.
- **Check for a folder inside a folder.** See Step 4 above.
- **Restart Claude.** It only looks for new skills when it starts up.

### Already comfortable with a terminal?

```bash
git clone https://github.com/bryanengel72/shoot-day-commander.git
cp -r shoot-day-commander ~/.claude/skills/
```

### What you need on your computer

Python 3.8 or newer, and nothing else — no libraries to install, no accounts to
create. Python is already on every Mac. On Windows, if Claude tells you Python
is missing, get it from [python.org/downloads](https://www.python.org/downloads/)
and tick **"Add Python to PATH"** on the first screen of the installer.

## Try it in thirty seconds

Just talk to Claude. Open Claude, and type:

> Plan a headshot day using the sample roster in the Shoot Day Commander
> examples folder. Start at 9am, 9 people, group by department, for Meridian
> Law on September 14 2026.

Claude runs the scheduler for you and hands back a run sheet. Compare it to
`examples/run-sheet-sample.md` to see what a finished one looks like.

Then try the harder one. `examples/attendee-email-sample.txt` is what a roster
actually looks like when it arrives: a coordinator's plain-text email with a
signature block, a placeholder row, a duplicate, and a stated headcount that
does not match the list. Point Claude at it and ask it to plan a shoot day —
watch it catch the problems before you are standing in a lobby with a missing
person.

If you would rather run it yourself from a terminal:

```bash
cd examples
python3 ../scripts/build_schedule.py --roster roster-sample.csv --start 09:00 \
  --verify-count 9 --by-department --title "Meridian Law" --date 2026-09-14
```

## Setup

Ask Claude to do it:

> Open the Shoot Day Commander SKILL.md and walk me through filling in my
> studio details.

Or open `SKILL.md` yourself in any text editor and fill in the `client` and
`outreach` blocks at the top of the file. Two values matter more than the rest:

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
