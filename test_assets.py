import gradio as gr
from pathlib import Path

ROOT = Path(__file__).parent
BRANDS = ROOT / "static" / "brands"

with gr.Blocks() as demo:
    gr.Markdown("## 🖼️ تست نمایش لوگوها از static/brands")

    # لینک تست باز کردن فایل
    gr.HTML(f'<p><a href="file={(BRANDS / "openai.svg").as_posix()}" target="_blank">بازکردن openai.svg</a></p>')

    # نمایش همه لوگوها
    html = (
        '<div style="display:flex; gap:20px; flex-wrap:wrap;">'
        f'<div><img src="file={(BRANDS / "openai.svg").as_posix()}" width="56"><br>OpenAI</div>'
        f'<div><img src="file={(BRANDS / "anthropic.svg").as_posix()}" width="56"><br>Anthropic</div>'
        f'<div><img src="file={(BRANDS / "google.svg").as_posix()}" width="56"><br>Google</div>'
        '</div>'
    )
    gr.HTML(html)

if __name__ == "__main__":
    demo.launch()
