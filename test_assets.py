import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("## 🖼️ تست لوگوها از static/brands (HTML)")
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
