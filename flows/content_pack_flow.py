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