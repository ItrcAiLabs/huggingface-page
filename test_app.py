import gradio as gr
from utils import submit_request, load_all_data, df_to_styled_html, TASK_GROUPS, filter_table
import pandas as pd

SMALL_PARAMS_B = 9
CONTEXT_RANGE_CHOICES = ["No Filter", "0–16K", "16K–32K", "32K–128K", "128K–500K", "500K+"]

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

# ---------------- Load leaderboard data ----------------
dfs = load_all_data("data/")
df_sbu = add_organization_column(dfs["SBU"])
df_uq  = add_organization_column(dfs["UQ"])
df_aut = add_organization_column(dfs["AUT"])

df_sbu = df_sbu.loc[df_sbu[TASK_GROUPS["SBU"]].notna().any(axis=1)]
df_uq  = df_uq.loc[df_uq[TASK_GROUPS["UQ"]].notna().any(axis=1)]
df_aut = df_aut.loc[df_aut[TASK_GROUPS["AUT"]].notna().any(axis=1)]

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
    text-align: center !important;
    font-size: 42px !important;
    font-weight: 800 !important;
    letter-spacing: 1.5px;
    background: linear-gradient(90deg, #1e40af, #2563eb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 40px 0 20px 0 !important;
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

/* ===== Brand chips: آبی روشن + لوگو ===== */
.brand-chips .gr-checkbox-group { display:flex; flex-wrap:wrap; gap:8px; }

.brand-chips .gr-checkbox-group input { display:none; }

.brand-chips .gr-checkbox-group label {
  display:inline-flex; align-items:center; gap:8px;
  padding:6px 12px; border-radius:9999px;
  background:#e0f2fe;             /* آبی روشن */
  color:#0369a1;                   /* متن آبی تیره */
  border:1px solid #bae6fd;
  font-weight:600; font-size:13px; cursor:pointer;
  transition:.2s;
  position:relative; padding-left:30px; /* جا برای لوگو */
}

.brand-chips .gr-checkbox-group label:hover {
  background:#bae6fd; border-color:#7dd3fc;
}

.brand-chips .gr-checkbox-group input:checked + label {
  background:#0ea5e9; color:#fff; border-color:#0284c7;
}

/* آیکون پایه (روی همهٔ لیبل‌ها) */
.brand-chips .gr-checkbox-group label::before{
  content:""; position:absolute; left:10px; width:16px; height:16px;
  background-size:contain; background-repeat:no-repeat; background-position:center;
}

/* نگاشت لوگوها: بر اساس ترتیب items داخلی
   ساختار: .gr-checkbox-group > div:nth-of-type(N) > label */
.brand-chips .gr-checkbox-group > div:nth-of-type(1) > label::before { background-image:url("https://upload.wikimedia.org/wikipedia/commons/4/4d/OpenAI_Logo.svg"); }
.brand-chips .gr-checkbox-group > div:nth-of-type(2) > label::before { background-image:url("https://upload.wikimedia.org/wikipedia/commons/2/24/Anthropic-logo.svg"); }
.brand-chips .gr-checkbox-group > div:nth-of-type(3) > label::before { background-image:url("https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg"); }
.brand-chips .gr-checkbox-group > div:nth-of-type(4) > label::before { background-image:url("https://upload.wikimedia.org/wikipedia/commons/0/05/Meta_Platforms_Inc._logo.svg"); }
.brand-chips .gr-checkbox-group > div:nth-of-type(5) > label::before { background-image:url("https://huggingface.co/front/assets/hub/qwen-icon.png"); }
.brand-chips .gr-checkbox-group > div:nth-of-type(6) > label::before { background-image:url("https://mistral.ai/favicon.ico"); }
.brand-chips .gr-checkbox-group > div:nth-of-type(7) > label::before { background-image:url("https://avatars.githubusercontent.com/u/172669550?s=200&v=4"); }
.brand-chips .gr-checkbox-group > div:nth-of-type(8) > label::before { background-image:url("https://x.ai/favicon.ico"); }


"""

# ---------------- Sort Function ----------------
# def make_sort_func(col, df, table_id, ascending):
#     def _sort():
#         temp_df = df.copy()
#         if col in temp_df.columns:
#             temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
#         sorted_df = temp_df.sort_values(by=col, ascending=ascending, na_position="last")
#         return df_to_styled_html(sorted_df, table_id=table_id, active_col=col, ascending=ascending)
#     return _sort

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


# ---------------- Gradio App ----------------
with gr.Blocks(css=CUSTOM_CSS) as demo:
    # ===== Navbar =====
    gr.HTML("""
    <div class="navbar">
        <div class="navbar-title">Tarazban Leaderboard</div>
        <div class="navbar-links">
            <a href="#">Leaderboard</a>
            <a href="#">About</a>
            <a href="#">Submit</a>
        </div>
    </div>
    """)

    with gr.Tab("📊 Persian Benchmark"):
        # 🏆 Title
        gr.HTML("<h1 class='main-title'>Tarazban Leaderboard</h1>")
        gr.HTML("""
        <div style='text-align:center; margin-bottom:30px; font-family:"Vazirmatn",sans-serif;'>
            <p style='font-size:16px; color:#555;'>Interactive Persian NLP Leaderboard — Compare models across multiple benchmarks</p>
            
        </div>
        """)

        # 🔍 Search bar
        gr.Markdown("<div class='section-title'>🔍 Search Models</div>")
        search_input = gr.Textbox(
            placeholder="Type model name...",
            elem_classes=["search-box"],
        )
        #---------------------------------------------------
        gr.Markdown("<div class='section-title'>Quick Filters</div>")

        with gr.Column(elem_classes=["filters-box"]):
            # ردیف بالا: quick + context
            with gr.Row():
                quick_filters = gr.CheckboxGroup(
                    choices=["Open Models", f"Small Models (<{SMALL_PARAMS_B}B)"],
                    value=[], label=""
                )
                context_range = gr.Dropdown(
                    choices=["No Filter","0–16K","16K–32K","32K–128K","128K–500K","500K+"],
                    value="No Filter",
                    label="Input Context Length",
                    show_label=True,
                    elem_classes=["ctx-dd"],
                )
        
            # ردیف پایین: برندها (افقی، چیپیِ آبی)
            with gr.Row():
                brand_filters = gr.CheckboxGroup(
                    choices=["OpenAI","Anthropic","Google","Meta","Qwen","Mistral","DeepSeek","xAI"],
                    value=[], label="",
                    elem_classes=["brand-chips"],   # ← مهم
                )
        
#---------------------------------------------------------------------------------------------------------------------
       
        # subtabs for SBU / UQ / AUT
        tabs = [
            ("🏛️ SBU", df_sbu, "leaderboard_sbu"),
            ("🎓 UQ", df_uq, "leaderboard_uq"),
            ("⚙️ AUT", df_aut, "leaderboard_aut"),
        ]

        # def make_filter_func(current_df, table_id):
        #     return lambda s, tasks: filter_table(s, tasks, current_df, table_id=table_id)
        # def make_filter_func(current_df, table_id):
        #     return lambda s, tasks, qf, br: make_pipeline_filter(current_df, table_id)(s, tasks, qf, br)
        def make_filter_func(current_df, table_id):
            return lambda s, tasks, qf, br, cr: make_pipeline_filter(current_df, table_id)(s, tasks, qf, br, cr)

        
        for tab_name, df, table_id in tabs:
            with gr.Tab(tab_name):
                tab_tasks = [col for col in TASK_GROUPS[tab_name.split()[1]]]
                gr.Markdown("<div class='section-title'>📑 Select Task Columns</div>")
                task_selector = gr.CheckboxGroup(
                    choices=tab_tasks,
                    value=tab_tasks,
                    label="",
                    elem_classes=["task-box"],
                )

                output_html = gr.HTML(value=df_to_styled_html(df, table_id=table_id))

                for col in df.columns:
                    if col.lower() not in ["model", "precision", "license", "organization"]:
                        btn_asc = gr.Button(visible=False, elem_id=f"{table_id}_{col}_asc")
                        btn_desc = gr.Button(visible=False, elem_id=f"{table_id}_{col}_desc")

                        btn_asc.click(
                            make_sort_func(col, df, table_id, True),
                            inputs=None,
                            outputs=output_html,
                        )
                        btn_desc.click(
                            make_sort_func(col, df, table_id, False),
                            inputs=None,
                            outputs=output_html,
                        )

                search_input.change(
                    fn=make_filter_func(df, table_id),
                    inputs=[search_input, task_selector, quick_filters, brand_filters, context_range],
                    outputs=output_html,
                )
                task_selector.change(
                    fn=make_filter_func(df, table_id),
                    inputs=[search_input, task_selector, quick_filters, brand_filters, context_range],
                    outputs=output_html,
                )
                quick_filters.change(
                    fn=make_pipeline_filter(df, table_id),
                    inputs=[search_input, task_selector, quick_filters, brand_filters, context_range],
                    outputs=output_html,
                )
                brand_filters.change(
                    fn=make_pipeline_filter(df, table_id),
                    inputs=[search_input, task_selector, quick_filters, brand_filters, context_range],
                    outputs=output_html,
                )
                context_range.change(
                    fn=make_pipeline_filter(df, table_id),
                    inputs=[search_input, task_selector, quick_filters, brand_filters, context_range],
                    outputs=output_html,
                )



    with gr.Tab("ℹ️ About"):
        gr.Markdown("""
        # Tarazban
        A leaderboard for Persian NLP models, grouped by **SBU**, **UQ**, and **AUT** tasks.  
        You can search, filter tasks, and compare models interactively.
        """)

    with gr.Tab("📥 Submit Model Request"):
        model_name = gr.Textbox(label="Model Name", placeholder="Enter model name")
        revision = gr.Dropdown(["main"], label="Revision")
        precision = gr.Dropdown(["fp16", "bf16", "int8", "int4"], label="Precision")
        weight_type = gr.Dropdown(["Original"], label="Weight Type")
        model_type = gr.Dropdown(["🔶 Fine-tuned", "⭕ Instruction-tuned", "🟢 Pretrained"], label="Model Type")
        params = gr.Number(label="Params (Billions)")
        license_str = gr.Dropdown(["custom", "mit", "apache-2.0"], label="License")
        private_bool = gr.Checkbox(label="Private Model")
        submit_btn = gr.Button("Submit")
        output_status = gr.Textbox(label="Submission Status")

        submit_btn.click(
            fn=submit_request,
            inputs=[model_name, revision, precision, weight_type, model_type, params, license_str, private_bool],
            outputs=output_status,
        )

if __name__ == "__main__":
    demo.launch()
