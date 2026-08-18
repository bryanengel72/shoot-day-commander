#!/usr/bin/env python3
"""
Build a corporate headshot day schedule from a roster CSV.

Deterministic slot math so the skill never eyeballs a timeline. Reads roster.csv,
applies setup time, per-person slots, recurring buffers, and an optional lunch,
then writes the slot times back into roster.csv and generates run-sheet.md and
shoot-day.md.

roster.csv is the single source of truth for the whole shoot. This script adds
slot_time and initializes the tracking columns; nothing else writes to it except
you and the skill.

Standard library only. No pip install.

Usage:
    python3 build_schedule.py --roster roster.csv --start 09:00 [options]
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path

INPUT_FIELDS = ["name", "department", "email", "notes"]
STATE_FIELDS = ["slot_time", "attendance", "selection_status", "selected_image"]
ALL_FIELDS = INPUT_FIELDS + STATE_FIELDS

# Lines that are never a person. Matched case-insensitively against the whole
# name cell, after stripping. Parsing happens upstream; this is the last net.
PLACEHOLDER_NAMES = {
    "tbd", "tba", "n/a", "na", "new hire", "unknown", "vacant",
    "open", "placeholder", "name", "-", "?",
}


def clean_cell(value):
    """Normalize one CSV cell. Ragged rows hand us a list, not a string."""
    if value is None:
        return ""
    if isinstance(value, list):
        # More fields than headers. Keep the content rather than crashing.
        return " ".join(str(v).strip() for v in value if v is not None).strip()
    return str(value).strip()


def load_roster(path):
    """Read roster.csv. Returns (people, blanks, ragged)."""
    path = Path(path)
    if not path.exists():
        sys.exit(f"Roster not found: {path}")

    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    people, blanks, placeholders, ragged = [], 0, [], []
    for i, raw in enumerate(rows, 1):
        row = {clean_cell(k).lower(): clean_cell(v) for k, v in raw.items()}

        # Content past the last header, usually an unquoted comma in a name or
        # note. Keep it rather than dropping it, and flag the row.
        overflow = row.pop("", "")
        if overflow:
            row["notes"] = " ".join(x for x in [row.get("notes", ""), overflow] if x)
            ragged.append(i)

        # A fully empty row is an export artifact, not a missing name.
        if not any(row.values()):
            blanks += 1
            continue

        name = row.get("name", "")
        if not name:
            sys.exit(
                f"Row {i} has data but no name: {row}\n"
                "Every roster row needs a real name. None are invented."
            )
        if name.lower() in PLACEHOLDER_NAMES:
            placeholders.append((i, name))
            continue

        person = {k: row.get(k, "") for k in ALL_FIELDS}
        person["name"] = name
        people.append(person)

    if placeholders:
        listed = ", ".join(f"row {i} '{n}'" for i, n in placeholders)
        sys.exit(
            f"Placeholder rows found and refused: {listed}\n"
            "These are not people. Get the real names, or drop the rows.\n"
            "Never schedule a slot against a placeholder."
        )
    if not people:
        sys.exit("Roster is empty.")
    return people, blanks, ragged


def group_by_department(people):
    """Keep departments contiguous, preserving first-seen department order."""
    order, groups = [], {}
    for p in people:
        dept = p["department"] or "(no department)"
        if dept not in groups:
            groups[dept] = []
            order.append(dept)
        groups[dept].append(p)
    return [p for dept in order for p in groups[dept]]


def find_duplicates(people):
    """Same name twice is sometimes two people and sometimes one mistake."""
    seen, dupes = {}, []
    for p in people:
        key = p["name"].lower()
        if key in seen:
            dupes.append(p["name"])
        seen[key] = True
    return sorted(set(dupes))


def build(people, start, per_person, buffer_minutes, buffer_every,
          setup, breakdown, lunch_after, lunch_minutes):
    """Walk the roster and assign each person a slot."""
    day_start = start - timedelta(minutes=setup)
    cursor = start
    slots, events = [], []

    events.append({
        "type": "setup",
        "label": "Photographer setup: rig, lighting, test frames",
        "start": day_start.strftime("%H:%M"),
        "end": start.strftime("%H:%M"),
        "minutes": setup,
    })

    since_lunch = 0
    lunch_taken = False
    total = len(people)

    for idx, person in enumerate(people, 1):
        # Lunch fires once, before the slot that would cross the threshold.
        lunch_due = (
            lunch_minutes and lunch_after and not lunch_taken
            and since_lunch >= lunch_after and idx <= total
        )
        if lunch_due:
            events.append({
                "type": "lunch",
                "label": "Lunch / reset",
                "start": cursor.strftime("%H:%M"),
                "end": (cursor + timedelta(minutes=lunch_minutes)).strftime("%H:%M"),
                "minutes": lunch_minutes,
            })
            cursor += timedelta(minutes=lunch_minutes)
            lunch_taken = True

        end = cursor + timedelta(minutes=per_person)
        person["slot_time"] = cursor.strftime("%H:%M")
        person["attendance"] = person["attendance"] or "Scheduled"
        slots.append({
            "position": idx,
            "name": person["name"],
            "department": person["department"],
            "email": person["email"],
            "notes": person["notes"],
            "start": cursor.strftime("%H:%M"),
            "end": end.strftime("%H:%M"),
        })
        cursor = end
        since_lunch += 1

        # Recurring buffer. Skipped after the last person, and skipped when
        # lunch is about to fire so the two never stack back to back.
        lunch_next = (
            lunch_minutes and lunch_after and not lunch_taken
            and since_lunch >= lunch_after
        )
        due = buffer_minutes and buffer_every and idx % buffer_every == 0
        if due and idx != total and not lunch_next:
            events.append({
                "type": "buffer",
                "label": f"Buffer (after {idx})",
                "start": cursor.strftime("%H:%M"),
                "end": (cursor + timedelta(minutes=buffer_minutes)).strftime("%H:%M"),
                "minutes": buffer_minutes,
            })
            cursor += timedelta(minutes=buffer_minutes)

    events.append({
        "type": "breakdown",
        "label": "Breakdown and pack-out",
        "start": cursor.strftime("%H:%M"),
        "end": (cursor + timedelta(minutes=breakdown)).strftime("%H:%M"),
        "minutes": breakdown,
    })

    summary = {
        "people": total,
        "arrive": day_start.strftime("%H:%M"),
        "first_person": start.strftime("%H:%M"),
        "last_person_ends": cursor.strftime("%H:%M"),
        "depart": (cursor + timedelta(minutes=breakdown)).strftime("%H:%M"),
        "shooting_hours": round((cursor - start).total_seconds() / 3600, 2),
        "total_hours": round(
            ((cursor + timedelta(minutes=breakdown)) - day_start).total_seconds() / 3600, 2),
    }
    return slots, events, summary


def write_roster(path, people):
    """Write roster.csv back with slot times and tracking columns."""
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ALL_FIELDS)
        w.writeheader()
        for p in people:
            w.writerow({k: p.get(k, "") for k in ALL_FIELDS})


def to_run_sheet(slots, events, summary, cfg, warnings):
    """Render the day-of run sheet with breaks interleaved in clock order."""
    rows = [{"sort": s["start"], "kind": "person", "data": s} for s in slots]
    rows += [{"sort": e["start"], "kind": "event", "data": e}
             for e in events if e["type"] in ("buffer", "lunch")]
    rows.sort(key=lambda r: r["sort"])

    header = cfg["title"] or "Shoot Day Run Sheet"
    L = [f"# {header}"]
    if cfg["date"]:
        L.append(f"\n**Date:** {cfg['date']}")
    if cfg["location"]:
        L.append(f"  \n**Location:** {cfg['location']}")
    if cfg["coordinator"]:
        L.append(f"  \n**Coordinator:** {cfg['coordinator']}")

    L.append(f"\n**{summary['people']} people** | Arrive **{summary['arrive']}** | "
             f"First person **{summary['first_person']}** | Wrap **{summary['depart']}**\n")
    L.append(f"Shooting time {summary['shooting_hours']} hrs | "
             f"Total on site {summary['total_hours']} hrs\n")
    L.append(f"Slot length {cfg['per_person']} min | "
             f"Buffer {cfg['buffer_minutes']} min every {cfg['buffer_every']} | "
             f"Setup {cfg['setup']} min | Breakdown {cfg['breakdown']} min\n")

    if warnings:
        L.append("\n> **Flags**")
        for w in warnings:
            L.append(f">  \n> {w}")
        L.append("")

    L.append("\n## Timeline\n")
    L.append("| Time | # | Name | Department | Notes |")
    L.append("|---|---|---|---|---|")
    first = events[0]
    L.append(f"| {first['start']}-{first['end']} | | **{first['label']}** | | |")
    for r in rows:
        d = r["data"]
        if r["kind"] == "person":
            L.append(f"| {d['start']}-{d['end']} | {d['position']} | {d['name']} | "
                     f"{d['department']} | {d['notes']} |")
        else:
            L.append(f"| {d['start']}-{d['end']} | | **{d['label']}** | | |")
    last = events[-1]
    L.append(f"| {last['start']}-{last['end']} | | **{last['label']}** | | |")

    L.append("\n## Check-in list\n")
    L.append("Tick each person off as they arrive. Mark no-shows in roster.csv "
             "(attendance = No Show) for the recapture list.\n")
    for s in slots:
        dept = f" ({s['department']})" if s["department"] else ""
        L.append(f"- [ ] {s['start']}  {s['name']}{dept}")

    return "\n".join(L) + "\n"


def to_day_sheet(summary, cfg, warnings):
    """The shoot header file. Human-editable, carries state between sessions."""
    L = ["# Shoot Day", ""]
    L.append(f"- **Client:** {cfg['title'] or '[CONFIRM: client company]'}")
    L.append(f"- **Date:** {cfg['date'] or '[CONFIRM: shoot date]'}")
    L.append(f"- **Location:** {cfg['location'] or '[CONFIRM: building and room]'}")
    L.append(f"- **Coordinator:** {cfg['coordinator'] or '[CONFIRM: name and email]'}")
    L.append(f"- **Status:** Scheduled")
    L.append(f"- **Selection model:** {cfg['selection_model'] or '[CONFIRM: on-site | gallery-after]'}")
    L.append("")
    L.append("## Schedule")
    L.append("")
    L.append(f"- Roster count: {summary['people']}")
    L.append(f"- Arrive: {summary['arrive']}")
    L.append(f"- First person: {summary['first_person']}")
    L.append(f"- Wrap: {summary['depart']}")
    L.append(f"- Shooting hours: {summary['shooting_hours']}")
    L.append(f"- Total on site: {summary['total_hours']}")
    L.append(f"- Per-person minutes (planned): {cfg['per_person']}")
    L.append("")
    L.append("## Close-out")
    L.append("")
    L.append("_Filled in at Workflow E._")
    L.append("")
    L.append("- Photographed: ")
    L.append("- No shows: ")
    L.append("- Selections received: ")
    L.append("- **Per-person minutes (actual):** ")
    L.append("- Delivery date: ")
    L.append("")
    if warnings:
        L.append("## Flags")
        L.append("")
        for w in warnings:
            L.append(f"- {w}")
        L.append("")
    return "\n".join(L)


def main():
    p = argparse.ArgumentParser(
        description="Build a headshot day schedule from roster.csv.")
    p.add_argument("--roster", required=True, help="Path to roster CSV")
    p.add_argument("--start", required=True, help="First person's slot time, HH:MM (24h)")
    p.add_argument("--verify-count", type=int, default=0,
                   help="Headcount the client stated. Refuses to build on a mismatch.")
    p.add_argument("--per-person", type=int, default=10, help="Minutes per person (default 10)")
    p.add_argument("--buffer-minutes", type=int, default=5, help="Buffer length (default 5)")
    p.add_argument("--buffer-every", type=int, default=5, help="Buffer every N people (default 5)")
    p.add_argument("--setup", type=int, default=30, help="Setup minutes (default 30)")
    p.add_argument("--breakdown", type=int, default=15, help="Breakdown minutes (default 15)")
    p.add_argument("--lunch-after", type=int, default=0, help="Lunch after N people (0 = none)")
    p.add_argument("--lunch-minutes", type=int, default=30, help="Lunch length (default 30)")
    p.add_argument("--by-department", action="store_true", help="Keep departments contiguous")
    p.add_argument("--title", default="", help="Client company, printed on the run sheet")
    p.add_argument("--date", default="", help="Shoot date, printed on the run sheet")
    p.add_argument("--location", default="", help="Building and room")
    p.add_argument("--coordinator", default="", help="Client-side coordinator")
    p.add_argument("--selection-model", default="", choices=["", "on-site", "gallery-after"])
    p.add_argument("--out-run-sheet", default="run-sheet.md")
    p.add_argument("--out-day-sheet", default="shoot-day.md")
    args = p.parse_args()

    try:
        start = datetime.strptime(args.start, "%H:%M")
    except ValueError:
        sys.exit(f"Bad --start '{args.start}'. Use 24-hour HH:MM, e.g. 09:00.")
    if args.per_person < 1:
        sys.exit("--per-person must be at least 1 minute.")

    people, blanks, ragged = load_roster(args.roster)

    # Count gate. The client's stated headcount is the check on the parse.
    if args.verify_count and args.verify_count != len(people):
        sys.exit(
            f"COUNT MISMATCH: client stated {args.verify_count}, roster has {len(people)}.\n"
            f"Difference of {abs(args.verify_count - len(people))}. Resolve before scheduling.\n"
            "Someone is missing from the list, or the stated count was wrong. "
            "Do not pad the roster to close the gap."
        )

    warnings = []
    if blanks:
        warnings.append(f"Skipped {blanks} blank row(s) in the roster file.")
    if ragged:
        warnings.append(
            f"Row(s) {', '.join(str(r) for r in ragged)} had more fields than headers, "
            "probably an unquoted comma. The extra text was appended to notes. "
            "Check those rows read correctly.")
    dupes = find_duplicates(people)
    if dupes:
        warnings.append(
            f"Duplicate name(s): {', '.join(dupes)}. Both are scheduled. "
            "Confirm whether these are two people or one entry twice.")
    if not args.verify_count:
        warnings.append(
            "Headcount not verified against a client-stated number "
            "(--verify-count was not used).")

    if args.by_department:
        people = group_by_department(people)

    slots, events, summary = build(
        people, start, args.per_person, args.buffer_minutes, args.buffer_every,
        args.setup, args.breakdown, args.lunch_after, args.lunch_minutes)

    if summary["total_hours"] > 8:
        warnings.append(
            f"Day runs {summary['total_hours']} hrs on site, past the 8 hour threshold. "
            "Offer the split-day option before delivering this schedule.")

    cfg = {
        "per_person": args.per_person,
        "buffer_minutes": args.buffer_minutes,
        "buffer_every": args.buffer_every,
        "setup": args.setup,
        "breakdown": args.breakdown,
        "title": args.title,
        "date": args.date,
        "location": args.location,
        "coordinator": args.coordinator,
        "selection_model": args.selection_model,
    }

    write_roster(args.roster, people)
    Path(args.out_run_sheet).write_text(
        to_run_sheet(slots, events, summary, cfg, warnings), encoding="utf-8")
    Path(args.out_day_sheet).write_text(
        to_day_sheet(summary, cfg, warnings), encoding="utf-8")

    print(f"{summary['people']} people scheduled.")
    print(f"Arrive {summary['arrive']}, first person {summary['first_person']}, "
          f"wrap {summary['depart']}.")
    print(f"Shooting {summary['shooting_hours']} hrs, "
          f"total on site {summary['total_hours']} hrs.")
    for w in warnings:
        print(f"FLAG: {w}")
    print(f"Updated {args.roster}. Wrote {args.out_run_sheet} and {args.out_day_sheet}.")


if __name__ == "__main__":
    main()
