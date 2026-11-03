# TvennDB logo

Tvenn is Old Norse for twin or pair. The symbol is a T, one record (the bar) carried by two stems: the physical asset and its digital twin. The orange node marks the record. All lettering is converted to outlines, so no fonts are needed.

## Versions

| Folder | Use |
|---|---|
| `horizontal` | Primary logo. Web headers, documentation, the Explorer. |
| `horizontal-tagline` | With GRAPH DATABASE FOR DIGITAL TWINS. Covers, product pages, the first time TvennDB appears in a document. Not below 48 px tall. |
| `stacked` | Square or narrow spaces: social avatars, booth graphics, README banners. |
| `symbol` | The mark on its own, once the name is already visible nearby. |
| `wordmark` | Lettering only, where the symbol already appears. |
| `app-icon` | Rounded tile (`-square` without rounding, for platforms that apply their own mask). |
| `favicon` | Complete favicon set for the web, see below. |

## Colour versions

| Suffix | Background | Colours |
|---|---|---|
| `on-light` | paper `#FBF9F6` or white | ink `#231F20`, teal `#008287`, orange `#FF7400` |
| `on-dark` | deep teal `#002F31` or dark photos | light `#DBD5D6`, teal `#008287`, orange `#FF7400` |
| `black` | single colour print, embossing, fax, engraving | ink `#231F20` |
| `white` | single colour on teal or busy backgrounds | white |

Every SVG is in `svg/`. PNG files with transparent backgrounds are in `png/` at heights of 128, 256, 512 and 1024 px (the `-128h` suffix gives the height).

## Rules

- Clear space: keep at least the height of the symbol's bar, including the orange node, free on every side.
- Minimum size: the horizontal logo 24 px tall on screen and 8 mm in print; the symbol 16 px.
- Do not recolour, stretch, rotate, outline, add effects to, or retype the logo.
- Use orange only for the node. Do not swap the teal and ink stems.
- TvennDB is always written as one word with a capital T and capital DB.

## Favicon

Copy everything in `favicon/` to the web root and paste `head-snippet.html` into `<head>`.

- `favicon.svg` switches the ink parts to light in dark mode, for modern browsers.
- `favicon.ico` (16, 32 and 48 px) and the PNG files use the deep teal tile so they show up on both light and dark tabs.
- `apple-touch-icon.png` is 180 px, `android-chrome-*` and `icon-maskable-512x512.png` are referenced by `site.webmanifest`, `safari-pinned-tab.svg` is the single colour mask icon, and `mstile-150x150.png` with `browserconfig.xml` covers Windows tiles.

## Typefaces (for reference)

The wordmark is Familjen Grotesk Bold and the tagline is Chakra Petch Regular, the same families as the Hubbiot design system. Both are under the SIL Open Font License.

The TvennDB name and logo are trademarks of Hubbiot AB.
