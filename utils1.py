import pandas as pd
import json
import os
import uuid
from datetime import datetime
import pytz
from datasets import load_dataset, Dataset

FIXED_COLUMNS = ["model", "params", "license", "precision", "type"]


# ---------------- Task Groups ----------------
TASK_GROUPS = {
    "SBU": [
        "General Medicine",
        "Complementary & Alternative Medicine",
        "Emergency Medicine",
        "Constitution of IRI",
        "Other legal Domains",
        "Religion",
        "Grammar, Proverbs & Strings",
        "Lexical Semantics",
        "Encyclopedic Knowledge",
        "Recommendation & Human Preferences",
        "Text Completion",
        "Poems & Lyrics",
        "Paraphrase",
        "Style Transfer",
        "Emotion",
        "Irony",
        "Metaphor",
        "Empathy, Intimacy & Trust",
        "Ethics & Bias",
        "Toxicity",
        "Human Rights",
    ],
    "UQ": [
        "belebel_e",
        "farstail",
        "pn_summary_categorization",
        "pn_summary_summarize",
        "Parsinlu_translation_fa_en",
        "Parsinlu_translation_en_fa",
        "persian_MMLU",
        "ARC_easy",
        "ARC_challenge",
    ],
    "AUT": []
}
# ---------------- Style ----------------
HTML_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600&family=Poppins:wght@500;700&display=swap');

    body, table {
        font-family: 'Vazirmatn', 'Poppins', sans-serif;
    }
    .main-title {
    font-family: 'Poppins', 'Vazirmatn', sans-serif;
    font-size: 34px;
    font-weight: 500;
    color: #222;
    text-align: center;
    margin: 10px 0 20px 0;
}

    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        border: 1px solid #f5f5f5;
    }
    .styled-table th {
        background-color: #fafafa;
        font-weight: 600;
        padding: 8px 10px;
        border: 1px solid #f3f3f3;
        text-align: center;
        font-size: 12px;
    }
    .styled-table td {
        padding: 6px 8px;
        border: 1px solid #f3f3f3;
        font-size: 12px;
        color: #222;
        text-align: center;
        background-repeat: no-repeat;
        background-size: 100% 100%;
    }
    .styled-table tr:nth-child(even) {
        background-color: #fcfcfc;
    }
    .styled-table tr:hover {
        background-color: #f1f7ff;
    }
    .model-col a {
        color: #0066cc;
        text-decoration: none;
        font-weight: 500;
    }
    .model-col a:hover {
        text-decoration: underline;
    }
</style>
"""
SMALL_PARAMS_B = 9
CONTEXT_RANGE_CHOICES = ["No Filter", "0–16K", "16K–32K", "32K–128K", "128K–500K", "500K+"]
from pathlib import Path
import base64, mimetypes

BRANDS_DIR = Path(__file__).parent / "static" / "brands"

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

def ctx_to_int(x):
    if pd.isna(x):
        return -1
    s = str(x).strip().lower().replace(" ", "")
    try:
        if s.endswith("m"):
            return int(float(s[:-1]) * 1_000_000)
        if s.endswith("k"):
            return int(float(s[:-1]) * 1_000)
        return int(float(s))
    except:
        return -1

def apply_quick_filters(df: pd.DataFrame, quick: list, brands: list, ctx_range: str | None = None) -> pd.DataFrame:
    out = df.copy()

    # Open-source
    if "Open Models" in quick and "OpenSource" in out.columns:
        out = out[out["OpenSource"] == True]

    # Small models
    if f"Small Models (<{SMALL_PARAMS_B}B)" in quick:
        col = next((c for c in ["#Params (B)","Params (B)","Parameters (B)"] if c in out.columns), None)
        if col:
            v = pd.to_numeric(out[col], errors="coerce").fillna(1e9)
            out = out[v < SMALL_PARAMS_B]

    # Brands
    if brands and "Brand" in out.columns:
        out = out[out["Brand"].isin(brands)]

    # Context range
# Context range
    if ctx_range and ctx_range != "No Filter":
        col = next((c for c in ["Input Context Length","Context Length","Max Context","Context"] if c in out.columns), None)
        if col:
            v = out[col].apply(ctx_to_int)
            if ctx_range == "0–16K":
                out = out[(v >= 0) & (v < 16_000)]
            elif ctx_range == "16K–32K":
                out = out[(v >= 16_000) & (v < 32_000)]
            elif ctx_range == "32K–128K":
                out = out[(v >= 32_000) & (v < 128_000)]
            elif ctx_range == "128K–500K":
                out = out[(v >= 128_000) & (v < 500_000)]
            elif ctx_range == "500K+":
                out = out[(v >= 500_000)]
    return out

def make_pipeline_filter(current_df: pd.DataFrame, table_id: str):
    def _fn(search_text: str, task_cols: list, quick: list, brands: list, ctx_range: str | None):
        df1 = apply_quick_filters(current_df, quick or [], brands or [], ctx_range)
        return filter_table(search_text, task_cols, df1, table_id=table_id)
    return _fn
def add_organization_column(df: pd.DataFrame) -> pd.DataFrame:
    if "Organization" not in df.columns:
        df["Organization"] = df["Model"].apply(
            lambda m: str(m).split("/")[0].lower() if "/" in str(m) else str(m).lower()
        )
        df["Brand"] = df["Organization"].map(lambda o: ORG_TO_BRAND.get(o, o.title()))
        df["OpenSource"] = df["Organization"].map(lambda o: OPEN_ORGS.get(o, False))
    return df
ORG_TO_BRAND = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google": "Google",
    "gemma": "Google",        # بعضی مدل‌ها فقط gemma دارن
    "meta": "Meta",
    "meta-llama": "Meta",
    "nousresearch": "Meta",   # چون Llama هست
    "qwen": "Qwen",
    "mistral": "Mistral",
    "deepseek": "DeepSeek",
    "xai": "xAI",
    "coherelabs": "Cohere",
    "cohereforai": "Cohere",
    "microsoft": "Microsoft",
    "ibm-granite": "IBM",
    "frameai": "FrameAI",
    "mehdihosseinimoghadam": "Independent",
    "maralgpt": "Independent",
}

OPEN_ORGS = {
    "openai": False,        # بسته
    "anthropic": False,     # بسته
    "google": False,        # gemini بسته است
    "gemma": True,          # gemma اوپن‌سورس
    "meta": True,           # llama اوپن‌سورس
    "meta-llama": True,
    "nousresearch": True,   # روی llama سوار شده
    "qwen": True,
    "mistral": True,
    "deepseek": True,
    "xai": False,
    "coherelabs": True,    # بسته
    "cohereforai": True,    # aya اوپن
    "microsoft": True,      # phi اوپن
    "ibm-granite": True,
    "frameai": True,
    "mehdihosseinimoghadam": True,
    "maralgpt": True,
}


# df_sbu = df_sbu.loc[df_sbu[TASK_GROUPS["SBU"]].notna().any(axis=1)]
# df_uq  = df_uq.loc[df_uq[TASK_GROUPS["UQ"]].notna().any(axis=1)]
# df_aut = df_aut.loc[df_aut[TASK_GROUPS["AUT"]].notna().any(axis=1)]

# df_sbu = dfs["SBU"]
# df_uq  = dfs["UQ"]
# df_aut = dfs["AUT"]

# ---------------- Custom CSS ----------------
CUSTOM_CSS = """
/* ====== Global ====== */
body, .gradio-container {
    font-family: 'Raleway','Vazirmatn',sans-serif !important;
    background: #f9fafb !important;
    color: #111827;
}
/* ====== Navbar ====== */
.navbar {
    background: linear-gradient(90deg, #1e40af, #2563eb);
    padding: 14px 30px;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #1e3a8a;
}
.navbar-title {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 1px;
}
.navbar-links a {
    color: white;
    margin: 0 12px;
    font-size: 15px;
    font-weight: 600;
    text-decoration: none;
}
.navbar-links a:hover {
    text-decoration: underline;
}
/* ====== Titles ====== */
.main-title {
  text-align: center;
  font-size: 48px;
  font-weight: 900;
  letter-spacing: 1.5px;
  background: linear-gradient(90deg, #1e3a8a, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 30px 0 10px 0;
  animation: fadeInDown 1s ease;
}
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
.section-title {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #1e3a8a !important;
    margin: 20px 0 10px 0;
}
/* ====== Search Box ====== */
.search-box input {
    border: 2px solid #3b82f6 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-size: 15px !important;
    transition: all 0.25s ease;
}
.search-box input:focus {
    border-color: #1e3a8a !important;
    box-shadow: 0 0 8px rgba(30,58,138,0.3);
}
/* ====== Task Selector ====== */
.task-box label {
    font-size: 14px !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    padding: 6px 12px !important;
    background: #f3f4f6 !important;
    border: 1px solid #e5e7eb !important;
    transition: all 0.2s ease;
}
.task-box label:hover {
    background: #e0e7ff !important;
    border-color: #3b82f6 !important;
}
/* ====== Table ====== */
.table-wrapper { 
    border: 1px solid #e9ecef !important; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    background: #fff !important;
}
.table-wrapper table[border],
.table-wrapper table[style*="border"] {
    border: none !important;
}
.table-wrapper table,
.table-wrapper thead,
.table-wrapper tbody,
.table-wrapper tr,
.table-wrapper th,
.table-wrapper td {
    border: 0 !important;
    border-color: #e5e7eb !important;
}
.table-wrapper th { 
    border-bottom: 1px solid #e5e7eb !important; 
}
.table-wrapper td { 
    border-bottom: 1px solid #f0f0f0 !important; 
}
#leaderboard_sbu, 
#leaderboard_uq, 
#leaderboard_aut {
    border: none !important;
}
#leaderboard_sbu th, #leaderboard_uq th, #leaderboard_aut th {
    border-bottom: 1px solid #e5e7eb !important;
}
#leaderboard_sbu td, #leaderboard_uq td, #leaderboard_aut td {
    border-bottom: 1px solid #f0f0f0 !important;
}
.model-col {
    font-weight: 600;
    color: #2563eb;
}
.navbar { 
    display: none !important; 
}
.gradio-container {
    padding-top: 0 !important;   
}
.main-title {
    margin-top: 24px !important; 
}
.gradio-container [style*="resize"], 
.gradio-container .svelte-1ipelgc, 
.gradio-container .svelte-drgfj1 {
    resize: none !important;
    overflow: hidden !important;
}
::-webkit-scrollbar {
    display: none;
}
/* ====== Animation ====== */
@keyframes fadeIn {
    from {opacity:0; transform: translateY(6px);}
    to {opacity:1; transform: translateY(0);}
}
/* ===== Quick Filters Container ===== */
.quick-filters-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin: 8px 0 12px;
}
/* ====== Container: All filters in one box ====== */
.all-filters-box {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
/* ====== Pills (Quick + Brand filters) ====== */
.gr-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.gr-checkbox-group input { display: none; }
.gr-checkbox-group label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 9999px;
  background: #f3f4f6;
  color: #1e293b;
  border: 1px solid #e5e7eb;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all .2s;
}
.gr-checkbox-group label:hover { background: #e0e7ff; border-color: #93c5fd; }
.gr-checkbox-group input:checked + label {
  background: #4f46e5; color: #fff; border-color: #4f46e5;
}
/* ====== Context pill (label + dropdown) ====== */
.ctx-filter-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px;
  border: 1px solid #e5e7eb;
  border-radius: 9999px;
  background: #f9fafb;
  box-shadow: 0 1px 2px rgba(0,0,0,.04);
  height: 32px;
}
.mini-chip {
  font-weight: 600;
  font-size: 12px;
  color: #334155;
}
.ctx-range select,
.ctx-range button,
.ctx-range .wrap-inner {
  border: none !important;
  background: transparent !important;
  font-size: 13px !important;
  height: 26px !important;
  cursor: pointer !important;
}
/* همه‌ی فیلترها داخل یک باکس */
/* باکس کلی فیلترها */
.filters-box{
  display:flex; 
  flex-direction:column;  /* ستون: ردیف بالا + ردیف پایین */
  gap:12px;
  padding:12px; 
  border:1px solid #e5e7eb; 
  border-radius:12px;
  background:#fff; 
  box-shadow:0 1px 3px rgba(0,0,0,.04);
}
/* چیپ‌های چک‌باکسی (Quick + Brand) */
.gr-checkbox-group{
  display:flex; 
  flex-wrap:wrap; 
  gap:8px;
}
.gr-checkbox-group input{ display:none; }
.gr-checkbox-group label{
  display:inline-flex; 
  align-items:center; 
  gap:6px;
  padding:6px 12px; 
  border-radius:9999px;
  background:#eef2ff; 
  color:#1e293b; 
  border:1px solid #e5e7eb;
  font-weight:600; 
  font-size:13px; 
  cursor:pointer;
  transition:.2s;
}
.gr-checkbox-group label:hover{ background:#e0e7ff; border-color:#93c5fd; }
.gr-checkbox-group input:checked+label{
  background:#4f46e5; 
  color:#fff; 
  border-color:#4f46e5;
}
/* استایل لیبل Dropdown کانتکست */
.ctx-dd label{
  font-weight:600; 
  font-size:13px; 
  color:#334155; 
  margin-bottom:2px;
}
.ctx-dd select, .ctx-dd button, .ctx-dd .wrap-inner{
  border:1px solid #e5e7eb !important; 
  border-radius:8px !important;
  padding:4px 8px !important;
  font-size:13px !important; 
  background:#f9fafb !important;
  cursor:pointer !important;
}
/* ==== Brand chips (Clean) ==== */
/* ردیف برندها کنار هم */
.brand-row {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 6px !important;
  row-gap: 6px !important;
  margin: 0 !important;
  padding: 0 !important;
}
.brand-row > div {
  margin: 0 !important;
  padding: 0 !important;
  flex: 0 0 auto !important;
}
/* مخفی کردن مربع چک‌باکس پیش‌فرض */
[id^="brand_"] input[type="checkbox"] {
  position: absolute !important;
  opacity: 0 !important;
  pointer-events: none !important;
}
/* ظاهر پایهٔ چیپ */
[id^="brand_"] label {
  position: relative !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  padding: 6px 10px 6px 42px !important;  /* جا برای لوگو سمت چپ */
  border-radius: 9999px !important;
  background: #e0f2fe !important;
  color: #0369a1 !important;
  border: 1px solid #bae6fd !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  cursor: pointer !important;
  transition: background .2s, border-color .2s, color .2s, box-shadow .2s !important;
}
[id^="brand_"] label:hover {
  background: #bae6fd !important;
  border-color: #7dd3fc !important;
}
/* جای لوگو (خودِ تصویر در make_brand_chip_css_by_id() ست می‌شود) */
[id^="brand_"] label::before {
  content: "" !important;
  position: absolute !important;
  left: 12px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  width: 20px !important;
  height: 20px !important;
  background-size: contain !important;
  background-repeat: no-repeat !important;
  background-position: center !important;
}
/* حالت انتخاب‌شده — رنگ چیپ پررنگ شود */
[id^="brand_"] label:has(input:checked) {
  background: #0ea5e9 !important;
  color: #fff !important;
  border-color: #0284c7 !important;
  box-shadow: 0 0 0 2px rgba(2,132,199,.25) inset !important;
}
/* === Main Title (مشکی ساده با انیمیشن) === */
.hero .main-title {
  font-size: 46px;
  font-weight: 600;  
  text-align: center;
  margin: 20px 0 10px 0;
  font-family: 'Raleway','Vazirmatn',sans-serif;
  letter-spacing: 0.5px;
  color: #000 !important;          /* سیاه کامل */
  background: none !important;     /* گرادیان قبلی حذف بشه */
  -webkit-background-clip: initial !important;
  -webkit-text-fill-color: initial !important;
  animation: fadeInDown 1s ease-out;
}
/* === Subtitle (خاکستری، دو خطه با انیمیشن) === */
.hero .subtitle {
  font-size: 18px;
  font-weight: 500;
  color: #4b5563;   /* خاکستری مدرن */
  text-align: center;
  margin-top: 12px;
  line-height: 1.6;
  font-family: 'Raleway','Vazirmatn',sans-serif;
  max-width: 700px;       /* محدود کردن عرض برای شکستن به خط دوم */
  margin-left: auto;
  margin-right: auto;
  white-space: normal;    
  word-wrap: break-word;
  letter-spacing: 0.3px;
  animation: fadeInUp 1s ease-out;
}
/* ==== انیمیشن‌ها ==== */
@keyframes fadeInDown {
  from {opacity: 0; transform: translateY(-10px);}
  to   {opacity: 1; transform: translateY(0);}
}
@keyframes fadeInUp {
  from {opacity: 0; transform: translateY(10px);}
  to   {opacity: 1; transform: translateY(0);}
}
/* ===== Tabs Styling (Minimal Elegant, No underline) ===== */
.tabs.svelte-1tcem6n {
  display: flex !important;
  justify-content: center !important;
  gap: 20px !important;
  margin: 20px 0 !important;
  border: none !important; /* بدون خط زیر تب‌ها */
}
.tabs.svelte-1tcem6n button[role="tab"] {
  font-family: 'Vazirmatn','Raleway',sans-serif !important;
  font-size: 15px !important;
  font-weight: 500 !important;     
  padding: 8px 4px !important;
  background: transparent !important;
  color: #374151 !important;       /* خاکستری تیره */
  border: none !important;
  border-radius: 0 !important;
  cursor: pointer !important;
  transition: color .2s ease;
}
/* هاور */
.tabs.svelte-1tcem6n button[role="tab"]:hover {
  color: #2563eb !important;        /* آبی ملایم هنگام هاور */
}
/* تب فعال */
.tabs.svelte-1tcem6n button[role="tab"].selected {
  color: #1d4ed8 !important;        /* آبی پررنگ‌تر برای انتخاب */
  font-weight: 600 !important;
}
"""
def make_sort_func(col, df, table_id, ascending):
    def _ctx_to_int(x):
        if pd.isna(x):
            return -1
        s = str(x).strip().lower().replace(" ", "")
        try:
            if s.endswith("m"):   
                return int(float(s[:-1]) * 1_000_000)
            if s.endswith("k"):   
                return int(float(s[:-1]) * 1_000)
            return int(float(s))
        except:
            return -1

    def _sort():
        temp_df = df.copy()
        if col in temp_df.columns:
            if col.lower() == "context":
                temp_df["__ctxnum"] = temp_df[col].apply(_ctx_to_int)
                sorted_df = temp_df.sort_values(
                    by="__ctxnum", ascending=ascending, na_position="last"
                ).drop(columns="__ctxnum")
            else:
                temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
                sorted_df = temp_df.sort_values(
                    by=col, ascending=ascending, na_position="last"
                )
        else:
            sorted_df = temp_df
        return df_to_styled_html(sorted_df, table_id=table_id, active_col=col, ascending=ascending)
    return _sort

# ---------------- Load Data ----------------
def load_all_data(path: str):
    """Load results.jsonl and split into dataframes by task groups."""
    rows = []
    with open(os.path.join(path, "results.jsonl"), "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    df = pd.DataFrame(rows)

    base_cols = ["Model", "Precision", "#Params (B)", "Context"]
    dfs = {}

    for group, tasks in TASK_GROUPS.items():
        cols = base_cols + [col for col in tasks if col in df.columns]
        sub_df = df[cols].copy()

        for col in tasks:
            if col in sub_df.columns:
                sub_df[col] = pd.to_numeric(sub_df[col], errors="coerce")

        dfs[group] = sub_df

    return dfs
# ---------------- Load leaderboard data ----------------
dfs = load_all_data("data/")
df_sbu = add_organization_column(dfs["SBU"])
df_uq  = add_organization_column(dfs["UQ"])
df_aut = add_organization_column(dfs["AUT"])

def _keep_rows_with_any_scores(df: pd.DataFrame, group: str) -> pd.DataFrame:
    cols = [c for c in TASK_GROUPS[group] if c in df.columns]
    if cols:
        return df.loc[df[cols].notna().any(axis=1)]
    return df

df_sbu = _keep_rows_with_any_scores(df_sbu, "SBU")
df_uq  = _keep_rows_with_any_scores(df_uq,  "UQ")
df_aut = _keep_rows_with_any_scores(df_aut, "AUT")    
def sort_dataframe(df: pd.DataFrame, col: str, ascending: bool = True):
    if col in df.columns:
        return df.sort_values(by=col, ascending=ascending).reset_index(drop=True)
    return df

# ---------------- Gradient ----------------
def value_to_gradient_range(value: float, min_val: float = 0, max_val: float = 100) -> str:
    """
    Map value (0-100) to a pastel gradient background.
    Colors: pink → yellow → green (pastel).
    """
    ratio = (value - min_val) / (max_val - min_val)
    ratio = max(0, min(1, ratio))

    pink = (255, 179, 186)   # #ffb3ba
    yellow = (255, 245, 186) # #fff5ba
    green = (186, 255, 201)  # #baffc9

    if ratio < 0.5:
        # Pink → Yellow
        t = ratio / 0.5
        r = int(pink[0] + t * (yellow[0] - pink[0]))
        g = int(pink[1] + t * (yellow[1] - pink[1]))
        b = int(pink[2] + t * (yellow[2] - pink[2]))
    else:
        # Yellow → Green
        t = (ratio - 0.5) / 0.5
        r = int(yellow[0] + t * (green[0] - yellow[0]))
        g = int(yellow[1] + t * (green[1] - yellow[1]))
        b = int(yellow[2] + t * (green[2] - yellow[2]))

    return f"linear-gradient(90deg, rgba({r},{g},{b},0.4), rgba({r},{g},{b},0.9))"

# ---------------- Table Renderer ----------------
# def df_to_styled_html(df: pd.DataFrame, table_id: str = "leaderboard") -> str:
def df_to_styled_html(
    df: pd.DataFrame, 
    table_id: str = "leaderboard", 
    active_col=None, 
    ascending=None
) -> str:
    """Convert DataFrame into styled HTML leaderboard table with gradients and sortable headers (JS)."""
    if df.empty:
        return "<p>No results found.</p>"

    task_columns = [c for c in df.columns if c not in ["Model", "Precision", "#Params (B)", "License", "Organization", "Context"]]
    df = df.dropna(how="all", subset=task_columns)
    df = df[~df[task_columns].apply(lambda row: all(str(v) in ["--", "nan", "NaN"] for v in row), axis=1)]

    if "Model" in df.columns:
        def linkify(m):
            if isinstance(m, str) and "/" in m:
                if m.lower().startswith(("openai/", "anthropic/", "google/")):
                    return str(m)
                return f"<a href='https://huggingface.co/{m}' target='_blank'>{m}</a>"
            return str(m)
        df["Model"] = df["Model"].apply(linkify)

    # HTML Table
    html = HTML_STYLE
    html += f"<table id='{table_id}' class='styled-table'>"
    html += "<thead><tr>"

    for col in df.columns:
        if col.lower() in ["model", "precision", "license", "organization"]:
            html += f"<th>{col}</th>"
        else:
            up_color = "color:#999;"
            down_color = "color:#999;"
            if active_col == col:
                if ascending:
                    up_color = "color:#2563eb;font-weight:bold;"
                else:
                    down_color = "color:#2563eb;font-weight:bold;"

            html += f"""
            <th>
                {col}
                <button style='all:unset;cursor:pointer;' 
                        onclick="document.getElementById('{table_id}_{col}_asc').click()">
                    <span style='{up_color}'>&uarr;</span>
                </button>
                <button style='all:unset;cursor:pointer;' 
                        onclick="document.getElementById('{table_id}_{col}_desc').click()">
                    <span style='{down_color}'>&darr;</span>
                </button>
            </th>
            """

    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            value = row[col]
            if pd.isna(value) or str(value).lower() in ["nan", "none", "--"]:
                html += "<td>--</td>"
            elif isinstance(value, (int, float)):
                if col == "#Params (B)":
                    html += f"<td>{int(value)}</td>"
                else:
                    bg = value_to_gradient_range(value)
                    html += f"<td style='background:{bg};'>{value:.1f}</td>"
            else:
                if col == "Model":
                    html += f"<td class='model-col'>{value}</td>"
                else:
                    html += f"<td>{value}</td>"
        html += "</tr>"

    html += "</tbody></table>"
    # return html
    return f"<div class='table-wrapper'>{html}</div>"



# ---------------- Filter ----------------
def filter_table(search: str, tasks: list, df: pd.DataFrame, table_id: str = "leaderboard") -> str:
    """Filter DataFrame by search term and selected tasks."""
    if search:
        df = df[df["Model"].str.contains(search, case=False, na=False)]
    if tasks:
        base_cols = ["Model", "Precision", "#Params (B)", "Context"]
        selected_cols = base_cols + [c for c in tasks if c in df.columns]
        df = df[selected_cols]
    return df_to_styled_html(df, table_id=table_id)

# from huggingface_hub import HfApi
# from huggingface_hub.utils import HfHubHTTPError
# DATASET_NAME = "ailabs-itrc/requests"
# HF_TOKEN = os.environ.get("HF_TOKEN")

# def submit_request(model_name, revision, precision, weight_type,
#                    model_type, params, license_str, private_bool):
#     """Submit a model request to HuggingFace dataset only if model exists on HF."""
#     try:
#         # ---------- Check model existence on Hugging Face ----------
#         api = HfApi()
#         try:
#             api.model_info(model_name, revision=revision, token=HF_TOKEN)
#         except HfHubHTTPError as e:
#             return f"❌ Error: Model '{model_name}' (rev: {revision}) not found on Hugging Face. ({e})"
        
#         # ---------- Load dataset or create empty ----------
#         try:
#             dataset = load_dataset(DATASET_NAME, split="train", token=HF_TOKEN)
#         except Exception:
#             dataset = Dataset.from_list([])

#         existing_models = [entry["model"] for entry in dataset if "model" in entry]
#         if model_name in existing_models:
#             return f"⚠️ Model '{model_name}' already exists."

#         # ---------- Create new entry ----------
#         tehran = pytz.timezone("Asia/Tehran")
#         now = datetime.now(tehran)
#         persian_time = now.strftime("%Y-%m-%dT%H:%M:%S")

#         new_entry = {
#             "id": str(uuid.uuid4()),
#             "model": model_name,
#             "revision": revision,
#             "precision": precision,
#             "weight_type": weight_type,
#             "submitted_time": persian_time,
#             "model_type": model_type,
#             "params": float(params) if params else None,
#             "license": license_str,
#             "private": bool(private_bool),
#             "status": "⏳ pending"
#         }

#         dataset = dataset.add_item(new_entry)
#         dataset.push_to_hub(DATASET_NAME, token=HF_TOKEN)

#         return f"✅ Submitted! ID: {new_entry['id']}"
    
#     except Exception as e:
#         return f"❌ Error: {str(e)}"

# # ---------------- Submit Request ----------------
# DATASET_NAME = "ailabs-itrc/requests"
# HF_TOKEN = os.environ.get("HF_TOKEN")

# def submit_request(model_name, revision, precision, weight_type,
#                    model_type, params, license_str, private_bool):
#     """Submit a model request to HuggingFace dataset."""
#     try:
#         try:
#             dataset = load_dataset(DATASET_NAME, split="train", token=HF_TOKEN)
#         except Exception:
#             dataset = Dataset.from_list([])

#         existing_models = [entry["model"] for entry in dataset if "model" in entry]
#         if model_name in existing_models:
#             return f"⚠️ Model '{model_name}' already exists."

#         tehran = pytz.timezone("Asia/Tehran")
#         now = datetime.now(tehran)
#         persian_time = now.strftime("%Y-%m-%dT%H:%M:%S")

#         new_entry = {
#             "id": str(uuid.uuid4()),
#             "model": model_name,
#             "revision": revision,
#             "precision": precision,
#             "weight_type": weight_type,
#             "submitted_time": persian_time,
#             "model_type": model_type,
#             "params": float(params) if params else None,
#             "license": license_str,
#             "private": bool(private_bool),
#             "status": "⏳ pending"
#         }

#         dataset = dataset.add_item(new_entry)
#         dataset.push_to_hub(DATASET_NAME, token=HF_TOKEN)

#         return f"✅ Submitted! ID: {new_entry['id']}"
#     except Exception as e:
#         return f"❌ Error: {str(e)}"

import os, uuid, json
from datetime import datetime
import pytz
import pandas as pd
from datasets import load_dataset, Dataset
from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError


HF_TOKEN = os.environ.get("HF_TOKEN")
DATASET_NAME = "ailabs-itrc/requests"   # یا your-username/requests

def ensure_private_dataset(repo_id: str, token: str):
    """
    اگر دیتاست وجود نداشته باشد، آن را به صورت Private می‌سازد.
    اگر وجود دارد، کاری نمی‌کند.
    """
    api = HfApi(token=token)
    try:
        # اگر نبود، بساز
        api.create_repo(
            repo_id=repo_id,          # مثال: "ailabs-itrc/requests"
            repo_type="dataset",
            private=True,             # مهم: پرایوت
            exist_ok=True
        )
    except HfHubHTTPError as e:
        # اگر 403 گرفتی یعنی توکن دسترسی ساخت زیر org را ندارد
        raise RuntimeError(
            f"Cannot create dataset '{repo_id}'. "
            f"Check Org Write permission for this token. Original: {e}"
        )

def submit_request(
    model_name, revision, precision, weight_type,
    model_type, params, license_str, private_bool
):
    TRIM_CHARS = ' \t\n\r"\'`.,:;!؟،؛…«»()[]{}|/\\'
    
    model_name = model_name.strip(TRIM_CHARS)
    try:
        # if not HF_TOKEN:
        #     return "❌ Error: Secret HF_TOKEN not found in Space."

        # # 1) مطمئن شو دیتاست وجود دارد (و پرایوت است)
        # ensure_private_dataset(DATASET_NAME, HF_TOKEN)
        api = HfApi(token=HF_TOKEN)

#         # 🔍 اول: چک کن مدل روی Hub وجود داره یا نه
        try:
            api.model_info(model_name)  # اگر نبود، خطا میده
        except HfHubHTTPError as e:
            code = e.response.status_code if getattr(e, "response", None) else "?"
            # if code == 404:
            return f"❌ Error: Model '{model_name}' not found on Hugging Face Hub."
            # return f"❌ Error while checking model on Hub: {e}"
        # 2) دیتاست را بخوان (اگر خالی بود، از لیست خالی شروع می‌کنیم)
        try:
            dataset = load_dataset(DATASET_NAME, split="train", token=HF_TOKEN)
        except Exception:
            dataset = Dataset.from_list([])  # دیتاست جدید/خالی

        # 3) چک تکراری نبودن
        existing_models = [entry.get("model") for entry in dataset]
        if model_name in existing_models:
            return f"⚠️ Model '{model_name}' already exists."

        # 4) رکورد جدید
        tehran = pytz.timezone("Asia/Tehran")
        now = datetime.now(tehran).strftime("%Y-%m-%dT%H:%M:%S")

        new_entry = {
            "id": str(uuid.uuid4()),
            "model": model_name,
            "revision": revision,
            "precision": precision,
            "weight_type": weight_type,
            "submitted_time": now,
            "model_type": model_type,
            "params": float(params) if (params not in [None, ""]) else None,
            "license": license_str,
            "private": bool(private_bool),
            "status": "⏳ pending"
        }

        dataset = dataset.add_item(new_entry)

        # 5) پوش به هاب
        dataset.push_to_hub(DATASET_NAME, token=HF_TOKEN)

        return f"✅ Submitted! ID: {new_entry['id']}"
    except HfHubHTTPError as e:
        # خطاهای هاب را خواناتر کن
        return (
            "❌ Error while pushing to Hub:\n"
            f"{e}\n\n"
            "راهنما: اگر 403 می‌بینی، توکن باید Org Write برای 'ailabs-itrc' داشته باشد "
            "یا DATASET_NAME را موقتاً به فضای شخصی خودت ببری."
        )
    except Exception as e:
        return f"❌ Error: {e}"

# import os, uuid
# from datetime import datetime
# import pytz
# from datasets import load_dataset, Dataset
# from huggingface_hub import HfApi
# from huggingface_hub.utils import HfHubHTTPError

# HF_TOKEN = os.environ.get("HF_TOKEN")
# DATASET_NAME = "ailabs-itrc/requests"  # یا از env بخون

# def submit_request(
#     model_name, revision, precision, weight_type,
#     model_type, params, license_str, private_bool
# ):
#     try:
#         if not HF_TOKEN:
#             return "❌ Error: Secret HF_TOKEN not found in Space."

#         api = HfApi(token=HF_TOKEN)

#         # 🔍 اول: چک کن مدل روی Hub وجود داره یا نه
#         try:
#             api.model_info(model_name)  # اگر نبود، خطا میده
#         except HfHubHTTPError as e:
#             code = e.response.status_code if getattr(e, "response", None) else "?"
#             if code == 404:
#                 return f"❌ Error: Model '{model_name}' not found on Hugging Face Hub."
#             return f"❌ Error while checking model on Hub: {e}"

#         # 📂 دوم: دیتاست صف باید وجود داشته باشه
#         try:
#             api.repo_info(repo_id=DATASET_NAME, repo_type="dataset")
#         except HfHubHTTPError as e:
#             code = e.response.status_code if getattr(e, "response", None) else "?"
#             if code == 404:
#                 return f"❌ Error: Dataset '{DATASET_NAME}' not found."
#             if code == 403:
#                 return f"❌ Error: No write access to '{DATASET_NAME}'."
#             raise

#         # 📥 سوم: دیتاست رو بخون
#         try:
#             dataset = load_dataset(DATASET_NAME, split="train", token=HF_TOKEN)
#         except Exception:
#             dataset = Dataset.from_list([])

#         # ⛔ چهارم: جلوگیری از رکورد تکراری
#         existing_models = [entry.get("model") for entry in dataset]
#         if model_name in existing_models:
#             return f"⚠️ Model '{model_name}' already exists in dataset."

#         # 🆕 پنجم: رکورد جدید
#         tehran = pytz.timezone("Asia/Tehran")
#         now = datetime.now(tehran).strftime("%Y-%m-%dT%H:%M:%S")

#         new_entry = {
#             "id": str(uuid.uuid4()),
#             "model": model_name,
#             "revision": revision,
#             "precision": precision,
#             "weight_type": weight_type,
#             "submitted_time": now,
#             "model_type": model_type,
#             "params": float(params) if (params not in [None, ""]) else None,
#             "license": license_str,
#             "private": bool(private_bool),
#             "status": "⏳ pending"
#         }

#         dataset = dataset.add_item(new_entry)
#         dataset.push_to_hub(DATASET_NAME, token=HF_TOKEN)

#         return f"✅ Submitted! ID: {new_entry['id']}"

#     except HfHubHTTPError as e:
#         code = e.response.status_code if getattr(e, "response", None) else "?"
#         return f"❌ Hub Error ({code}): {e}"
#     except Exception as e:
#         return f"❌ Error: {e}"

