#!/usr/bin/env python3
"""Turn the full-resolution photographs into a web gallery.

For every entry in `data/<gallery>.json` this script

  1. reads the master from `photos_src/<gallery>/`,
  2. writes a display copy and a filmstrip thumbnail into `img/<gallery>/`,
  3. strips the camera metadata (device, serial numbers, GPS, original
     filename) and puts the copyright back in its place, and
  4. regenerates the markup between the gallery markers in
     `<gallery>.html`.

Point 3 is the reason this exists rather than a `sips` one-liner. Phone
JPEGs carry a lot that has no business on a public page, and the fields
that *should* travel with a photograph — who took it and on what terms —
are exactly the ones a resize would otherwise throw away. The author's
name goes into XMP (UTF-8, what Google Images and Lightroom read) and, in
an ASCII-folded form, into the old EXIF Artist/Copyright tags, which
cannot represent an accented character.

The masters stay out of the repo; see `.gitignore`. Keep a backup of
`photos_src/` — without it this script has nothing to rebuild from.

Usage:

    python3 scripts/build_gallery.py            # every gallery in data/
    python3 scripts/build_gallery.py lepidoptera

Only Pillow is needed on top of the standard library:

    pip3 install Pillow

Exit codes: 0 on success, 1 if a master is missing or a page has no
gallery markers to write into.
"""

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required: pip3 install Pillow")

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "photos_src"
DATA_DIR = ROOT / "data"
IMG_DIR = ROOT / "img"

# Long edge in pixels. The display copy fills the carousel stage, so it
# has to survive a full-screen desktop; the thumbnail only ever fills a
# filmstrip cell, at 2x for retina.
DISPLAY_PX = 1600
THUMB_PX = 800
DISPLAY_QUALITY = 82
THUMB_QUALITY = 78

MARKER_START = "<!-- gallery:start -->"
MARKER_END = "<!-- gallery:end -->"

# EXIF tag ids we deliberately keep.
EXIF_DATETIME = 0x0132
EXIF_ARTIST = 0x013B
EXIF_COPYRIGHT = 0x8298


def xmp_packet(credit, alt, taken):
    """An XMP block carrying authorship, terms and a description.

    xmpRights:Marked=True is the flag that tells an aggregator the image
    is *not* free to use; UsageTerms and WebStatement say on what terms
    and where to check. dc:rights is what most viewers surface as
    "Copyright".
    """
    e = lambda s: html.escape(s, quote=False)
    return (
        '<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
        '<rdf:Description rdf:about=""'
        ' xmlns:dc="http://purl.org/dc/elements/1.1/"'
        ' xmlns:xmpRights="http://ns.adobe.com/xap/1.0/rights/"'
        ' xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"'
        ' xmlns:xmp="http://ns.adobe.com/xap/1.0/">'
        f"<dc:creator><rdf:Seq><rdf:li>{e(credit['creator'])}</rdf:li></rdf:Seq></dc:creator>"
        f'<dc:rights><rdf:Alt><rdf:li xml:lang="x-default">{e(credit["notice"])}</rdf:li></rdf:Alt></dc:rights>'
        f'<dc:description><rdf:Alt><rdf:li xml:lang="x-default">{e(alt)}</rdf:li></rdf:Alt></dc:description>'
        "<xmpRights:Marked>True</xmpRights:Marked>"
        f'<xmpRights:UsageTerms><rdf:Alt><rdf:li xml:lang="x-default">{e(credit["usage_terms"])}</rdf:li></rdf:Alt></xmpRights:UsageTerms>'
        f"<xmpRights:WebStatement>{e(credit['web_statement'])}</xmpRights:WebStatement>"
        f"<photoshop:Credit>{e(credit['creator'])}</photoshop:Credit>"
        f"<photoshop:DateCreated>{e(taken)}</photoshop:DateCreated>"
        f"<xmp:CreateDate>{e(taken)}</xmp:CreateDate>"
        "</rdf:Description></rdf:RDF></x:xmpmeta>"
        '<?xpacket end="w"?>'
    )


def clean_exif(credit, taken):
    """A brand new EXIF block holding only the three fields we want.

    Building it from scratch rather than editing the camera's own is the
    point: anything not set here — GPS, device, serial, thumbnail — is
    simply absent from the file we publish.
    """
    exif = Image.Exif()
    exif[EXIF_ARTIST] = credit["creator_ascii"]
    exif[EXIF_COPYRIGHT] = credit["notice_ascii"]
    exif[EXIF_DATETIME] = taken.replace("-", ":") + " 00:00:00"
    return exif


def render(src, dest, long_edge, quality, credit, alt, taken):
    """Resize `src` into `dest` and return the (width, height) written."""
    with Image.open(src) as im:
        # Honour the camera's rotation flag, then drop it: the pixels are
        # now the right way up, so a viewer that ignores EXIF still gets
        # an upright photograph.
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((long_edge, long_edge), Image.LANCZOS)
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(
            dest,
            "JPEG",
            quality=quality,
            optimize=True,
            progressive=True,
            subsampling="4:2:0",
            exif=clean_exif(credit, taken),
            xmp=xmp_packet(credit, alt, taken).encode("utf-8"),
        )
        return im.size


def pretty_date(iso):
    """2026-06-09 -> '9 June 2026', matching the style used site-wide."""
    d = date.fromisoformat(iso)
    return f"{d.day} {d:%B} {d.year}"


def taxon_markup(taxon):
    """A scientific name set the way a taxonomist expects to read it.

    Genus and species in italics, the genus capitalised and the species
    not; the qualifier ("cf.") and the "sp." of an open determination stay
    upright, because they are not part of the name; the author citation
    upright too, and smaller. `<i>` is the right element here — HTML calls
    out taxonomic designations as one of its jobs.

    Returns '' when there is no determination, which is a valid state: an
    animal nobody has named yet still gets a date.
    """
    if not taxon or not taxon.get("genus"):
        return ""

    parts = [f'<i>{html.escape(taxon["genus"])}</i>']
    if taxon.get("qualifier"):
        parts.append(html.escape(taxon["qualifier"]))
    if taxon.get("species"):
        parts.append(f'<i>{html.escape(taxon["species"])}</i>')
    else:
        # Open nomenclature: the genus is settled, the species is not.
        parts.append("sp.")
    if taxon.get("authority"):
        parts.append(
            f'<span class="taxon-authority">{html.escape(taxon["authority"])}</span>'
        )
    return f'<span class="taxon">{" ".join(parts)}</span>'


def caption_markup(photo):
    """The species, then the date — separated only when both are there."""
    taxon = taxon_markup(photo.get("taxon"))
    when = (
        f'<time datetime="{photo["date"]}">{pretty_date(photo["date"])}</time>'
    )
    return f'{taxon}<span class="caption-sep">·</span>{when}' if taxon else when


def slide_markup(gallery, photo, i, indent):
    """One full-size frame. Only the active one is displayed."""
    pad = " " * indent
    active = " is-active" if i == 0 else ""
    # The first frame is what the visitor sees on arrival, so it loads
    # eagerly; the rest wait until the carousel reaches them.
    loading = "eager" if i == 0 else "lazy"
    return (
        f'{pad}<figure class="slide{active}" data-index="{i}">\n'
        f'{pad}  <img src="img/{gallery}/{photo["slug"]}.jpg"\n'
        f'{pad}       width="{photo["display_w"]}" height="{photo["display_h"]}"\n'
        f'{pad}       loading="{loading}" decoding="async"\n'
        f'{pad}       alt="{html.escape(photo["alt"], quote=True)}">\n'
        f'{pad}  <figcaption class="slide-caption">{caption_markup(photo)}</figcaption>\n'
        f"{pad}</figure>"
    )


def thumb_markup(gallery, photo, i, indent):
    """One frame of the filmstrip under the stage."""
    pad = " " * indent
    active = " is-active" if i == 0 else ""
    # The accessible name is the determination, falling back to the date —
    # "Melanargia cf. lachesis" tells a screen-reader user far more about
    # where they are in the strip than "photograph 12 of 20" would.
    label = re.sub(r"<[^>]+>", "", caption_markup(photo)).replace("·", "—")
    return (
        f'{pad}<button type="button" class="thumb{active}" role="tab"\n'
        f'{pad}        data-index="{i}" aria-selected="{str(i == 0).lower()}"\n'
        f'{pad}        aria-label="{html.escape(label, quote=True)}">\n'
        f'{pad}  <img src="img/{gallery}/thumb/{photo["slug"]}.jpg"\n'
        f'{pad}       width="{photo["thumb_w"]}" height="{photo["thumb_h"]}"\n'
        f'{pad}       loading="lazy" decoding="async" alt="">\n'
        f"{pad}</button>"
    )


def splice(page, markup):
    """Replace whatever sits between the gallery markers in `page`."""
    text = page.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"([ \t]*){re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}",
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        sys.exit(f"{page.name}: no {MARKER_START} / {MARKER_END} pair to write into")

    indent = match.group(1)
    gallery = page.stem
    n = len(markup)
    pad, inner = indent + "  ", len(indent) + 4

    slides = "\n".join(slide_markup(gallery, p, i, inner) for i, p in enumerate(markup))
    thumbs = "\n".join(thumb_markup(gallery, p, i, inner) for i, p in enumerate(markup))

    # The prev/next buttons live inside the stage so they can sit over the
    # photograph; the filmstrip is a tablist, which is what it behaves like.
    body = (
        f'{pad}<div class="carousel" data-count="{n}">\n'
        f'{pad}  <div class="stage">\n'
        f'{pad}    <button type="button" class="stage-nav stage-prev" aria-label="Previous photograph">&#8249;</button>\n'
        f"{slides}\n"
        f'{pad}    <button type="button" class="stage-nav stage-next" aria-label="Next photograph">&#8250;</button>\n'
        f"{pad}  </div>\n"
        f'{pad}  <div class="filmstrip" role="tablist" aria-label="Choose a photograph">\n'
        f"{thumbs}\n"
        f"{pad}  </div>\n"
        f"{pad}</div>"
    )
    block = f"{indent}{MARKER_START}\n{body}\n{indent}{MARKER_END}"
    updated = text[: match.start()] + block + text[match.end() :]

    if updated == text:
        return False
    page.write_text(updated, encoding="utf-8")
    return True


def build(name):
    manifest_path = DATA_DIR / f"{name}.json"
    if not manifest_path.exists():
        sys.exit(f"no manifest at {manifest_path.relative_to(ROOT)}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    credit = manifest["credit"]
    photos = manifest["photos"]
    src_dir = SRC_DIR / name

    for photo in photos:
        src = src_dir / photo["source"]
        if not src.exists():
            sys.exit(f"missing master: {src.relative_to(ROOT)}")

        slug, alt, taken = photo["slug"], photo["alt"], photo["date"]
        w, h = render(
            src, IMG_DIR / name / f"{slug}.jpg",
            DISPLAY_PX, DISPLAY_QUALITY, credit, alt, taken,
        )
        tw, th = render(
            src, IMG_DIR / name / "thumb" / f"{slug}.jpg",
            THUMB_PX, THUMB_QUALITY, credit, alt, taken,
        )
        photo["display_w"], photo["display_h"] = w, h
        photo["thumb_w"], photo["thumb_h"] = tw, th
        print(f"  {slug}  {w}x{h} + {tw}x{th} thumb")

    changed = splice(ROOT / f"{name}.html", photos)
    total = sum(
        p.stat().st_size
        for p in (IMG_DIR / name).rglob("*.jpg")
    )
    print(
        f"{name}: {len(photos)} photographs, {total / 1e6:.1f} MB served, "
        f"{name}.html {'updated' if changed else 'already current'}"
    )


def main():
    names = sys.argv[1:] or sorted(p.stem for p in DATA_DIR.glob("*.json"))
    if not names:
        sys.exit("no galleries found in data/")
    for name in names:
        build(name)


if __name__ == "__main__":
    main()
