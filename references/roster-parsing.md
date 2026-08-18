# Roster Parsing

The roster almost never arrives as a clean CSV. It arrives as a coordinator
pasting forty names into an email. Treat that as the normal case.

Claude does the parsing, not a script. Regex on human names loses immediately.
Claude reads the paste, produces `roster.csv`, and `build_schedule.py` does the
slot math. That split is deliberate: judgment where judgment is needed,
determinism where arithmetic is needed.

Parsing is also the one place in this skill where a person can quietly get
dropped or invented, which is exactly what the No-Fabrication Rule exists to
prevent. So the parse is checked mechanically, not by being careful.

## The count gate

Three numbers, reconciled out loud before anything gets scheduled:

1. **What the coordinator said.** "Attached are our 42 people."
2. **Lines that looked like names.**
3. **Rows written to roster.csv.**

When those disagree, that is the finding, not a rounding error. A coordinator
who says 42 and sends 39 lines has three people sitting in a different email,
and catching that now is worth more than anything else in this workflow.

Enforce it in code, not by remembering to check:

```
python3 scripts/build_schedule.py --roster roster.csv --start 09:00 --verify-count 42
```

The builder refuses on a mismatch and prints the gap. **Never close the gap by
padding the roster.** Go back to the coordinator.

If the coordinator never stated a count, the builder flags that the headcount is
unverified. Ask for the number rather than accepting the flag.

## Echo the parsed list back

Show the full list with its count and get a yes before scheduling. The full
list, not a summary. Forty names is cheap to display, and this is the last
moment where a missing person is still free to fix.

## What real email lists contain

Each of these has a right answer and a tempting wrong one.

**Annotations that are not part of the name.** `Jane Smith (out 9/14)`,
`Tom Reyes - remote`, `Priya Nair, joining late`. The parenthetical is roster
intelligence. It goes in `notes`. An annotation like "out 9/14" is a scheduling
flag and should surface before slots get assigned, not after.

**Placeholder rows.** `New Hire (starts 9/1)`, `TBD - Marketing`,
`+1 assistant`. These are real lines the client sent and they are not people.
The builder refuses them by design. They become `[CONFIRM: ...]` items back to
the photographer. Never fill a slot with a placeholder.

**Name order.** `Nair, Priya` and `Priya Nair` sometimes appear in the same
list. Normalize to first-last, and show the normalized form in the confirmation
so a wrong guess is visible rather than silent.

**Signature block contamination.** The coordinator's own name, title, phone, and
company footer sit directly below the list and read exactly like more roster
entries. So does "Sent from my iPhone." Strip them, and if the coordinator is
also being photographed, confirm rather than assume.

**Framing text.** "Here's everyone for Tuesday:", "Let me know if you need
anything else", "Thanks!" Easy to strip, easy to accidentally keep as a person.

**Duplicates.** People genuinely appear twice when a list is assembled from two
teams. The builder flags them and schedules both. Confirm rather than silently
deduplicating, because sometimes it really is two people with the same name.

**Titles and suffixes.** Dr., Jr., III. Keep them. They show up in delivered
file naming and in how someone expects to be addressed.

**Departments embedded in the line.** `Jane Smith - Legal`, `Tom Reyes (Ops)`.
That is `--by-department` grouping arriving for free. Pull it into the
`department` column rather than discarding it.

**Emails inline.** Often present. Capture them, they are needed for the prep
mail and the selection chase.

**Numbered or bulleted lists.** Strip the numbering. Watch for a list that skips
a number, which usually means a line was lost in a copy and paste.

## Other input shapes

**Screenshot or photo of a list.** Transcribe, then echo back with unusually
clear flagging of anything ambiguous. Names read off an image are the highest
risk input this skill takes.

**PDF or Word attachment.** Extract, then run the same count gate.

**An actual spreadsheet.** Best case. Still confirm the column meanings and run
the count gate, since a column headed "Name" occasionally holds "Lastname,
Firstname" or a mix.

**Email in the photographer's inbox.** If Gmail MCP is connected the
photographer can point at the message instead of pasting it. Same parse path,
same count gate. Pasting stays the default so the skill works with no
connectors at all.

## After the parse

Write `roster.csv` with whatever columns you have, minimum `name`. Report what
you found and what you could not resolve:

> Parsed 41 names from the paste. Dana said 42.
>
> One line I did not count as a person: "New Hire (starts 9/1)" in Marketing.
> That is likely the 42nd. [CONFIRM: do they have a name yet, or do we schedule
> 41 and add them later?]
>
> Two people flagged with notes: Jane Smith (out 9/14), Tom Reyes (remote).
> Jane will not be there on the shoot date, so she belongs on the recapture
> list rather than in a slot.
