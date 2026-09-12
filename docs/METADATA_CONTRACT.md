# Metadata contract

This service extracts facts from the binary asset using deterministic tools.
It does not infer business tags and does not expose a human override for these
fields.

## Image fields

- MIME type
- Width and height in pixels
- Reduced aspect ratio, such as `16:9` or `1:1`
- Source marker `deterministic`

## Video fields

- MIME type
- Width and height in pixels
- Reduced aspect ratio
- Duration in seconds
- Frame rate when available
- Source marker `deterministic`

The actual adapters may use ImageMagick/Sharp for images and `ffprobe` for
videos. Adapter failures must be retried or reported; fields must not be
silently guessed. The JSON contract is in
`schemas/metadata-result.schema.json`.
