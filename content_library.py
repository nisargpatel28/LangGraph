"""Command-line browser and exporter for generated content packs."""
import argparse

from flows.library_flow import browse_library


def main() -> None:
    parser = argparse.ArgumentParser(description="Browse and export generated content packs.")
    parser.add_argument("--root", default="output", help="Content-pack directory")
    parser.add_argument("--query", default="", help="Search prompt, caption, alt text, or hashtag")
    parser.add_argument("--export", help="Optional ZIP path for matching packs")
    args = parser.parse_args()

    result = browse_library(args.root, query=args.query, export_path=args.export)
    print(f"Found {result['total']} pack(s).")
    for pack in result["packs"]:
        print(f"- {pack['pack_id']}: {pack['prompt']}")
    if result.get("export_path"):
        print(f"Exported to: {result['export_path']}")


if __name__ == "__main__":
    main()
