import json
from pathlib import Path

import streamlit as st

from flows.batch_content_flow import run_batch_content_packs


st.set_page_config(page_title="Batch Content Packs", page_icon="🖼️")
st.title("Batch Content Pack Generator")

st.write("Generate multiple image packs from a list of prompts and save a summary manifest.")

prompts_input = st.text_area(
    "Prompts (one per line)",
    value="A futuristic city at sunrise\nA cozy coffee shop in the rain\nA cyberpunk market at night",
)
watermark = st.text_input("Watermark", value="LangGraph")
outdir = st.text_input("Output directory", value="output")

if st.button("Generate Packs"):
    prompts = [line.strip() for line in prompts_input.splitlines() if line.strip()]
    if not prompts:
        st.warning("Enter at least one prompt before generating packs.")
    else:
        try:
            result = run_batch_content_packs(prompts, output_dir=outdir, watermark=watermark)
            st.success(f"Generated {result['total_packs']} packs.")
            batch_manifest = Path(result["batch_manifest_path"])
            st.write("Batch manifest:")
            st.code(batch_manifest.read_text(encoding="utf-8"), language="json")
        except Exception as exc:  # pragma: no cover - UI-level safety
            st.error(f"Generation failed: {exc}")
