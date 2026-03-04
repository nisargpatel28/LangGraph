"""
An agentic flow that: creates content from a prompt, produces an image
from the content, post-processes the image (resize + watermark), and
generates an alt-text description.

Requires: `openai` and `Pillow`.
Environment variables: `OPENAI_API_KEY`.
"""
import os
import io
import base64
import json
from typing import Dict
from PIL import Image, ImageDraw, ImageFont
import openai

from langgraph_sdk import Flow, node


def _save_b64_image(b64: str, out_path: str):
    data = base64.b64decode(b64)
    with open(out_path, "wb") as f:
        f.write(data)


def _add_watermark(image_path: str, text: str, out_path: str, opacity: float = 0.8):
    im = Image.open(image_path).convert("RGBA")
    txt = Image.new("RGBA", im.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    margin = 10
    w, h = draw.textsize(text, font=font)
    x = im.width - w - margin
    y = im.height - h - margin
    draw.text((x, y), text, fill=(255,255,255,int(255*opacity)), font=font)
    out = Image.alpha_composite(im, txt).convert("RGB")
    out.save(out_path, quality=95)


def make_flow() -> Flow:
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise EnvironmentError("Set OPENAI_API_KEY in environment")
    openai.api_key = openai_api_key

    flow = Flow("agentic-image-flow")

    @node("create_content")
    def create_content(ctx: Dict) -> Dict:
        prompt = ctx.get("prompt")
        if not prompt:
            return {"content": ""}
        # Generate a short content piece and an image prompt
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"system","content":"You are an assistant that writes short visual descriptions and an image prompt."},
                      {"role":"user","content": f"Write a short creative blurb and a concise image generation prompt for: {prompt}. Respond as JSON with keys 'blurb' and 'image_prompt'."}],
            max_tokens=300,
            temperature=0.9,
        )
        text = resp["choices"][0]["message"]["content"].strip()
        # Try to parse JSON out of the model output
        blurb = ""
        image_prompt = prompt
        try:
            parsed = json.loads(text)
            blurb = parsed.get("blurb", "")
            image_prompt = parsed.get("image_prompt", prompt)
        except Exception:
            blurb = text
        return {"content": blurb, "image_prompt": image_prompt}

    @node("generate_image")
    def generate_image(ctx: Dict) -> Dict:
        img_prompt = ctx.get("image_prompt")
        out_dir = ctx.get("output_dir", "output")
        os.makedirs(out_dir, exist_ok=True)
        # Use OpenAI Images API (may vary by client version)
        resp = openai.Image.create(
            prompt=img_prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json",
        )
        b64 = resp["data"][0]["b64_json"]
        raw_path = os.path.join(out_dir, "raw_image.png")
        _save_b64_image(b64, raw_path)
        return {"raw_image_path": raw_path}

    @node("post_process")
    def post_process(ctx: Dict) -> Dict:
        raw = ctx.get("raw_image_path")
        out_dir = ctx.get("output_dir", "output")
        final_path = os.path.join(out_dir, "final_image.jpg")
        # Resize to max 1024 and add watermark
        im = Image.open(raw)
        im.thumbnail((1024, 1024))
        tmp_path = os.path.join(out_dir, "tmp_resized.jpg")
        im.convert("RGB").save(tmp_path, quality=95)
        watermark_text = ctx.get("watermark", "© LangGraph")
        _add_watermark(tmp_path, watermark_text, final_path)
        return {"final_image_path": final_path}

    @node("generate_alt")
    def generate_alt(ctx: Dict) -> Dict:
        final = ctx.get("final_image_path")
        if not final:
            return {"alt_text": ""}
        # Describe the image briefly
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"system","content":"You are an assistant that writes concise alt text for images."},
                      {"role":"user","content": f"Write a one-sentence alt text describing the image generated from: {ctx.get('image_prompt')}. Keep it under 20 words."}],
            max_tokens=60,
            temperature=0.3,
        )
        alt = resp["choices"][0]["message"]["content"].strip()
        return {"alt_text": alt}

    flow.add_node(create_content)
    flow.add_node(generate_image)
    flow.add_node(post_process)
    flow.add_node(generate_alt)

    return flow


if __name__ == "__main__":
    f = make_flow()
    ctx = {"prompt": "A futuristic city at sunrise with flying cars and neon trees", "output_dir": "output"}
    out = f.run(ctx)
    print("Flow output:", out)
