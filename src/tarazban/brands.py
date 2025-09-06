from pathlib import Path
import base64, mimetypes

# BRANDS_DIR = Path(__file__).parent / "static" / "brands"
BRANDS_DIR = Path(__file__).resolve().parents[2] / "static" / "brands"


BRAND_ICONS = {
    "OpenAI":    "openai.svg",
    "Anthropic": "anthropic.svg",
    "Google":    "google.svg",
    "Meta":      "meta.svg",
    "Qwen":      "qwen.webp",
    "Mistral":   "mistral.svg",
    "DeepSeek":  "deepseek.webp",   
    "xAI":       "xai.svg",
}

def _data_uri(p: Path) -> str:
    if p.suffix.lower() == ".svg":
        mime = "image/svg+xml"
    else:
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"

def make_brand_icon_css() -> str:
    rules = []
    for brand, fname in BRAND_ICONS.items():
        fp = BRANDS_DIR / fname
        if not fp.exists():
            continue
        uri = _data_uri(fp)
        # ساختار DOM: هر آیتم → div شامل input + label
        # پس div:has(input[value="..."]) > label::before را هدف می‌گیریم
        rules.append(
            f'''.brand-chips .gr-checkbox-group div:has(> input[value="{brand}"]) > label::before {{
                    background-image: url("{uri}");
                }}'''
        )
    return "<style>\n" + "\n".join(rules) + "\n</style>"
def make_brand_chip_css_by_id() -> str:
    id_map = {
        "brand_openai":   BRAND_ICONS["OpenAI"],
        "brand_anthropic":BRAND_ICONS["Anthropic"],
        "brand_google":   BRAND_ICONS["Google"],
        "brand_meta":     BRAND_ICONS["Meta"],
        "brand_qwen":     BRAND_ICONS["Qwen"],
        "brand_mistral":  BRAND_ICONS["Mistral"],
        "brand_deepseek": BRAND_ICONS["DeepSeek"],
        "brand_xai":      BRAND_ICONS["xAI"],
    }
    rules = []
    for elem_id, fname in id_map.items():
        fp = BRANDS_DIR / fname
        if not fp.exists():
            continue
        uri = _data_uri(fp)
        rules.append(
            f'''#{elem_id} label::before {{
                    content:"";
                    position:absolute;
                    left:12px; top:50%; transform:translateY(-50%);
                    width:20px; height:20px;
                    background-image:url("{uri}");
                    background-size:contain; background-repeat:no-repeat; background-position:center;
                }}'''
        )
    return "<style>\n" + "\n".join(rules) + "\n</style>"

def collect_brands(openai, anthropic, google, meta, qwen, mistral, deepseek, xai):
    selected = []
    if openai:   selected.append("OpenAI")
    if anthropic:selected.append("Anthropic")
    if google:   selected.append("Google")
    if meta:     selected.append("Meta")
    if qwen:     selected.append("Qwen")
    if mistral:  selected.append("Mistral")
    if deepseek: selected.append("DeepSeek")
    if xai:      selected.append("xAI")
    return selected