"""Command-line browser and exporter for generated content packs."""
import argparse
import html
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from flows.library_flow import browse_library


def filter_packs(
    packs: List[Dict[str, Any]],
    hashtags: Optional[List[str]] = None,
    sort_by: str = "pack_id",
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Apply exact hashtag filtering, stable sorting, and an optional limit."""
    selected = packs
    required_tags = {tag.lower().lstrip("#") for tag in (hashtags or [])}
    if required_tags:
        selected = [
            pack
            for pack in selected
            if required_tags.issubset(
                {tag.lower().lstrip("#") for tag in pack.get("hashtags", [])}
            )
        ]

    selected = sorted(selected, key=lambda pack: str(pack.get(sort_by, "")).lower())
    return selected[:limit] if limit is not None else selected


def build_stats(packs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return compact totals and hashtag counts for the selected packs."""
    tag_counts = Counter(
        tag.lower() for pack in packs for tag in pack.get("hashtags", [])
    )
    return {
        "total": len(packs),
        "with_images": sum(bool(pack.get("image_path")) for pack in packs),
        "hashtags": dict(tag_counts.most_common()),
    }


def write_html_report(packs: List[Dict[str, Any]], report_path: str) -> str:
    """Write a browsable HTML gallery for the selected packs."""
    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    cards = []
    for pack in packs:
        image_path = Path(pack["image_path"])
        try:
            image_href = os.path.relpath(image_path, destination.parent)
        except ValueError:
            image_href = str(image_path)
        manifest_path = Path(pack.get("manifest_path", ""))
        try:
            manifest_href = os.path.relpath(manifest_path, destination.parent)
        except ValueError:
            manifest_href = str(manifest_path)
        hashtags = " ".join(html.escape(tag) for tag in pack["hashtags"])
        cards.append(
            "<article>"
            f'<img src="{html.escape(image_href)}" alt="{html.escape(pack["alt_text"])}">'
            f'<h2>{html.escape(pack["pack_id"])}</h2>'
            f'<p>{html.escape(pack["caption"] or pack["prompt"])}</p>'
            f'<small>{hashtags}</small>'
            f'<p><a href="{html.escape(manifest_href)}">View manifest</a></p>'
            "</article>"
        )
    document = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Content Pack Library</title>
<style>body{font-family:system-ui;margin:2rem;background:#f5f5f5}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}article{background:white;padding:1rem;border-radius:8px;box-shadow:0 1px 4px #bbb}img{width:100%;aspect-ratio:1;object-fit:cover;background:#eee}h2{font-size:1rem;margin-bottom:.5rem}small{color:#555}</style>
</head><body><h1>Content Pack Library</h1><main>""" + "".join(cards) + "</main></body></html>"
    destination.write_text(document, encoding="utf-8")
    return str(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description="Browse, filter, and export generated content packs.")
    parser.add_argument("--root", default="output", help="Content-pack directory")
    parser.add_argument("--query", default="", help="Search prompt, caption, alt text, or hashtag")
    parser.add_argument("--pack-id", action="append", help="Limit results to a pack ID; repeat for multiple IDs")
    parser.add_argument("--hashtag", action="append", help="Require a hashtag; repeat to require multiple tags")
    parser.add_argument("--sort", choices=("pack_id", "prompt", "caption"), default="pack_id")
    parser.add_argument("--limit", type=int, help="Limit the number of displayed packs")
    parser.add_argument("--export", help="Optional ZIP path for matching packs")
    parser.add_argument("--report", help="Optional HTML gallery path for matching packs")
    parser.add_argument("--stats", action="store_true", help="Show summary statistics")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be greater than zero")

    result = browse_library(
        args.root,
        query=args.query,
        pack_ids=args.pack_id,
    )
    result["packs"] = filter_packs(result["packs"], args.hashtag, args.sort, args.limit)
    result["total"] = len(result["packs"])
    if args.stats:
        result["stats"] = build_stats(result["packs"])
    if args.export and result["packs"]:
        exported = browse_library(
            args.root,
            query=args.query,
            pack_ids=[pack["pack_id"] for pack in result["packs"]],
            export_path=args.export,
        )
        result["export_path"] = exported["export_path"]
    if args.report:
        result["report_path"] = write_html_report(result["packs"], args.report)

    if args.format == "json":
        print(json.dumps(result, indent=2))
        return

    print(f"Found {result['total']} pack(s).")
    for pack in result["packs"]:
        print(f"- {pack['pack_id']}: {pack['prompt']}")
    if result.get("export_path"):
        print(f"Exported to: {result['export_path']}")
    if result.get("report_path"):
        print(f"Report written to: {result['report_path']}")


if __name__ == "__main__":
    main()
