"""Generate multiple content packs from a list of prompts."""
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional


PackRunner = Callable[..., Dict[str, Any]]

def _build_batch_manifest(packs: List[Dict[str, Any]], output_dir: str) -> Dict[str, Any]:
    manifest = {
        "output_dir": output_dir,
        "total_packs": len(packs),
        "packs": [
            {
                "pack_id": pack.get("pack_id", ""),
                "prompt": pack.get("prompt", ""),
                "final_image_path": pack.get("final_image_path", ""),
                "caption": pack.get("caption", ""),
                "hashtags": pack.get("hashtags", []),
                "alt_text": pack.get("alt_text", ""),
                "manifest_path": pack.get("manifest_path", ""),
            }
            for pack in packs
        ],
    }
    batch_manifest_path = os.path.join(output_dir, "batch_manifest.json")
    with open(batch_manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    manifest["batch_manifest_path"] = batch_manifest_path
    return manifest
