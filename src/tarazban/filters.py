import pandas as pd
SMALL_PARAMS_B = 14
from .render import df_to_styled_html
# def add_organization_column(df: pd.DataFrame) -> pd.DataFrame:
#     if "Organization" not in df.columns:
#         df["Organization"] = df["Model"].apply(
#             lambda m: str(m).split("/")[0].lower() if "/" in str(m) else str(m).lower()
#         )
#         df["Brand"] = df["Organization"].map(lambda o: ORG_TO_BRAND.get(o, o.title()))
#         df["OpenSource"] = df["Organization"].map(lambda o: OPEN_ORGS.get(o, False))
#     return df

def add_organization_column(df: pd.DataFrame) -> pd.DataFrame:
    if "Organization" not in df.columns:
        def detect_org(m):
            m = str(m).lower()
            if "/" in m:
                org, rest = m.split("/", 1)
                if "gemma" in rest:   # 👈 اگر مدل از گوگل باشه ولی اسمش gemma داشته باشه
                    return "gemma"    # سازمان رو gemma در نظر بگیر
                return org
            return m

        df["Organization"] = df["Model"].apply(detect_org)
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
    "tiiuae" : "Falcon",
    "01-ai" : "Yi",
    "mistralai" :"Mistral AI",
    "partai"     : "Part DP AI"
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
    "tiiuae" : True,
    "01-ai" : True,
    "mistralai" :True,
    "partai"     : True
}

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