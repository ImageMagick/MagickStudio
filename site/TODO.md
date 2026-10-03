# MagickStudio site TODO

Small, self-contained tasks for the browser version of Magick Online Studio in this
folder. Each item should be doable in a single change. Use the CGI version in
`../app/scripts/MagickStudio.cgi` as the reference for layout, fields and behavior.
Remove an item when it is done.

## Upload

- [ ] Add the Upload Properties fieldset (Size, Format, Meta, Interlace, Scene, Channel,
      Passphrase, Density) and pass the values as `MagickReadSettings` (see `UploadForm`).
- [ ] Support the generated input formats from the Format list (`xc`, `gradient`, `plasma`,
      `label`, `caption`, `pattern`, ...) that don't need a file.
- [ ] Add a maximum image area/extent check like `$MaxImageArea`/`$MaxImageExtent` in
      `MagickStudio.pm`, using `ResourceLimits`.
- [ ] Support "append to clipboard image" once a clipboard exists.

## View

- [ ] Paint at position 0,0 when the value of any Paint Properties field changes,
      including the Method and Paint Type dropdowns (new behaviour, not in the CGI).
      Pressing Enter in a text field already does this, see `paintAt` in `src/pages/view.ts`.
- [ ] Add an undo (Back) history so the last change can be reverted.
- [ ] Show the distortion (`error`) value after a Compare, as `ViewForm` does.
- [ ] Show the small image thumbnail in the footer, like `Trailer(1)` does.

## Tools (currently show the "not available" page)

- [ ] Identify
- [ ] Transform
- [ ] Resize
- [ ] Effects
- [ ] F/X
- [ ] Enhance
- [ ] Colormap
- [ ] Decorate
- [ ] Annotate (requires registering fonts with `Magick.addFont`)
- [ ] Draw
- [ ] Composite (requires a second image/clipboard)
- [ ] Compare (requires a second image/clipboard)

## Download

- [ ] Add the Download page with the output format and quality options instead of
      directly saving the image in its original format.

## Help pages

- [ ] Remove or replace the comment links to `scripts/MagickStudio.cgi` in the shared
      help pages, which don't work on the static site.

## General

- [ ] Close the collapsed navbar on small screens after choosing a menu item.
- [ ] Decide whether to fall back to the 32-bit `magick.wasm` for browsers without
      memory64 support (for example Safari).
