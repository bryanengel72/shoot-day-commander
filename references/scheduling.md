# Scheduling a Corporate Headshot Day

## Pace: the number everything else depends on

Working photographers genuinely disagree on minutes per person, and the range is wide enough to
change a day's length by hours. Two published positions, both from photographers who run these
shoots regularly:

- **10 to 15 minutes** per person, covering wardrobe check on arrival, getting settled, a few
  poses, three or four distinct looks, and dismissal.
- **5 to 10 minutes**, with the argument that 5 minute back-to-back slots are the sweet spot
  and that blocks longer than 10 minutes let the day sag.

Both are real practice, not one being wrong. The difference usually comes down to whether the
photographer shoots tethered with an assistant handling flow, and whether selections happen on
site.

**So: never present a default as if it were measured.** Confirm the photographer's actual pace
during setup. After a real shoot, Workflow E measures it (shooting time divided by people
photographed) and writes it to LEARNINGS.md, which then outranks the configured default. After
two or three shoots the schedule stops being a guess.

## Buffers, and why published team-size tables run short

A widely cited team-size table gives roughly: 5 people 2 hours, 10 people 3 hours, 25 people 6
hours, 50 people a full day at about 8.5 hours.

Those numbers assume flat per-person time with no recovery built in. Once buffers and a lunch
are included, a 50 person day at 10 minutes each runs closer to 9.5 hours of shooting and over
10 hours on site. The gap is not an error in either direction, it is the buffer time, and
buffer time is precisely what absorbs the late arrival, the person who needs a minute to settle,
and the equipment check.

Practical rule: a 5 minute buffer every 5 people. It looks like padding on paper and it is the
reason the last person of the day is not 40 minutes late.

The builder script includes buffers by default. Trust its total over any published table.

## The split-day threshold

Past about 8 hours on site, offer splitting across two days. The script prints a warning when a
schedule crosses that line. Reasons a split day works better at scale: employees get more
flexibility to find a slot that does not collide with their actual job, no-show rates drop, and
neither the photographer nor the on-site coordinator is running on fumes by person 45.

For 50 or more people, raise the split-day option before delivering a single-day schedule, not
after.

## Space requirements, check before scheduling

This is a blocking check, not a detail. A shoot planned into a room that cannot hold the setup
is a wasted day, and the cheapest moment to catch it is before anyone gets a time slot.

- **At least a 10 by 12 foot clear area.** That holds the backdrop stand, the lighting rig, and
  enough subject-to-background distance for clean separation.
- **Standard power outlet access.** The draw is small but the connection is not optional.
- **A waiting area immediately adjacent.** The next person should be steps away, ready to step
  in. A waiting area across the building adds dead time to every single slot, which compounds
  hard across 25 or 50 people.
- **Temperature.** Studio lights put out steady heat across a long day. A room that creeps warm
  means people arrive at the camera already uncomfortable, and it shows. Worth asking facilities
  to run the room slightly cool.

Conference rooms usually work. Lobbies and large common areas work if foot traffic can be
controlled during the session.

## Ordering the day

- **Group by department.** Contiguous departments let people step away together and keep the
  disruption concentrated rather than spread across every team's morning. The builder does this
  with `--by-department`.
- **Mornings beat afternoons.** Energy is higher, and afternoons collide with the usual stack of
  back-to-back meetings.
- **30 minutes of setup before the first person.** Rig assembly, lighting, test frames. The
  client does not need to be involved, they just need to provide room access on time.
- **15 minutes at the end** for breakdown and pack-out.

## Division of responsibility

Worth stating explicitly to the client coordinator up front, it prevents the day-of confusion:

- **Photographer:** all equipment, backdrop, lighting, posing direction, expression coaching,
  shooting, culling, delivery, retouching.
- **Client:** scheduling individual employees, sending the prep communications, reserving and
  preparing the space, managing day-of flow, being the point of contact.

The client should designate one day-of coordinator who owns the flow, checks people in, and
keeps things moving. An office manager or executive assistant is ideal. What helps the
photographer most is the schedule in advance, plus a heads-up on anyone who may need extra time
or accommodation.

## Absences are normal

Some people will be sick, traveling, or remote on the day, every time. Plan the recapture rather
than treating it as a failure. This is also why per-person pricing tends to beat day rates for
the client, they pay for who actually got photographed. Mark no-shows in Notion and build the
recapture list at close-out.
