import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("## 🖼️ تست لوگوها از static/brands")
    gr.HTML("""
    <div style="display:flex; gap:20px; flex-wrap:wrap; align-items:center">
        <div><img src="/file=static/brands/openai.svg"    width="56"><br>OpenAI</div>
        <div><img src="/file=static/brands/anthropic.svg" width="56"><br>Anthropic</div>
        <div><img src="/file=static/brands/google.svg"    width="56"><br>Google</div>
        <div><img src="/file=static/brands/meta.svg"      width="56"><br>Meta</div>
        <div><img src="/file=static/brands/qwen.webp"     width="56"><br>Qwen</div>
        <div><img src="/file=static/brands/mistral.svg"   width="56"><br>Mistral</div>
        <div><img src="/file=static/brands/deepseek.svg"  width="56"><br>DeepSeek</div>
        <div><img src="/file=static/brands/xai.svg"       width="56"><br>xAI</div>
    </div>
    """)

if __name__ == "__main__":
    demo.launch()

# import gradio as gr
# from pathlib import Path

# ROOT = Path(__file__).parent
# BRANDS = ROOT / "static" / "brands"

# files = [
#     (BRANDS/"openai.svg").as_posix(),
#     (BRANDS/"anthropic.svg").as_posix(),
#     (BRANDS/"google.svg").as_posix(),
#     (BRANDS/"meta.svg").as_posix(),
#     (BRANDS/"qwen.webp").as_posix(),
#     (BRANDS/"mistral.svg").as_posix(),
#     (BRANDS/"deepseek.webp").as_posix(),
#     (BRANDS/"xai.svg").as_posix(),
# ]

# with gr.Blocks() as demo:
#     gr.Markdown("## 🖼️ تست لوگوها از static/brands (Components)")
#     gr.Gallery(
#         value=files,
#         label=None,
#         preview=True,
#         allow_preview=True,
#         columns=8,
#         height=140
#     )

# if __name__ == "__main__":
#     demo.launch()
