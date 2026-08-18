---
name: shoot-day-commander
description: "Runs a corporate headshot day end to end: turns a roster into a timed schedule, drafts prep emails and the run sheet, then chases image selections. Use for shoot day planning, rosters, run sheets."
compatibility: >
  No connectors required. Python 3 (standard library only, no pip install) for the two bundled
  scripts. State lives in plain CSV and Markdown files the photographer owns. Gmail MCP is
  optional, used only to stage approved drafts in the photographer's own drafts folder, never
  to send. Employee-facing mail is always draft-only. Google Drive or Notion MCP are optional
  one-way mirrors if the photographer wants a live view for the client coordinator.
metadata:
  client:
    status: not yet configured
    photographer: "{{PHOTOGRAPHER}}"
    business_name: "{{BUSINESS_NAME}}"
    per_person_minutes: 10
    buffer_minutes: 5
    buffer_every: 5
    setup_minutes: 30
    breakdown_minutes: 15
    selection_model: "{{on-site | gallery-after}}"
    note: >
      per_person_minutes is the single most important number here and photographers genuinely
      disagree on it, see references/scheduling.md. Confirm the photographer's real pace during
      setup rather than assuming the default. selection_model changes the entire post-shoot
      workflow, so it must be set before the first shoot.
  storage:
    status: configured
    backend: csv
    shoots_dir: "shoots/"
    folder_pattern: "client-slug-YYYY-MM-DD"
    note: >
      One folder per shoot holding roster.csv, shoot-day.md, and run-sheet.md. Schema in
      references/state-schema.md. No database. roster.csv is the single source of truth for
      per-person state; anything else is generated or mirrored from it.
  outreach:
    status: not yet configured
    sender_name: "{{SENDER_NAME}}"
    send_channel: draft-only
    note: >
      draft-only is not negotiable by default. Employee-facing mail can go to dozens of people
      at a client company, and a mistake there lands on the photographer's relationship, not
      ours. Draft, show, hand over. Do not change this without the photographer explicitly
      saying so.
---

# Shoot Day Commander Skill

Runs a corporate team headshot day end to end: schedule, communications, day-of execution, and
the selection chase afterward. Built for the on-location team shoot, the 15 to 50 person kind
where small scheduling errors cascade and where tracking down final image picks from 40 people
becomes its own administrative job.

**This is a template.** Clone the folder per client, rename it, and fill in the `client` and
`outreach` blocks under `metadata` before first use. Any block still marked `not yet
configured` means setup is incomplete: run the setup steps below rather than planning a shoot
with guessed values.

> **Read [references/state-schema.md](references/state-schema.md) first, every time.** It
> defines the three files that hold a shoot and how to read them back in a fresh session.
>
> **Read [LEARNINGS.md](LEARNINGS.md) first, every time, too.** It holds what this skill has
> learned from real shoot days, above all the photographer's true pace once actual shoots have
> been run. A measured pace from a real day always beats the configured default.
>
> **Precedence when things disagree:** a measured pace in LEARNINGS.md wins over the configured
> default. The frontmatter config wins on everything else about this business.
> state-schema.md wins on file structure. Flag conflicts rather than silently picking one.

---

## Setup (once per photographer)

1. Fill in the `client` and `outreach` blocks under `metadata`. Confirm `per_person_minutes`
   and `selection_model` with the photographer directly, do not assume the defaults, both
   change the output substantially.
2. Create the `shoots/` directory. Nothing else to build. There is no database.
3. Confirm where the photographer works. On a machine with a writable disk the shoot files
   persist on their own. In a plain chat they do not, and the photographer has to download the
   files at the end of a session and upload them at the start of the next. Say this once,
   plainly, at setup.

---

## Workflow A: Plan the shoot day

Trigger phrases: "plan a shoot day", "build the schedule", "I have a roster", "here's the
attendee list", "corporate headshot day", "team shoot logistics".

1. Capture from the photographer: client company, shoot date, arrival time or desired first
   slot, location, on-site coordinator name and contact, and the roster. Never invent a name, a
   headcount, or a room.
2. **Check the space before scheduling anything.** Read
   [references/scheduling.md](references/scheduling.md) §Space. If the room dimensions or power
   access are unknown, ask. A shoot planned into a room that cannot hold the setup is a wasted
   day, and this is the cheapest possible moment to catch it.
3. Confirm the pace. If LEARNINGS.md has a measured pace from previous real shoots, use it and
   say so. Otherwise use `client.per_person_minutes` and flag that it is unverified.
4. **Parse the roster.** Read [references/roster-parsing.md](references/roster-parsing.md)
   before touching a pasted list. The roster usually arrives as plain text in an email, and
   parsing is where a person quietly gets dropped or invented. Write `roster.csv` with at
   minimum a `name` column, plus `department`, `email`, `notes` where known.
5. **Run the count gate.** Reconcile the coordinator's stated headcount against the rows you
   wrote, echo the full parsed list back, and get a yes before scheduling. Never pad a roster
   to close a gap and never invent a name to fill a slot.
6. Run the schedule builder, passing the confirmed headcount so the check is enforced in code:
   ```
   python3 scripts/build_schedule.py --roster roster.csv --start 09:00 --verify-count 42 \
     --per-person 10 --buffer-minutes 5 --buffer-every 5 \
     --setup 30 --breakdown 15 --by-department \
     --title "Meridian Law" --date 2026-09-14 \
     --location "HQ, Conf Room B" --coordinator "Dana Reyes" \
     --selection-model gallery-after
   ```
   Add `--lunch-after N --lunch-minutes 30` for any day long enough to need one. The builder
   updates roster.csv in place and writes run-sheet.md and shoot-day.md.
7. **Read the flags.** The builder prints every flag it raised and repeats them in both output
   files. If the day runs past 8 hours on site, surface that immediately and offer the
   split-day option before going further. Do not quietly hand over a twelve hour schedule.
8. Deliver the schedule summary and the run sheet. State the arrival time, first slot, wrap
   time, and total hours plainly. If the photographer is in a plain chat with no persistent
   disk, hand over roster.csv and shoot-day.md and tell them to keep both for next session.

---

## Workflow B: Draft the communications

Trigger phrases: "prep email for the team", "send the reminders", "what do I send the client".

Read [references/comms-templates.md](references/comms-templates.md). Three messages, each
drafted, never sent:

1. **Coordinator brief** to the client contact, covering the division of responsibility, space
   and power requirements, and what the photographer needs on arrival.
2. **Employee prep email**, roughly a week ahead: wardrobe, grooming timing, backup outfit, and
   each person's specific slot from `roster.csv`. A named time beats "sometime Tuesday morning"
   every time.
3. **48-hour reminder**, short: time, room, and a line that the session itself only takes a few
   minutes. That line measurably reduces no-shows, nervousness is a real cause of them.

Every draft goes to the photographer for approval. Employee-facing mail is never sent from this
skill, regardless of how the request is phrased. Offer `Gmail:create_draft` to stage it in the
photographer's own drafts if they want it there. Set `Status: Comms Sent` in shoot-day.md only
once the photographer confirms they actually sent them.

---

## Workflow C: Day-of

Trigger phrases: "run sheet", "day of", "who's next", "mark a no-show".

1. Deliver run-sheet.md from Workflow A: timeline with breaks interleaved, plus the check-in
   list.
2. Track arrivals against roster.csv as the photographer reports them. Set `attendance` to
   `Photographed` or `No Show`. No-shows become the recapture list, not a loss.
3. Run `python3 scripts/status.py --roster roster.csv` for live counts rather than counting
   rows by eye.
4. If the day slips, recalculate honestly. Re-run the builder against the people who remain
   with a new start time rather than pretending the original schedule still holds.

---

## Workflow D: Chase selections

Trigger phrases: "who hasn't picked their headshot", "chase selections", "selection status".

This workflow only applies when `client.selection_model` is `gallery-after`. Under `on-site`,
selections are captured during the shoot and there is nothing to chase, say so rather than
inventing a chase list.

1. Run `python3 scripts/status.py --roster roster.csv --chase`. It groups everyone outstanding
   into never opened the gallery, opened but did not pick, and already picked.
2. Those three need different nudges. A person who has not opened anything needs the link
   again, not a reminder to decide. See
   [references/selection-tracking.md](references/selection-tracking.md).
3. Draft one short nudge per outstanding person, plus a single summary for the client
   coordinator listing who is outstanding. The coordinator summary usually does more work than
   the individual nudges.
4. Approval gate, then update `selection_status` in roster.csv. Never send.

---

## Workflow E: Close out

Trigger phrases: "close out the shoot", "shoot day report".

Fill in the close-out block in shoot-day.md: final counts photographed, no-shows, selections
received, delivery date, status `Closed`. Use `status.py` for the counts.

Then record in LEARNINGS.md the one number that improves every future shoot: **actual minutes
per person**, measured as shooting time divided by people photographed. Compare it to the
configured pace and note the gap. This is the single highest-value thing this skill learns,
after two or three real shoots the schedule stops being an estimate.

Also flag any no-show list that never got a recapture session, that is the quiet failure mode
here, people the client paid to have photographed who still have no headshot.

---

## No-Fabrication Rule

Never invent a person, a headcount, a room dimension, or a slot. Every name comes from the
client's real roster; the builder refuses a nameless row and refuses a placeholder row for
exactly this reason. Never close a count gap by padding. Never state a pace as measured when it
is the unverified default. Use `[CONFIRM: ...]` for anything not known.

---

## Error Handling

| Error | Response |
|---|---|
| Config block still `not yet configured` | Stop and ask. Do not guess client details. |
| `per_person_minutes` never confirmed | Use the default but flag it plainly as unverified. Do not present an unverified pace as fact. |
| `selection_model` not set | Stop before Workflow D. The whole post-shoot flow depends on it. |
| Roster arrives as pasted email text | Normal case, not an edge case. Read roster-parsing.md, parse, echo the full list back, run the count gate. |
| Roster arrives as a photo, screenshot, or PDF | Transcribe, then flag ambiguous names unusually clearly. Names read off an image are the riskiest input here. |
| Coordinator's stated count does not match parsed rows | Stop. Report the gap and the likely cause. Never pad the roster to close it. |
| Coordinator never stated a count | Ask for it. Do not accept the builder's unverified flag as good enough. |
| Roster row has data but no name | The builder refuses by design. Get the real name, never fill it in. |
| Placeholder row ("TBD", "New Hire") | The builder refuses it. Surface as `[CONFIRM: ...]`, never schedule a slot against it. |
| Duplicate name in the roster | The builder flags it and schedules both. Confirm whether it is two people or one entry twice. |
| Room size or power access unknown | Ask before scheduling. Flag it as a blocking unknown, not a detail. |
| Room is smaller than the setup needs | Say so directly and early. Offer alternatives (different room, lobby, split setup) rather than scheduling into a space that will not work. |
| Day runs past 8 hours on site | The builder flags it. Surface it and offer the split-day option before delivering the schedule. |
| Client adds people after the schedule is built | Add rows to roster.csv and re-run the builder rather than hand-patching slots. Hand-patched schedules drift. |
| Day is running late | Re-run against remaining people with a real new start time. Do not pretend the original holds. |
| No-shows on the day | Set `attendance` to `No Show`, build a recapture list. Never quietly drop them. |
| Photographer wants employee mail sent directly | Never send. Offer a Gmail draft and say plainly this skill drafts only. |
| roster.csv missing at the start of a session | In a plain chat this is expected between sessions. Ask the photographer to upload it. Never reconstruct a roster from memory or from earlier in the conversation. |
| Selection chase requested under `on-site` model | Say there is nothing to chase. Do not invent a list. |

---

## Full Workflow Checklist

- [ ] Config blocks filled in, none marked `not yet configured`
- [ ] Shoot folder created, named `client-slug-YYYY-MM-DD`
- [ ] LEARNINGS.md read, measured pace applied if one exists
- [ ] Space checked: dimensions, power, waiting area, before scheduling
- [ ] Pace confirmed with the photographer, or flagged as unverified
- [ ] Roster parsed, full list echoed back, count gate run and reconciled
- [ ] Schedule built with the script and `--verify-count`, never eyeballed
- [ ] Every builder flag read and surfaced, split-day offered if over 8 hours
- [ ] roster.csv, shoot-day.md, run-sheet.md all written
- [ ] Coordinator brief drafted
- [ ] Employee prep email drafted with individual slots
- [ ] 48-hour reminder drafted
- [ ] Approval gate run before anything is staged or logged as sent
- [ ] Run sheet and check-in list delivered
- [ ] Files handed over for re-upload if the photographer has no persistent disk
- [ ] No-shows marked, recapture list built
- [ ] Selections chased (gallery-after only) or captured on site
- [ ] Shoot closed out, actual minutes per person measured into LEARNINGS.md

---

## Reference Files

| File | When to Read |
|---|---|
| [references/state-schema.md](references/state-schema.md) | Read first, every time. The three files per shoot, their columns, and how to read state back in a fresh session. |
| [LEARNINGS.md](LEARNINGS.md) | Read first, every time (apply the measured pace) and last (record the new one). Starts empty in a fresh clone. |
| [references/roster-parsing.md](references/roster-parsing.md) | Read at Workflow A before parsing any roster. Pasted email lists, the count gate, and everything that looks like a name but is not. |
| [references/scheduling.md](references/scheduling.md) | Read at Workflow A before building any schedule. Pace, the disagreement between sources, space requirements, buffers, and the split-day threshold. |
| [references/comms-templates.md](references/comms-templates.md) | Read before Workflow B. Coordinator brief, employee prep email, and 48-hour reminder, plus the no-send rule. |
| [references/selection-tracking.md](references/selection-tracking.md) | Read before Workflow D. The two selection models and how the chase differs between them. |

## Bundled Scripts

Standard library only. No pip install, no virtualenv.

| Script | Purpose |
|---|---|
| `scripts/build_schedule.py` | Turns roster.csv into slots with setup, buffers, optional lunch, and breakdown. Writes slot times back into roster.csv and generates run-sheet.md and shoot-day.md. Enforces the count gate with `--verify-count`, refuses nameless and placeholder rows, and flags duplicates and any day over 8 hours. `--help` lists all options. |
| `scripts/status.py` | Reads roster.csv and reports attendance, the recapture list, and selection counts. `--chase` groups outstanding selections into never-opened and opened-no-pick, which need different messages. Use it rather than counting rows by eye. |
