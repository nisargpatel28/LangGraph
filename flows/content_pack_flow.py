"""Create a reusable content pack from the existing agentic image flow."""
import json
import os
import uuid
from typing import Any, Callable, Dict, Optional

import openai

from models.content_pack import ContentPack
from storage.artifact_store import ArtifactStore
from flows.agentic_image_flow import make_flow

TextGenerator = Callable[[str], str]
ImageFlow = Callable[[Dict[str, Any]], Dict[str, Any]]


def _parse_metadata(text: str) -> Dict[str, Any]:
    """Parse model metadata while tolerating fenced JSON responses."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        metadata = json.loads(cleaned)
    except (TypeError, json.JSONDecodeError):
        return {"caption": cleaned, "hashtags": []}

    hashtags = metadata.get("hashtags", [])
    if isinstance(hashtags, str):
        hashtags = [tag.strip() for tag in hashtags.split() if tag.strip()]
    return {
        "caption": str(metadata.get("caption", "")),
        "hashtags": [str(tag) for tag in hashtags],
    }


def _openai_text_generator(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Create social media metadata and respond only with JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=180,
        temperature=0.7,
    )
    return response["choices"][0]["message"]["content"]


def run_content_pack(
    prompt: str,
    output_dir: str = "output",
    watermark: str = "LangGraph",
    image_flow: Optional[ImageFlow] = None,
    text_generator: Optional[TextGenerator] = None,
    store: Optional[ArtifactStore] = None,
) -> Dict[str, Any]:
    """Run image generation and persist the resulting content pack."""
    if not prompt.strip():
        raise ValueError("prompt must not be empty")

    os.makedirs(output_dir, exist_ok=True)
    image_flow = image_flow or make_flow().run
    text_generator = text_generator or _openai_text_generator
    store = store or ArtifactStore()

    image_result = image_flow(
        {"prompt": prompt, "output_dir": output_dir, "watermark": watermark}
    )
    metadata_prompt = (
        "Create a concise caption and 3 to 5 relevant hashtags for this creative image. "
        "Return JSON with string key 'caption' and array key 'hashtags'.\n"
        f"Original prompt: {prompt}\n"
        f"Image description: {image_result.get('content', '')}"
    )
    metadata = _parse_metadata(text_generator(metadata_prompt))

    pack = ContentPack(
        pack_id=uuid.uuid4().hex[:12],
        prompt=prompt,
        blurb=image_result.get("content", ""),
        image_prompt=image_result.get("image_prompt", prompt),
        final_image_path=image_result["final_image_path"],
        alt_text=image_result.get("alt_text", ""),
        caption=metadata["caption"],
        hashtags=metadata["hashtags"],
    )
    saved = store.save_pack(pack, output_dir)
    return {**image_result, **saved["pack"].to_dict(), "manifest_path": saved["manifest_path"]}
