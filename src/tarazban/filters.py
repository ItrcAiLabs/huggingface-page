import pandas as pd
SMALL_PARAMS_B = 9

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
def make_pipeline_filter(current_df: pd.DataFrame, table_id: str):
    def _fn(search_text: str, task_cols: list, quick: list, brands: list, ctx_range: str | None):
        df1 = apply_quick_filters(current_df, quick or [], brands or [], ctx_range)
        return filter_table(search_text, task_cols, df1, table_id=table_id)
    return _fn
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