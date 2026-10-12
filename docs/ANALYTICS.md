# Doom website analytics

GA4 measurement ID: **G-JVF09MZEGD**, shared with the other ChanceTheMaker instrument sites. The `product=doom-fm1-smk` field and page path separate this site in reports.

Only `https://chancethemaker.github.io/doom-fm1-smk/` and its subpages send data. Localhost and other forks do not. This follows the existing Sloop website behavior: analytics is on by default, a cookie notice offers **Keep analytics on** or **Essential only**, and the footer **Cookie settings** button reopens the preferences modal. A stored decline is respected; installer features work either way.

Advertising consent, advertising personalization and Google signals remain disabled. Page URLs omit query strings, and referrers are reduced to their origin. Custom event metadata is limited to product, selected model, firmware version, stage, fixed error category and file type. MIDI data, device serial numbers, firmware files, raw error messages and installer logs are never included.

| Event | Meaning |
| --- | --- |
| Page view | A production page loaded |
| `firmware_build_started` | User clicked Build |
| `firmware_build_complete` | App/base verification and package construction succeeded |
| `firmware_build_failed` | Download, verification or packaging failed |
| `download_click` | User requested a built FWSC download; not proof it was saved |
| `install_attempt` | User clicked Install, before MIDI permission |
| `install_transfer_complete` | Installer returned after loader completion; **does not prove Doom booted** |
| `install_failed` | Permission, discovery, handoff or installation failed |

No event is sent for automatic hero animation frames or color changes. Analytics never gates or delays installation. Counts can be reduced by opt-outs, blockers, closed tabs and network failures.

Register `product`, `device_model`, `firmware_version`, `stage`, `error_code` and `file_type` as event-scoped custom dimensions in GA4 if those breakdowns are useful. `device_model` is the user's selected build target, not a hardware identifier. The port does not claim verified installations from browser transfer counts.

Run `node tests/analytics_test.mjs` to check host/path isolation, preferences and event filtering without contacting Google.
