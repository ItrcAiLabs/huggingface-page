import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("## 🖼️ تست لوگوها (assets/brands)")

    # هر لوگو رو مستقیم لود کن
    gr.HTML('<div style="display:flex; gap:20px; flex-wrap:wrap;">'
            '<div><img src="file=assets/brands/openai.svg" width="48"><br>OpenAI</div>'
            '<div><img src="file=assets/brands/anthropic.svg" width="48"><br>Anthropic</div>'
            '<div><img src="file=assets/brands/google.svg" width="48"><br>Google</div>'
            '<div><img src="file=assets/brands/meta.svg" width="48"><br>Meta</div>'
            '<div><img src="file=assets/brands/qwen.webp" width="48"><br>Qwen</div>'
            '<div><img src="file=assets/brands/mistral.svg" width="48"><br>Mistral</div>'
            '<div><img src="file=assets/brands/deepseek.svg" width="48"><br>DeepSeek</div>'
            '<div><img src="file=assets/brands/xai.svg" width="48"><br>xAI</div>'
            '</div>')

if __name__ == "__main__":
    demo.launch()
