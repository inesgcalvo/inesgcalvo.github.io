# inesgcalvo.github.io

Personal site, served straight from this repository by GitHub Pages. Plain
HTML, one stylesheet, a little vanilla JavaScript — no build step and no
dependencies to install for the site itself.

## Layout

| Path | What lives there |
| --- | --- |
| `*.html` | One file per page. `index.html` is the molecule; the rest are its branches. |
| `css/style.css` | The whole design system. Bump the `?v=` on every page when you change it. |
| `js/` | One script per page that needs one. |
| `img/` | Everything the site serves, galleries included. |
| `data/` | Gallery manifests — the hand-edited source of truth for captions. |
| `photos_src/` | Full-resolution masters. **Not in the repo** (see `.gitignore`). |
| `scripts/` | Maintenance scripts, run by hand or by GitHub Actions. |

## Photo galleries

A gallery is three things: a manifest in `data/`, the masters in
`photos_src/`, and a page with a pair of `<!-- gallery:start -->` /
`<!-- gallery:end -->` markers. `scripts/build_gallery.py` joins them up.

To add photographs to an existing gallery:

1. Drop the originals into `photos_src/<gallery>/`.
2. Add an entry to `data/<gallery>.json` for each one — `source`, `slug`,
   `date` and an `alt` description for screen readers.
3. Run the build and commit what it produced:

   ```
   pip3 install Pillow          # once
   python3 scripts/build_gallery.py lepidoptera
   ```

The script writes a display copy and a thumbnail into `img/<gallery>/`,
rewrites the grid inside `<gallery>.html`, and re-stamps the copyright.
It is safe to re-run: same input, same output.

To start a new gallery, copy `lepidoptera.html`, change the title and the
prose, add `data/<name>.json`, and name the page after the manifest — the
script derives one from the other.

### Copyright

Resizing a JPEG throws its metadata away, so the build script puts the
important part back: the author and the licence terms go into XMP
(`dc:creator`, `dc:rights`, `xmpRights:UsageTerms`, `xmpRights:Marked`)
and, ASCII-folded, into the EXIF `Artist` and `Copyright` tags. Everything
else the camera wrote — GPS, device, serial number, original filename — is
dropped rather than republished.

Edit the terms in the `credit` block of the manifest, then re-run the
build to restamp every file.

### Back up `photos_src/`

The masters are the only thing here that cannot be regenerated. The repo
deliberately does not carry them (they are ~100 MB), so they exist on your
machine and nowhere else until you back them up.

## Citation counts

`scripts/update_citations.py` refreshes the numbers on `publications.html`
from Crossref. A GitHub Action runs it weekly; see
`.github/workflows/`.
