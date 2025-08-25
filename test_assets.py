import gradio as gr
from pathlib import Path
import base64
import mimetypes

ROOT = Path(__file__).parent
BRANDS = ROOT / "static" / "brands"

# نام فایل‌ها را دقیق با همان چیزی که در فضای شما هست بنویس
logos = [
    ("openai.svg",    "OpenAI"),
    ("anthropic.svg", "Anthropic"),
    ("google.svg",    "Google"),
    ("meta.svg",      "Meta"),
    ("qwen.webp",     "Qwen"),
    ("mistral.svg",   "Mistral"),
    ("deepseek.webp", "DeepSeek"),   # توجه: این یکی webp است
    ("xai.svg",       "xAI"),
]

def to_data_uri(path: Path) -> str:
    # MIME-type را از پسوند حدس می‌زنیم؛ اگر svg بود دستی ست می‌کنیم
    if path.suffix.lower() == ".svg":
        mime = "image/svg+xml"
    else:
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    b = path.read_bytes()
    b64 = base64.b64encode(b).decode("ascii")
    return f"data:{mime};base64,{b64}"

def render_logos_html() -> str:
    items = []
    for fname, label in logos:
        p = BRANDS / fname
        if not p.exists():
            # اگر فایلی نبود، یک جای‌نگهدار ساده نشان بده تا معلوم شود کدام غایب است
            items.append(
                f"""
                <figure style="text-align:center; margin:0; width:80px;">
                  <div style="width:56px;height:56px;border:1px dashed #ddd;display:flex;align-items:center;justify-content:center;font-size:10px;color:#888;">
                    missing
                  </div>
                  <figcaption style="font-size:12px;color:#555;margin-top:6px">{label}</figcaption>
                </figure>
                """
            )
            continue
        data_uri = to_data_uri(p)
        items.append(
            f"""
            <figure style="text-align:center; margin:0; width:80px;">
                <img src="{data_uri}" width="56" alt="{label}" draggable="false" style="user-select:none;-webkit-user-drag:none;pointer-events:none;" />
                <figcaption style="font-size:12px;color:#555;margin-top:6px">{label}</figcaption>
            </figure>
            """
        )
    return f"""
    <div style="display:flex; gap:20px; flex-wrap:wrap; align-items:center;">
        {''.join(items)}
    </div>
    """

with gr.Blocks() as demo:
    gr.Markdown("## 🖼️ لوگوها (بدون تعامل، با Data URI)")
    gr.HTML(render_logos_html())

if __name__ == "__main__":
    demo.launch()
