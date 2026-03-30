# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This repository is currently a small Claude Code skill repository centered on one skill: `research-figure-edit/`.

The intended usage model is to copy a skill folder into either `~/.claude/skills/` for global use or `.claude/skills/` inside a project for project-local use.

The first skill implements a research-figure generation/editing workflow:
- `research-figure-edit/SKILL.md` defines the skill contract, mode selection rules, prompt-preprocessing requirements, venue-style presets, and expected output reporting.
- `research-figure-edit/research_figure_edit.py` is the executable backend script that validates inputs, loads environment configuration, calls the remote image-generation API, and saves returned images/raw JSON to disk.

There is no top-level application framework, package manager config, test suite, or lint setup in the repository at the moment. Treat this repo as a skill-definition repo, not a conventional Python package.

## Common commands

### Inspect the backend CLI
```bash
python research-figure-edit/research_figure_edit.py --help
```

### Run text-to-image manually
```bash
python research-figure-edit/research_figure_edit.py \
  --mode text2image \
  --prompt "<prompt>" \
  --output-dir outputs/research-figure-edit \
  --save-raw-response
```

### Run image-to-image manually
```bash
python research-figure-edit/research_figure_edit.py \
  --mode image2image \
  --prompt "<prompt>" \
  --input <local-image-path> \
  --output-dir outputs/research-figure-edit \
  --save-raw-response
```

### Run a quick local syntax check
```bash
python -m py_compile research-figure-edit/research_figure_edit.py
```

## Environment variables for the first skill

`research_figure_edit.py` loads configuration from environment variables in `load_config_from_env()`.

Required authentication:
- `NANOBANANA_API_KEY`
- `NANOBANANA_BEARER_TOKEN`

At least one of the two must be set, otherwise the script raises an error.

Optional overrides:
- `NANOBANANA_HOST` — defaults to `api.vectorengine.ai`
- `NANOBANANA_MODEL` — defaults to `gemini-3-pro-image-preview`

Authentication behavior:
- If `NANOBANANA_BEARER_TOKEN` is set, the script sends `Authorization: Bearer ...`.
- If `NANOBANANA_API_KEY` is set, the script appends it as `?key=...` on the request path.
- Both can be present; bearer auth goes in headers and API key goes in the URL.

## High-level architecture

### Skill contract layer
`research-figure-edit/SKILL.md`

This file is the source of truth for how Claude should use the skill. It contains:
- when the skill should be selected
- how to infer `text2image` vs `image2image`
- required preprocessing before generation
- figure-category detection rules
- venue-style preset selection rules
- prompt construction requirements
- expected response structure back to the user

If behavior changes, update `SKILL.md` first, then align the backend script if needed.

### Execution layer
`research-figure-edit/research_figure_edit.py`

The backend script is intentionally self-contained and uses only the Python standard library.

Its flow is:
1. Parse CLI arguments with `parse_args()`.
2. Validate mode/prompt/input combinations in `validate_args()`.
3. Load API configuration from env vars via `load_config_from_env()`.
4. For `image2image`, detect MIME type and base64-encode the local input image.
5. Build request parts and payload with `build_parts()` and `build_payload()`.
6. Send one HTTPS request to the configured host with `send_request()`.
7. Walk the returned JSON recursively to find inline image bytes via `iter_inline_images()`.
8. Save generated images and optionally the raw response JSON into the chosen output directory.

### Request/response model
- The script sends requests to `/v1beta/models/{model}:generateContent`.
- `text2image` requests ask only for `IMAGE` output.
- `image2image` requests ask for `TEXT` and `IMAGE` output and include the local source image as `inline_data`.
- Returned images are extracted from any nested `inline_data` / `inlineData` fields in the API response, so response traversal is schema-tolerant.

### Prompt handling split
There is a deliberate split between prompt design and API execution:
- `SKILL.md` defines the rich preprocessing, category detection, positive/negative prompt construction, and venue-style reasoning Claude should do.
- `research_figure_edit.py` does not implement that reasoning. It only applies a small `clarity` suffix for text-to-image requests and sends the final prompt it receives.

When extending the skill, keep this separation: orchestration logic belongs in the skill instructions, while the Python script should stay focused on transport, validation, and file output.

## Important implementation details

- Supported modes are hard-coded as `text2image` and `image2image`.
- Supported input MIME types are PNG and JPEG only.
- `--clarity` is only valid for `text2image`; validation rejects it for `image2image`.
- If no image is found in the response, the script falls back to saving the raw JSON response so the result is still inspectable.
- Output files are timestamp-based and grouped by the provided `--output-dir`.

## Repository state assumptions

As of the current repo state:
- no `README.md`
- no existing `CLAUDE.md` before this file
- no test suite
- no lint/format config
- no package manifest (`pyproject.toml`, `requirements.txt`, `package.json`, `Makefile`)

Do not invent build, lint, or test workflows unless those files are added later.
