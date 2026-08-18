#!/usr/bin/env python3
"""
Report shoot status from roster.csv.

Counting 50 rows by eye is where numbers go wrong, and the selection chase
depends on grouping people correctly rather than blasting everyone. This reads
roster.csv and reports attendance and selection state, grouped the way the
chase actually needs.

Standard library only. No pip install.

Usage:
    python3 status.py --roster roster.csv
    python3 status.py --roster roster.csv --chase
"""

import argparse
import csv
import sys
from pathlib import Path

CHASE_GROUPS = {
    "Not Opened": "Needs the gallery link again, not a reminder to decide.",
    "Gallery Sent": "Needs the gallery link again, not a reminder to decide.",
    "Opened No Pick": "Needs a tiebreaker. Offer an opinion, that moves it.",
}


def load(path):
    path = Path(path)
    if not path.exists():
        sys.exit(f"Roster not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if any((v or "").strip() for v in r.values())]
    return [{(k or "").strip().lower(): (v or "").strip() if not isinstance(v, list)
             else " ".join(v) for k, v in r.items()} for r in rows]


def tally(people, field):
    counts = {}
    for p in people:
        counts[p.get(field) or "(blank)"] = counts.get(p.get(field) or "(blank)", 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def main():
    ap = argparse.ArgumentParser(description="Report shoot status from roster.csv.")
    ap.add_argument("--roster", required=True)
    ap.add_argument("--chase", action="store_true",
                    help="Group outstanding selections for the chase")
    args = ap.parse_args()

    people = load(args.roster)
    total = len(people)
    print(f"Roster: {total} people\n")

    print("Attendance")
    for k, v in tally(people, "attendance").items():
        print(f"  {k}: {v}")

    photographed = sum(1 for p in people if p.get("attendance") == "Photographed")
    no_shows = [p["name"] for p in people if p.get("attendance") == "No Show"]
    if no_shows:
        print(f"\nRecapture list ({len(no_shows)}):")
        for n in no_shows:
            print(f"  - {n}")

    print("\nSelections")
    for k, v in tally(people, "selection_status").items():
        print(f"  {k}: {v}")

    selected = sum(1 for p in people if p.get("selection_status") == "Selected")
    if photographed:
        outstanding = photographed - selected
        print(f"\n{selected} of {photographed} photographed have selected. "
              f"{outstanding} outstanding.")

    if args.chase:
        na = sum(1 for p in people if p.get("selection_status") == "Not Applicable")
        if na and na == total:
            print("\nOn-site selection model: nothing to chase.")
            return
        print("\n--- Chase groups ---")
        any_found = False
        for state, guidance in CHASE_GROUPS.items():
            group = [p for p in people if p.get("selection_status") == state]
            if not group:
                continue
            any_found = True
            print(f"\n{state} ({len(group)}): {guidance}")
            for p in group:
                email = f" <{p['email']}>" if p.get("email") else " [CONFIRM: email]"
                print(f"  - {p['name']}{email}")
        if not any_found:
            print("\nNothing outstanding.")


if __name__ == "__main__":
    main()
