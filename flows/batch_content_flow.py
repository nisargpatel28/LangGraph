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

def run_batch_content_packs(
    prompts: Iterable[str],
    output_dir: str = "output",
    watermark: str = "LangGraph",
    pack_runner: Optional[PackRunner] = None,
) -> Dict[str, Any]:
    """Create a batch of content packs and write a summary manifest."""
    prompt_list = [prompt.strip() for prompt in prompts if str(prompt).strip()]
    if not prompt_list:
        raise ValueError("prompts must contain at least one non-empty value")

    os.makedirs(output_dir, exist_ok=True)

    if pack_runner is None:
        from flows.content_pack_flow import run_content_pack

        def pack_runner(prompt: str, output_dir: str, watermark: str, **kwargs):
            return run_content_pack(prompt, output_dir=output_dir, watermark=watermark, **kwargs)

    results: List[Dict[str, Any]] = []
    for prompt in prompt_list:
        result = pack_runner(prompt=prompt, output_dir=output_dir, watermark=watermark)
        results.append(result)

    manifest = _build_batch_manifest(results, output_dir)
    return {"packs": results, "batch_manifest_path": manifest["batch_manifest_path"], "total_packs": len(results)}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate multiple content packs from a list of prompts.")
    parser.add_argument("--prompts", nargs="+", required=True, help="One or more creative prompts")
    parser.add_argument("--outdir", default="output", help="Output directory")
    parser.add_argument("--watermark", default="LangGraph", help="Watermark text")
    args = parser.parse_args()

    run_batch_content_packs(args.prompts, output_dir=args.outdir, watermark=args.watermark)
