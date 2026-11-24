# Invitation

A home for reusable online invitation templates. Each event selects a template and supplies its own details.

## Proposed layout

- `templates/<template-id>/` holds the layout, styles, and shared assets for a design.
- `events/<event-slug>/` holds an event's template ID, names, schedule, venue, and event-specific assets.
- Each published invitation uses its own URL, such as `/events/ayu-and-raka/`.

Keep event details separate from the design so several invitations can share a template and an event can change templates without re-entering its details.
