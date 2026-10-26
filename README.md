# OurCat public website

Static, accessible pages for OurCat early access, help, contributions, privacy and account deletion. GitHub Pages serves the repository root. The live site is https://ourcat.app/, served at the domain root; the 404 page uses root-relative links.

## Domains

- Main site: https://ourcat.app (GitHub Pages custom domain, set by the `CNAME` file, with HTTPS enforced).
- www.ourcat.app redirects to the apex. ourcat.co.uk redirects via the separate repository `powerK10/ourcat-co-uk-redirect`.
- Old github.io links get GitHub's automatic 301 redirect to ourcat.app.
- DNS: Namecheap for ourcat.app (keep the email-forwarding MX records); GoDaddy for ourcat.co.uk.
- Rollback: remove the custom domain in Pages settings and delete `CNAME`.

## Preview and check

```sh
python scripts/preview.py
python scripts/check_site.py
```

Open http://127.0.0.1:8769/ and run the checker in another terminal. The preview server serves extensionless page URLs and uses `404.html` for missing paths. Clean URLs on the live site rely on GitHub Pages; keep every `.html` file in place so existing routes and fragments continue to work. Use `/features`, not `/features/`.

No package installation or build is needed (Pillow, if installed, adds a photo-metadata check). The site uses no scripts, analytics, embedded forms or payment processing. Google Forms handles invitation requests and feedback; the contribution action links to Revolut.

## Design and assets

The visual system follows OurCat's 22 October 2026 app design: blue actions, navy text, pale blue canvas and mint selection. Lora headings and Mulish body text are served locally as WOFF2; their Open Font Licences are in `assets/fonts/`.

`assets/today.png` is a capture of the app's Today screen. It was recaptured on 23 October 2026 from the same OurCat source `dcad00cc` fake-backend release web build with the `features-guide` demo seed, at 360×880 and 2×. The taller viewport keeps the floating Log button clear of the last entry. The browser clock was set to 22 October, 11:00 so the seed's relative times read naturally, and the fresh-water reminder was marked done in the app. The top 26 dp (the FAKE DATA badge) are cropped off, as in the Features guide captures. The records (Miso, Sam) are fictional. It is shown as a development preview, not evidence of a published test build.

`assets/tokyo-wall.jpg` and `assets/tokyo-stretch.jpg` are the owner's own photos of their cat, Tokyo, used with permission. They were cropped and resized, and every embedded metadata field (including location) was removed. Do not add location-revealing photos, and keep the story general: no vet names, conditions, dates or places.

`assets/features/*.png` (used by `features.html`, 24 October 2026) are byte copies of six in-app Features guide captures from the OurCat repo (`assets/features_guide/`, source `43629a7b`, fake backend, `features-guide` seed, 360 dp at 2×). The records (Miso, Pip, Sam, demo vets with 020 0000 numbers) are made up. If the app's guide captures are retaken, recopy them and check the captions still match. The page tells one made-up day in short moments beside the screenshots; keep that plain first-person voice rather than a features grid. Android invitations are available; iPhone/iPad requests are open while the first TestFlight build awaits Apple’s review. Owner installation is separate from external availability and notification acceptance.

`assets/share.png` (1200×630) is the link-preview image. Its source is `scripts/share-card.html`; re-render it with a headless browser at a 1200×630 window after changing that file.

## Editing and publishing

The 23 October 2026 copy refinement keeps the owner story, one-day reply
promise, eligibility and legal pages. The recruitment page explains the app
before asking for an invitation, and links directly to its demo screenshot.
Joining help follows the app's resend, address-correction and return-to-app
actions. It deliberately does not name a custom email sender or subject:
Firebase currently refuses template updates for this project.

- Keep existing `.html` routes and the `support.html#support-development` fragment working: they have external and in-app callers.
- Keep joining, guide, feedback and 404 pages marked `noindex`. This is a search preference, not access control.
- Keep personal responses out of this repository. Never publish Google Forms editor or response links.
- Check content against the released app before describing version-specific behaviour. Do not infer an available Play release from a screenshot.
- Privacy and deletion wording must retain the verified processing, sharing and retention details. Preview substantive changes before publishing.
- A push to `main` publishes the site. Review and verify one revision, publish it, then check the deployed pages and form destinations.

## Tester operations — 26 October 2026

Invitation and feedback Forms keep their existing public links. Both send native new-response alerts to mycatapps@gmail.com. The invitation response workbook has private operational tabs; no participant details belong here. Platform choices include Android, iPhone/iPad and both. Google Play account and 14-day opt-in wording applies only to Android. The iOS joining section remains conditional on external TestFlight approval; do not infer it from an owner install. Update current availability only after an authenticated Apple readback.

TestFlight compatibility was checked on 26 October against its current [UK App Store listing](https://apps.apple.com/gb/app/testflight/id899247664): iOS 16.0 or iPadOS 16.0 or later. This is the TestFlight client requirement, separate from OurCat build 1’s minimum 15.0. Keep this distinction in recruitment and joining help.

For a both-platform request, keep Google Play and App Store country evidence on separate private tracker rows. The Form asks for Play country plus App Store country in the note; a missing second country stays unknown, never assumed eligible.
