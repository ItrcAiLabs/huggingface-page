import gradio as gr
from pathlib import Path

ROOT = Path(__file__).parent  # همان ریشهٔ ریپو/Space
BRANDS = ROOT / "static" / "brands"

def logo(fname, label):
    # as_posix برای سازگاری با لینوکسی بودن Space
    return f'<div><img src="file={ (BRANDS / fname).as_posix() }" width="56"><br>{label}</div>'

with gr.Blocks() as demo:
    gr.Markdown("## 🖼️ تست نمایش لوگوها از static/brands")
    html = (
        '<div style="display:flex; gap:20px; flex-wrap:wrap; align-items:center;">'
        + logo("openai.svg", "OpenAI")
        + logo("anthropic.svg", "Anthropic")
        + logo("google.svg", "Google")
        + logo("meta.svg", "Meta")
        + logo("qwen.webp", "Qwen")
        + logo("mistral.svg", "Mistral")
        + logo("deepseek.svg", "DeepSeek")
        + logo("xai.svg", "xAI")
        + '</div>'
    )
    gr.HTML(html)

if __name__ == "__main__":
    demo.launch()
