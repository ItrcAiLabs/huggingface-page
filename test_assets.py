import gradio as gr

logos = [
    ("openai.svg",    "OpenAI"),
    ("anthropic.svg", "Anthropic"),
    ("google.svg",    "Google"),
    ("meta.svg",      "Meta"),
    ("qwen.webp",     "Qwen"),
    ("mistral.svg",   "Mistral"),
    ("deepseek.svg",  "DeepSeek"),
    ("xai.svg",       "xAI"),
]

def render_logos():
    items = []
    for fname, label in logos:
        items.append(
            f"""
            <figure style="text-align:center; margin:0;">
                <img src="/file=static/brands/{fname}" width="56" alt="{label}" draggable="false" />
                <figcaption style="font-size:12px;color:#555;margin-top:6px">{label}</figcaption>
            </figure>
            """
        )
    return f"""
    <style>
      /* بدون امکان انتخاب/درگ یا کلیک */
      .logo-grid img {{
        user-select: none;
        -webkit-user-drag: none;
        pointer-events: none;
      }}
    </style>
    <div class="logo-grid" style="display:flex; gap:20px; flex-wrap:wrap; align-items:center;">
        {''.join(items)}
    </div>
    """

with gr.Blocks() as demo:
    gr.Markdown("## 🖼️ لوگوها (نمایش ساده، بدون تعامل)")
    gr.HTML(render_logos())

if __name__ == "__main__":
    demo.launch()
