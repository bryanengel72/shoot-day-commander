# Selection Tracking

## Two models, and why it must be decided before the shoot

How employees pick their final image changes the entire post-shoot workflow. It has to be set in
`client.selection_model` before Workflow D runs.

### On-site selection

People review their frames at a digital workstation right after their session and pick before
they leave. Often an assistant runs the workstation while the photographer keeps shooting.

Consequence: **there is nothing to chase.** The photographer knows exactly which frame to
retouch per person, delivery gets faster, and the follow-up email chain never happens. Under
this model, Workflow D should say there is nothing outstanding rather than inventing a chase
list. Roster rows carry `Selection Status = Not Applicable`.

The cost is on the day itself: it needs the space, the gear, and usually a second person.

### Gallery-after

Individual galleries go out after the session and people pick in their own time.

This works cleanly for small teams, roughly under 10 people. Past that it becomes its own
administrative job: dozens of gallery links to coordinate, reminders to send, and selections to
track down from people who have a day job. This is the exact pain Workflow D exists to absorb.

## Why the chase groups people

Three states, three different messages. Collapsing them into one "have you picked yet" blast is
the thing that makes selection chasing feel like nagging:

| State | What they actually need |
|---|---|
| Never opened the gallery | The link again. They may not have seen it, it may be in spam, it may be buried. A reminder to decide is useless to someone who has not looked. |
| Opened, no pick | A tiebreaker. They looked and stalled, which usually means they cannot choose between two. Offering an opinion moves this faster than another reminder. |
| Selected | Nothing. Do not include them in any nudge. |

## The coordinator summary usually outperforms individual nudges

A single message to the client coordinator listing who is outstanding tends to move more people
than a second round of individual emails. It is internal, it comes from a colleague rather than
a vendor, and the coordinator generally wants the project finished too.

Send both, but expect the summary to be what actually closes it out.

## What to record

Per person: `Selection Status`, and `Selected Image` once they pick. At close-out, the shoot day
row records how many selections came in against how many people were photographed. A shoot that
sits at `Selections Open` for weeks with a handful outstanding is worth flagging, it is
unfinished work and unfinished delivery.
