"""Run the agentic image flow from the command line.

Usage:
    python run_flow.py --prompt "your prompt" --outdir output
"""
import argparse
import os
from flows.agentic_image_flow import make_flow


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True, help="Concept prompt for content + image")
    p.add_argument("--outdir", default="output", help="Output directory")
    p.add_argument("--watermark", default="© LangGraph", help="Watermark text")
    args = p.parse_args()

    flow = make_flow()
    ctx = {"prompt": args.prompt, "output_dir": args.outdir, "watermark": args.watermark}
    out = flow.run(ctx)
    print("Flow completed. Results:")
    for k, v in out.items():
        print(f"- {k}: {v}")


if __name__ == "__main__":
    main()
