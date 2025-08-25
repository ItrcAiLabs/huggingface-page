import gradio as gr

with gr.Blocks() as demo:
    gr.HTML(
        """
        <h3>🖼️ تست نمایش لوگوها از static/brands</h3>
        <div style="display:flex; gap:20px; flex-wrap:wrap;">
            <div><img src="static/brands/openai.svg" width="64"><br>OpenAI</div>
            <div><img src="static/brands/anthropic.svg" width="64"><br>Anthropic</div>
            <div><img src="static/brands/google.svg" width="64"><br>Google</div>
            <div><img src="static/brands/meta.svg" width="64"><br>Meta</div>
            <div><img src="static/brands/qwen.webp" width="64"><br>Qwen</div>
            <div><img src="static/brands/mistral.svg" width="64"><br>Mistral</div>
            <div><img src="static/brands/deepseek.svg" width="64"><br>DeepSeek</div>
            <div><img src="static/brands/xai.svg" width="64"><br>xAI</div>
        </div>
        """
    )

if __name__ == "__main__":
    demo.launch()
