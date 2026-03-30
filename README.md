# research-skills

A small Claude Code skill repository for research-figure generation and editing.

## Current contents

This repository currently contains one skill:

- `research-figure-edit/`
  - `SKILL.md` — the skill contract for Claude Code, including mode selection, prompt preprocessing, figure-category detection, venue-style presets, and output expectations.
  - `research_figure_edit.py` — a Python CLI backend that sends image-generation requests to a remote API and saves generated images or raw JSON responses locally.

## What the skill does

The `research-figure-edit` skill supports two workflows:

- `text2image` — generate a research/scientific figure from a text prompt
- `image2image` — generate a new figure from a text prompt plus a local input image

The backend script:
- validates CLI arguments
- loads API configuration from environment variables
- base64-encodes local input images for `image2image`
- calls the remote model endpoint
- extracts inline image bytes from the response
- saves generated images and optionally the raw response JSON

## Requirements

- Python 3
- Valid API credentials via environment variables

The script uses only the Python standard library.

## Installation

### Option 1: Install as a Claude Code skill

Copy the skill folder into either:
- the global skills directory: `~/.claude/skills/`
- a project's local skills directory: `.claude/skills/`

Example:

```bash
cp -r research-figure-edit ~/.claude/skills/
# or
cp -r research-figure-edit .claude/skills/
```

No package installation step is required at the moment.

### Configure environment variables

Set at least one authentication variable before running the script:

```bash
export NANOBANANA_API_KEY="your_api_key"
# or
export NANOBANANA_BEARER_TOKEN="your_bearer_token"
```

Optional overrides:

```bash
export NANOBANANA_HOST="api.vectorengine.ai"
export NANOBANANA_MODEL="gemini-3-pro-image-preview"
```

## Environment variables

Authentication:
- `NANOBANANA_API_KEY`
- `NANOBANANA_BEARER_TOKEN`

At least one of these must be set.

Optional overrides:
- `NANOBANANA_HOST` — defaults to `api.vectorengine.ai`
- `NANOBANANA_MODEL` — defaults to `gemini-3-pro-image-preview`

## Usage

### Show CLI help

```bash
python research-figure-edit/research_figure_edit.py --help
```

### Text to image

```bash
python research-figure-edit/research_figure_edit.py \
  --mode text2image \
  --prompt "A clean paper-ready workflow figure for multimodal reasoning" \
  --output-dir outputs/research-figure-edit \
  --save-raw-response
```

### Image to image

```bash
python research-figure-edit/research_figure_edit.py \
  --mode image2image \
  --prompt "Preserve the structure and convert this into a clean Nature-style scientific figure" \
  --input path/to/input.png \
  --output-dir outputs/research-figure-edit \
  --save-raw-response
```

### Quick syntax check

```bash
python -m py_compile research-figure-edit/research_figure_edit.py
```

## Notes

- Supported input image types: PNG, JPG, JPEG
- `--clarity` is supported only for `text2image`
- If no inline image is returned by the API, the script can still save the raw response JSON for inspection
- The richer prompt engineering logic lives in `research-figure-edit/SKILL.md`; the Python script focuses on request execution and file output

## Repository status

At the moment this repository does not include:
- a test suite
- lint/format configuration
- a package manifest such as `pyproject.toml` or `requirements.txt`
