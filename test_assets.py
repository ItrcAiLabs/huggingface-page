import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("## 🖼️ تست لوگوها (static/brands)")

    gr.HTML(
        '<div style="display:flex; gap:20px; flex-wrap:wrap;">'
        '<div><img src="static/brands/openai.svg" width="48"><br>OpenAI</div>'
        '<div><img src="static/brands/anthropic.svg" width="48"><br>Anthropic</div>'
        '<div><img src="static/brands/google.svg" width="48"><br>Google</div>'
        '<div><img src="static/brands/meta.svg" width="48"><br>Meta</div>'
        '<div><img src="static/brands/qwen.webp" width="48"><br>Qwen</div>'
        '<div><img src="static/brands/mistral.svg" width="48"><br>Mistral</div>'
        '<div><img src="static/brands/deepseek.svg" width="48"><br>DeepSeek</div>'
        '<div><img src="static/brands/xai.svg" width="48"><br>xAI</div>'
        '</div>'
    )

if __name__ == "__main__":
    demo.launch()
