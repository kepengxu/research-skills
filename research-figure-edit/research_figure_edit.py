import argparse
import base64
import http.client
import json
import mimetypes
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple
from urllib.parse import quote


DEFAULT_HOST = "api.vectorengine.ai"
DEFAULT_MODEL = "gemini-3-pro-image-preview"
SUPPORTED_MODES = ("text2image", "image2image")
SUPPORTED_MIME_TYPES = {"image/png", "image/jpeg"}
SUPPORTED_CLARITY_LEVELS = ("standard", "high", "ultra")


@dataclass(frozen=True)
class NanoBananaConfig:
    host: str
    model: str
    api_key: Optional[str]
    bearer_token: Optional[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate or edit research figures with text2image and image2image modes."
    )
    parser.add_argument(
        "--mode",
        choices=SUPPORTED_MODES,
        required=True,
        help="Generation mode: text2image or image2image.",
    )
    parser.add_argument("--prompt", required=True, help="Prompt for image generation.")
    parser.add_argument(
        "--input",
        help="Input image path. Required when --mode=image2image.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where raw responses and generated images are saved.",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="9:16",
        help="Image aspect ratio. Defaults to 9:16.",
    )
    parser.add_argument(
        "--image-size",
        default="1K",
        help="Image size. Defaults to 1K.",
    )
    parser.add_argument(
        "--clarity",
        choices=SUPPORTED_CLARITY_LEVELS,
        default="standard",
        help="Text-to-image clarity preset. Defaults to standard.",
    )
    parser.add_argument(
        "--save-raw-response",
        action="store_true",
        help="Save the raw JSON response to disk.",
    )
    return parser.parse_args()


def load_config_from_env() -> NanoBananaConfig:
    host = os.environ.get("NANOBANANA_HOST", DEFAULT_HOST)
    model = os.environ.get("NANOBANANA_MODEL", DEFAULT_MODEL)
    api_key = os.environ.get("NANOBANANA_API_KEY")
    bearer_token = os.environ.get("NANOBANANA_BEARER_TOKEN")

    if not api_key and not bearer_token:
        raise ValueError(
            "At least one of NANOBANANA_API_KEY or NANOBANANA_BEARER_TOKEN must be set."
        )

    return NanoBananaConfig(
        host=host,
        model=model,
        api_key=api_key,
        bearer_token=bearer_token,
    )


def validate_args(args: argparse.Namespace) -> None:
    if not args.prompt.strip():
        raise ValueError("--prompt must not be empty.")

    if args.mode == "image2image" and not args.input:
        raise ValueError("--input is required when --mode=image2image.")

    if args.input:
        input_path = Path(args.input)
        if not input_path.is_file():
            raise FileNotFoundError(f"Input image not found: {input_path}")

    if args.mode != "text2image" and args.clarity != "standard":
        raise ValueError("--clarity is only supported when --mode=text2image.")


def guess_mime_type(input_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(input_path)
    if mime_type not in SUPPORTED_MIME_TYPES:
        raise ValueError(
            f"Unsupported input image type for {input_path}. Supported types: PNG, JPG, JPEG."
        )
    return mime_type


def encode_image_to_base64(input_path: Path) -> str:
    return base64.b64encode(input_path.read_bytes()).decode("utf-8")


def apply_text2image_clarity(prompt: str, clarity: str) -> str:
    if clarity == "standard":
        return prompt
    if clarity == "high":
        return (
            f"{prompt} Render with high clarity, sharp edges, strong visual separation, "
            "clear labels, clean lines, and polished publication-quality detail."
        )
    return (
        f"{prompt} Render with ultra-high clarity, crisp typography, precise diagram structure, "
        "maximum legibility, clean boundaries, and strong publication-quality visual detail."
    )


def build_parts(
    prompt: str,
    mode: str,
    image_b64: Optional[str] = None,
    mime_type: Optional[str] = None,
) -> List[dict[str, Any]]:
    parts: List[dict[str, Any]] = [{"text": prompt}]

    if mode == "image2image":
        if image_b64 is None or mime_type is None:
            raise ValueError("image2image mode requires image_b64 and mime_type.")
        parts.append(
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_b64,
                }
            }
        )

    return parts


def build_payload(
    prompt: str,
    mode: str,
    aspect_ratio: str,
    image_size: str,
    clarity: str,
    image_b64: Optional[str] = None,
    mime_type: Optional[str] = None,
) -> dict[str, Any]:
    response_modalities = ["IMAGE"] if mode == "text2image" else ["TEXT", "IMAGE"]
    resolved_prompt = apply_text2image_clarity(prompt, clarity) if mode == "text2image" else prompt

    return {
        "contents": [
            {
                "role": "user",
                "parts": build_parts(
                    prompt=resolved_prompt,
                    mode=mode,
                    image_b64=image_b64,
                    mime_type=mime_type,
                ),
            }
        ],
        "generationConfig": {
            "responseModalities": response_modalities,
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": image_size,
            },
        },
    }


def build_headers(config: NanoBananaConfig) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if config.bearer_token:
        headers["Authorization"] = f"Bearer {config.bearer_token}"
    return headers


def build_request_path(config: NanoBananaConfig) -> str:
    encoded_model = quote(config.model, safe="")
    base_path = f"/v1beta/models/{encoded_model}:generateContent"
    if config.api_key:
        return f"{base_path}?key={quote(config.api_key, safe='')}"
    return base_path


def send_request(config: NanoBananaConfig, payload: dict[str, Any]) -> dict[str, Any]:
    connection = http.client.HTTPSConnection(config.host, timeout=60)
    encoded_payload = json.dumps(payload)
    path = build_request_path(config)
    headers = build_headers(config)

    try:
        connection.request("POST", path, encoded_payload, headers)
        response = connection.getresponse()
        raw_response = response.read().decode("utf-8")
    finally:
        connection.close()

    if response.status >= 400:
        raise RuntimeError(
            f"API request failed with status {response.status} {response.reason}: {raw_response}"
        )

    try:
        return json.loads(raw_response)
    except json.JSONDecodeError as error:
        raise ValueError(f"Failed to parse JSON response: {error}: {raw_response}") from error


def save_raw_response(output_dir: Path, stem: str, response_data: dict[str, Any]) -> Path:
    output_path = output_dir / f"{stem}_response.json"
    output_path.write_text(json.dumps(response_data, indent=2, ensure_ascii=False))
    return output_path


def iter_inline_images(response_data: Any) -> List[Tuple[str, bytes]]:
    images: List[Tuple[str, bytes]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            inline_data = node.get("inline_data") or node.get("inlineData")
            if isinstance(inline_data, dict):
                mime_type = inline_data.get("mime_type") or inline_data.get("mimeType")
                encoded_data = inline_data.get("data")
                if isinstance(mime_type, str) and isinstance(encoded_data, str):
                    try:
                        decoded_bytes = base64.b64decode(encoded_data, validate=True)
                    except (ValueError, TypeError):
                        decoded_bytes = base64.b64decode(encoded_data)
                    images.append((mime_type, decoded_bytes))
            for value in node.values():
                walk(value)
            return

        if isinstance(node, list):
            for item in node:
                walk(item)

    walk(response_data)
    return images


def extension_for_mime_type(mime_type: str) -> str:
    if mime_type == "image/png":
        return ".png"
    if mime_type == "image/jpeg":
        return ".jpg"
    return ".bin"


def extract_and_save_images(output_dir: Path, stem: str, response_data: dict[str, Any]) -> List[Path]:
    saved_paths: List[Path] = []
    for index, (mime_type, image_bytes) in enumerate(iter_inline_images(response_data), start=1):
        extension = extension_for_mime_type(mime_type)
        image_path = output_dir / f"{stem}_image_{index}{extension}"
        image_path.write_bytes(image_bytes)
        saved_paths.append(image_path)
    return saved_paths


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def build_output_stem(mode: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{mode}_{timestamp}"


def main() -> None:
    args = parse_args()
    validate_args(args)
    config = load_config_from_env()

    output_dir = Path(args.output_dir)
    ensure_output_dir(output_dir)

    image_b64: Optional[str] = None
    mime_type: Optional[str] = None
    if args.mode == "image2image":
        input_path = Path(args.input)
        mime_type = guess_mime_type(input_path)
        image_b64 = encode_image_to_base64(input_path)

    payload = build_payload(
        prompt=args.prompt,
        mode=args.mode,
        aspect_ratio=args.aspect_ratio,
        image_size=args.image_size,
        clarity=args.clarity,
        image_b64=image_b64,
        mime_type=mime_type,
    )
    response_data = send_request(config=config, payload=payload)

    stem = build_output_stem(args.mode)
    raw_response_path: Optional[Path] = None
    if args.save_raw_response:
        raw_response_path = save_raw_response(output_dir, stem, response_data)

    image_paths = extract_and_save_images(output_dir, stem, response_data)

    if not image_paths and raw_response_path is None:
        raw_response_path = save_raw_response(output_dir, stem, response_data)

    if raw_response_path is not None:
        print(f"Saved raw response to: {raw_response_path}")

    if image_paths:
        for image_path in image_paths:
            print(f"Saved generated image to: {image_path}")
    else:
        print("No inline image data found in the response. Consider checking the raw response.")


if __name__ == "__main__":
    main()
