# Olive Motion

An Indonesian online wedding invitation with motion. It opens on a cover with an arch portrait. An opening scene then pulls back over a garden landscape while palms and flowers grow in. Scroll-revealed sections follow for the couple, countdown, schedule, love story, gallery, live stream, gift accounts and guest wishes. The palette is ivory and olive.

## Run locally

Use Node.js 20 or newer.

```sh
node build.mjs
python3 -m http.server 8000 --directory dist
```

Visit http://localhost:8000/ or add `?to=Ibu%20Dewi` for a personalized greeting. The recipient parameter personalizes the page and does not authenticate guests.

## Structure

- `templates/olive-motion/`: page markup (`index.html`), styles, script and scene artwork.
- `events/<event-slug>/`: one wedding's content (`wedding.js`) and its photos and music.
- `build.mjs`: combines the site with one event into `dist/`.

## New wedding

1. Copy `events/ayu-raka/` to a new event slug. Edit `wedding.js` and replace the files in its `assets/` folder. The sample couple, photos, and wedding details are fictional.
2. Run `node build.mjs <event-slug>`. Deploy the contents of `dist/` to a static web host. Build and deploy each wedding separately.
3. Set `demo: false` for a real wedding. This disables browser-local demo RSVP. Set `contactEmail` to offer direct email confirmation. A shared RSVP endpoint must be connected before the form can collect guest responses.

Set each event’s optional `startsAt` and `endsAt` to ISO 8601 timestamps with explicit offsets for the countdown and calendar links. The countdown targets the earliest scheduled start.

Use `attendanceNote` to explain which events guests are invited to. For a real event, set `mapPin` to the verified entrance coordinates in `latitude,longitude` format. Without a pin, the link searches Maps by name and address.

Optional fields: `shortDate`, `quote`, `inviteLine`, `couple[].instagram`, `streamUrl`, `giftAccounts`, `giftAddress` and `closing`.

The scene layers can be regenerated with `python templates/olive-motion/tools/draw.py` (requires Pillow). It reads `assets/backdrop.webp` and `tools/source/botanical.webp`.

The GitHub repository is public. Keep guest lists, RSVP records, and other private event data outside it.
