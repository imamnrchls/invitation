# Invitation

Reusable online invitations with event content stored separately from templates. The first template, Olive Garden, is an Indonesian wedding invitation with a personal cover, ceremony and reception details, directions, RSVP, photos, story, and opt-in music.

## Run locally

Use Node.js 20 or newer.

```sh
node build.mjs
python3 -m http.server 8000 --directory dist
```

Visit http://localhost:8000/ or add `?to=Ibu%20Dewi` for a personalized greeting. The recipient parameter personalizes the page and does not authenticate guests.

## Reuse a template

1. Copy `events/ayu-raka/` to a new event slug. Edit `wedding.js` and replace the files in its `assets/` folder. The sample couple, photos, and wedding details are fictional.
2. Run `node build.mjs <event-slug> olive-garden`. Deploy the contents of `dist/` to a static web host. Build and deploy each wedding separately.
3. Set `demo: false` for a real wedding. This disables browser-local demo RSVP. A shared RSVP endpoint must be connected before the form can collect guest responses.

Templates live in `templates/<template-id>/`. A template can define its own layout and styles while consuming the same event data. The GitHub repository is public. Keep guest lists, RSVP records, and other private event data outside it.
