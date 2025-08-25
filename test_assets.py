import gradio as gr
from pathlib import Path

ROOT = Path(__file__).parent
BRANDS = ROOT / "static" / "brands"

files = [
    (BRANDS/"openai.svg").as_posix(),
    (BRANDS/"anthropic.svg").as_posix(),
    (BRANDS/"google.svg").as_posix(),
    (BRANDS/"meta.svg").as_posix(),
    (BRANDS/"qwen.webp").as_posix(),
    (BRANDS/"mistral.svg").as_posix(),
    (BRANDS/"deepseek.webp").as_posix(),
    (BRANDS/"xai.svg").as_posix(),
]

with gr.Blocks() as demo:
    gr.Markdown("## 🖼️ تست لوگوها از static/brands (Components)")
    gr.Gallery(
        value=files,
        label=None,
        preview=True,
        allow_preview=True,
        columns=8,
        height=140
    )

if __name__ == "__main__":
    demo.launch()
