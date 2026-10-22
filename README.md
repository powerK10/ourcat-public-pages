# OurCat public website

Static, accessible pages for OurCat early access, help, contributions, privacy and account deletion. GitHub Pages serves the repository root. All site paths are relative so they work beneath `/ourcat-public-pages/`.

## Preview and check

```sh
python -m http.server 8769 --bind 127.0.0.1
python scripts/check_site.py
```

No package installation or build is needed. The site uses no scripts, analytics, embedded forms or payment processing. Google Forms handles invitation requests and feedback; the contribution action links to Revolut.

## Design and assets

The visual system follows OurCat's 22 October 2026 app design: blue actions, navy text, pale blue canvas and mint selection. Lora headings and Mulish body text are served locally as WOFF2; their Open Font Licences are in `assets/fonts/`.

`assets/today.png` is the app's accepted 22 October guide capture, with fictional Miso/Sam records, from source `23a2ffc1be029794727f155ca173034e48a7f873`. It is displayed as a development preview, not evidence of a published test build.

## Editing and publishing

- Keep existing `.html` routes and the `support.html#support-development` fragment working: they have external and in-app callers.
- Keep joining, guide and feedback pages marked `noindex`. This is a search preference, not access control.
- Keep personal responses out of this repository. Never publish Google Forms editor or response links.
- Check content against the released app before describing version-specific behaviour. Do not infer an available Play release from a screenshot.
- Privacy and deletion wording must retain the verified processing, sharing and retention details. Preview substantive changes before publishing.
- A push to `main` publishes the site. Review and verify one revision, publish it, then check the deployed pages and form destinations.
