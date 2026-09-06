"""Command-line browser and exporter for generated content packs."""
import argparse
import html
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from flows.library_flow import browse_library


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
        hashtags = " ".join(html.escape(tag) for tag in pack["hashtags"])
        cards.append(
            "<article>"
            f'<img src="{html.escape(image_href)}" alt="{html.escape(pack["alt_text"])}">'
            f'<h2>{html.escape(pack["pack_id"])}</h2>'
            f'<p>{html.escape(pack["caption"] or pack["prompt"])}</p>'
            f'<small>{hashtags}</small>'
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
    parser.add_argument("--export", help="Optional ZIP path for matching packs")
    parser.add_argument("--report", help="Optional HTML gallery path for matching packs")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    args = parser.parse_args()

    result = browse_library(
        args.root,
        query=args.query,
        pack_ids=args.pack_id,
        export_path=args.export,
    )
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
