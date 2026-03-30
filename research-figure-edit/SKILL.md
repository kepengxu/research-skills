---
name: research-figure-edit
description: Generate or edit research figures with text-to-image and text+image-to-image workflows. Use when the user wants科研绘图、论文插图生成、基于现有图片改图、统一 figure 风格、润色 scientific schematic。
argument-hint: [prompt and optional input image path]
allowed-tools: Bash(*), Read, Write, Edit
---

# Research Figure Edit

Use this skill for two capabilities:

1. **text2image**: generate a research/scientific figure from a text prompt.
2. **image2image**: generate a new figure from a text prompt plus an input image.

## Required environment variables

- `NANOBANANA_HOST` — API host. Defaults to `api.vectorengine.ai` if unset.
- `NANOBANANA_MODEL` — model name. Defaults to `gemini-3-pro-image-preview` if unset.
- `NANOBANANA_API_KEY` — optional query-string API key.
- `NANOBANANA_BEARER_TOKEN` — optional bearer token for `Authorization` header.

At least one of `NANOBANANA_API_KEY` or `NANOBANANA_BEARER_TOKEN` must be set.

## Backend script

The backend script is:

- `~/.claude/skills/research-figure-edit/research_figure_edit.py`

## Execution workflow

When this skill is invoked, do the following:

1. Parse the user's request from `$ARGUMENTS`.
2. Determine whether the user supplied an input image path.
3. If there is a valid local image path, use `--mode image2image` and pass that path with `--input`.
4. Otherwise use `--mode text2image`.
5. Run a **preprocessing stage** before generation.
6. In preprocessing, analyze the request context and infer:
   - the figure category
   - the paper-style intent
   - the likely venue-style preset
   - the desired layout structure
   - the color semantics
   - the connection structure
   - the arrow density and arrow hierarchy
   - whether the request is a hero figure, overview figure, mechanism figure, architecture figure, or workflow figure
7. Automatically select the most suitable venue-style preset.
8. Optimize the layout and connection grammar before writing prompts.
9. From the preprocessing result, write **two explicit prompts**:
   - a **Positive prompt** that is very detailed, publication-oriented, and suitable for scientific figure generation
   - a **Negative prompt** that suppresses low-quality, non-academic, decorative, illegible, or off-style outputs
9. Rewrite the generation input so the backend script receives a strong, paper-style final prompt derived from the Positive prompt.
10. Choose an output directory automatically:
   - default to `outputs/research-figure-edit/`
   - if that is unsuitable for the current workspace, use a nearby `outputs/` directory under the working directory
11. Run the backend script with Bash and let it complete the full workflow in one step: request API response, extract image bytes, and save the final image file.
12. Return the saved output paths to the user together with:
   - detected figure category
   - selected venue-style preset
   - Positive prompt
   - Negative prompt
   - any major rewrite decisions (briefly)

## Mode selection rules

- If the user provides **only a prompt**, run `--mode text2image`.
- If the user provides a **prompt and a local input image path**, run `--mode image2image`.
- Only treat a path as an image input if it points to an existing local file and has a supported image extension.
- If the request is ambiguous, ask the user to specify the prompt text and image path separately.

## Figure category detection

Before generating, classify the request into the closest figure category.

### Categories

- `flowchart` — workflows, pipelines, training loops, inference loops, algorithm steps
- `architecture` — model structures, module diagrams, system frameworks, encoder-decoder layouts
- `mechanism` — principle illustrations, reward mechanisms, attention/memory/routing logic, internal method explanation
- `comparison` — baseline vs ours, before/after, method comparison, ablation overviews
- `concept` — overview figures, teaser figures, motivation figures, high-level research idea illustrations
- `dataflow` — data transformation pipelines, multimodal input/output paths, preprocessing/postprocessing streams
- `experiment` — experiment setup, evaluation protocol, train/val/test structure, benchmark pipeline

### Detection heuristics

Use lightweight intent matching from the user's wording.

- If the request mentions `流程图`, `pipeline`, `workflow`, `step`, `loop`, `training pipeline`, prefer `flowchart`
- If it mentions `架构图`, `architecture`, `framework`, `module`, `encoder`, `decoder`, prefer `architecture`
- If it mentions `机制`, `principle`, `how it works`, `reward mechanism`, `attention mechanism`, prefer `mechanism`
- If it mentions `对比`, `compare`, `baseline`, `before/after`, `ablation`, prefer `comparison`
- If it mentions `overview`, `motivation`, `teaser`, `main idea`, `concept`, prefer `concept`
- If it mentions `data flow`, `input/output`, `preprocess`, `postprocess`, `multimodal stream`, prefer `dataflow`
- If it mentions `experiment setup`, `evaluation`, `benchmark`, `protocol`, prefer `experiment`

If multiple categories match, prefer the most structurally specific one in this order:
`flowchart > architecture > mechanism > comparison > concept > dataflow > experiment`

## Venue-style preset system

After detecting the category, automatically select a venue-style preset.

### Presets

#### `paper-clean`
Use for generic publication-quality figures when no venue-specific visual cue is clearly better.

Prompt guidance:
- clean publication-quality scientific figure
- white background
- minimal modern academic style
- balanced layout
- crisp labels
- subtle professional color palette
- polished and highly readable

#### `nature-like`
Use for elegant overview figures, concept figures, and high-level mechanism illustrations.

Prompt guidance:
- Nature-like scientific figure
- elegant and refined
- clean white background
- subtle professional color palette
- balanced composition
- minimal clutter
- polished scientific schematic

#### `science-like`
Use for explanatory mechanism figures and concept+experiment hybrid figures.

Prompt guidance:
- Science-like publication figure
- explanatory scientific illustration
- refined but accessible design
- strong visual storytelling
- concise labels
- polished multi-part composition

#### `cvpr-like`
Use for computer vision style architecture diagrams, technical pipelines, and comparison figures.

Prompt guidance:
- CVPR-like technical figure
- structured modular layout
- clear blocks and arrows
- compact and professional design
- white background
- strong readability
- conference-ready diagram

#### `iccv-like`
Use for visually layered architecture diagrams and complex visual systems.

Prompt guidance:
- ICCV-like vision paper diagram
- professional modular architecture figure
- clearly separated components
- strong visual hierarchy
- balanced layout
- publication-quality technical illustration

#### `neurips-like`
Use for machine learning method figures, algorithm logic diagrams, and concise training schematics.

Prompt guidance:
- NeurIPS-like machine learning figure
- clean and rigorous academic style
- precise structure
- compact scientific layout
- clear logical flow
- minimal but highly legible

#### `iclr-like`
Use for reinforcement learning, LLM, alignment, agent, and training workflow figures.

Prompt guidance:
- ICLR-like modern ML figure
- clean research schematic
- clear process flow
- concise modular design
- elegant but rigorous
- highly readable labels
- suitable for RL or LLM training diagrams

#### `aaai-like`
Use for formal AI system diagrams and logic-oriented technical figures.

Prompt guidance:
- AAAI-like AI research diagram
- clear and formal academic style
- structured blocks
- straightforward technical presentation
- neat and concise conference-style figure

## Category to preset mapping

Use these defaults unless the user explicitly asks for a different visual style:

- `flowchart` -> `iclr-like`
- `architecture` -> `cvpr-like`
- `mechanism` -> `nature-like`
- `comparison` -> `cvpr-like`
- `concept` -> `nature-like`
- `dataflow` -> `paper-clean`
- `experiment` -> `neurips-like`

## Override rules

- If the user explicitly asks for `Nature`, `Science`, `CVPR`, `ICCV`, `NeurIPS`, `ICLR`, or `AAAI` style, honor that request.
- If the user asks for a `paper main figure`, `overview figure`, or `teaser figure`, prefer `nature-like` unless they specify another venue.
- If the user asks for a `training pipeline`, `RL flowchart`, `agent workflow`, or `LLM training diagram`, prefer `iclr-like`.
- If the user asks for a `computer vision architecture`, `vision pipeline`, or `multi-branch model diagram`, prefer `cvpr-like` or `iccv-like`.
- If the user gives no clear style signal, use the mapping table above.

## Layout and connection optimization rules

Before writing prompts, optimize the visual organization of the figure itself.

### Narrative hierarchy

Prefer figures with explicit narrative hierarchy rather than flat equal-weight modules.

Use layered organization when appropriate, such as:
- top: central claim / problem framing
- middle: method response / mechanism / architecture
- bottom or side: validation mapping / experiment support

If one part of the figure is conceptually dominant, give it more visual weight.
Do not force all panels to have equal size when the content is not equally important.

### Arrow and connector discipline

Reduce unnecessary arrows.
Only use arrows when they truly improve scientific readability.

Prefer three levels of connector strength:
- **primary arrows** for the main process or argument flow
- **secondary arrows** for local dependencies within one panel
- **minimal connectors or simple alignment** for weak logical mapping

Avoid spider-web connection structures.
Avoid dense cross-panel arrows when color semantics, grouping, or alignment can communicate the same relationship more clearly.

### Preferred connection structures

Prefer clean structures such as:
- linear chains for process explanations
- tree-like branching and merging for supervision or aggregation paths
- parallel columns feeding one fusion block for multimodal reasoning
- aligned mapping grids or tag panels for experiment-to-operator correspondence

Avoid complex global loops unless the loop itself is the scientific point.
If a loop is needed, keep it local to one panel instead of the whole figure.

### Panel consistency

Within a multi-panel figure, keep panels internally consistent.
A strong default is:
- title on top
- main visual structure in the center
- one short takeaway note below

Do not mix radically different alignment systems across neighboring panels unless there is a clear reason.

### Cross-panel structure

Minimize direct cross-panel connectors.
When possible, communicate shared semantics by:
- repeated color meaning
- repeated visual tokens
- aligned panel ordering
- matching labels
- mirrored or parallel local structures

For validation panels, prefer compact mapping layouts over long return arrows to earlier panels.
For example, use aligned tags, mini-box mappings, or table-like correspondences rather than many long crossing connectors.

### Layout optimization objectives

During preprocessing, explicitly optimize for:
- balanced visual weight
- clean reading order
- minimal connector clutter
- high signal-to-noise ratio
- strong alignment
- clear grouping
- scientific readability at paper scale
- immediate recognition of the main claim

## Prompt preprocessing and construction rules

Before any image generation, always perform prompt preprocessing.

### Preprocessing outputs

The preprocessing stage must explicitly produce two artifacts:

1. **Positive prompt**
2. **Negative prompt**

### Positive prompt requirements

The Positive prompt must be:

- tailored to the user's scientific context
- aligned with the detected figure category
- aligned with the selected venue-style preset
- detailed enough for high-quality academic figure generation
- written in a publication-oriented style rather than a casual image-generation style
- structured, specific, and visually directive

The Positive prompt should usually contain:

1. **Figure identity**
   - what kind of figure this is
   - whether it is a hero figure, overview figure, mechanism figure, architecture figure, workflow figure, comparison figure, or experiment figure

2. **Scientific content layer**
   - the exact entities, modules, stages, or claims to show
   - the intended scientific message
   - the causal or logical relationships between components

3. **Layout layer**
   - horizontal or vertical layout
   - number of panels or bands
   - relative grouping of information
   - alignment and reading order
   - narrative hierarchy across panels or bands
   - which panel or band should receive the most visual weight

4. **Connection layer**
   - where arrows are necessary
   - where alignment or grouping should replace arrows
   - primary vs secondary connector hierarchy
   - whether the structure should be linear, branching, merging, parallel, or mapping-based
   - how to avoid clutter and spider-web connectors

5. **Visual semantics layer**
   - color meaning per pathway or concept
   - which elements should be emphasized
   - which elements should stay neutral

6. **Typography and labeling layer**
   - short labels only
   - clean scientific sans-serif style
   - bold panel titles when needed
   - no decorative text treatment

7. **Venue-style layer**
   - include the chosen preset guidance explicitly

8. **Quality layer**
   - white background
   - publication-ready
   - vector-graphics look
   - flat design when appropriate
   - strict alignment
   - high readability
   - minimal clutter
   - disciplined connector usage
   - balanced layout and panel spacing

### Negative prompt requirements

The Negative prompt must explicitly suppress outputs that are visually incompatible with scientific paper figures.

The Negative prompt should usually include terms such as:

- low quality
- blurry text
- unreadable labels
- poster design
- marketing infographic
- cartoon
- comic style
- childish icons
- 3D rendering
- glossy UI
- neon colors
- sci-fi interface
- cluttered layout
- dark background
- heavy gradients
- dramatic shadows
- photographic realism
- messy arrows
- inconsistent alignment
- decorative background
- exaggerated icons
- slide deck style
- business infographic style
- flashy presentation
- hand-drawn style
- sketch style
- crowded composition
- illegible academic labels

### Final generation prompt rule

Construct the final generation prompt by combining these layers in order:

1. **User intent layer** — what the user actually wants drawn
2. **Category layer** — structural instructions for the detected category
3. **Venue-style layer** — one of the preset guidance blocks above
4. **Quality layer** — aspect ratio, clarity, white background, readability, publication quality, minimal clutter

Do not merely forward the raw user request. Rewrite it into a stronger research-figure generation prompt.
The backend script should receive the rewritten Positive prompt as its `--prompt` content.

## Bash command templates

### Text to image

```bash
python ~/.claude/skills/research-figure-edit/research_figure_edit.py \
  --mode text2image \
  --prompt "<user prompt>" \
  --aspect-ratio "<aspect ratio, e.g. 16:9>" \
  --clarity "<standard|high|ultra>" \
  --output-dir outputs/research-figure-edit \
  --save-raw-response
```

### Text + image to image

```bash
python ~/.claude/skills/research-figure-edit/research_figure_edit.py \
  --mode image2image \
  --prompt "<user prompt>" \
  --input "<local image path>" \
  --output-dir outputs/research-figure-edit \
  --save-raw-response
```

## Output behavior

The script completes the whole pipeline in one run:

- sends the generation request
- extracts generated image bytes from the JSON response
- saves the final image file directly
- optionally saves raw API response JSON

It prints the saved paths after completion.

When responding to the user after generation, also report:
- detected figure category
- selected venue-style preset
- Positive prompt
- Negative prompt
- any major prompt rewrite decisions (briefly)

## Notes

- For `image2image`, the input image is read locally and base64-encoded automatically.
- Supported input MIME types: PNG, JPG, JPEG.
- `--aspect-ratio` is supported for both modes.
- `--clarity` is supported for `text2image` and can be `standard`, `high`, or `ultra`.
- Use clear prompts such as:
  - `preserve the structure and improve visual consistency`
  - `convert into a clean Nature-style scientific figure`
  - `white background, paper-ready, minimal annotations`
- Before running the script, verify that at least one of `NANOBANANA_API_KEY` or `NANOBANANA_BEARER_TOKEN` is available in the environment. If not, ask the user to configure them.
- Even if the user only provides a short request, you must still run the preprocessing stage internally and expand it into detailed Positive and Negative prompts before generation.
