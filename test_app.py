import gradio as gr
from utils import submit_request, load_all_data, df_to_styled_html, TASK_GROUPS, filter_table
import pandas as pd

SMALL_PARAMS_B = 9
# --- Context range choices (tokens) ---
CONTEXT_RANGE_CHOICES = ["0–16K", "16K–32K", "32K–128K", "128K–500K", "500K+"]

def ctx_to_int(x):
    
    import math
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

def apply_quick_filters(df: pd.DataFrame, quick: list, brands: list) -> pd.DataFrame:
    out = df.copy()
    # if "Multimodal" in quick and "Modality" in out.columns:
    #     out = out[out["Modality"].astype(str).str.contains("image|audio|vision|multimodal", case=False, na=False)]
    if "Open Models" in quick and "License" in out.columns:
        out = out[out["License"].astype(str).str.lower().ne("custom")]
    
    if "Small Models (<9B)" in quick:
        col = next((c for c in ["#Params (B)","Params (B)","Parameters (B)"] if c in out.columns), None)
        if col:
            v = pd.to_numeric(out[col], errors="coerce").fillna(1e9)
            out = out[v < SMALL_PARAMS_B]
    if brands and "Organization" in out.columns:
        out = out[out["Organization"].astype(str).isin(brands)]
        # --- Context range filter ---
    if ctx_range:
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

# def make_pipeline_filter(current_df: pd.DataFrame, table_id: str):
#     def _fn(search_text: str, task_cols: list, quick: list, brands: list):
#         df1 = apply_quick_filters(current_df, quick or [], brands or [])
#         return filter_table(search_text, task_cols, df1, table_id=table_id)
#     return _fn
def make_pipeline_filter(current_df: pd.DataFrame, table_id: str):
    def _fn(search_text: str, task_cols: list, quick: list, brands: list, ctx_range: str | None):
        df1 = apply_quick_filters(current_df, quick or [], brands or [], ctx_range)
        return filter_table(search_text, task_cols, df1, table_id=table_id)
    return _fn



# ---------------- Load leaderboard data ----------------
dfs = load_all_data("data/")
df_sbu = dfs["SBU"]
df_uq  = dfs["UQ"]
df_aut = dfs["AUT"]

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
.quick-filters-wrap{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:8px 0 12px}
.quick-title{color:#334155;font-weight:700;margin-inline-end:6px}
.gr-checkbox-group{display:flex;flex-wrap:wrap;gap:8px}
.gr-checkbox-group input{display:none}
.gr-checkbox-group label{
    display:inline-flex;align-items:center;gap:8px;
    padding:8px 12px;border-radius:999px;background:#eef2ff;color:#1e293b;
    border:1px solid #e5e7eb;font-weight:700;font-size:13px;cursor:pointer;
    box-shadow:0 2px 4px rgba(0,0,0,0.04);transition:.2s
}
.gr-checkbox-group label:hover{background:#e0e7ff}
.gr-checkbox-group input:checked+label{background:#4f46e5;color:#fff;border-color:#4f46e5}

/* ---- Tiny chip label ---- */
.mini-chip{
  display:inline-flex; align-items:center; gap:6px;
  padding:4px 10px; border:1px solid #e5e7eb; border-radius:9999px;
  background:#ffffff;
  font-weight:700; font-size:12px; color:#334155;
  box-shadow:0 1px 2px rgba(0,0,0,.04);
  height:32px; line-height:32px;
}

/* ---- Compact pill dropdown ---- */
.ctx-range{
  display:inline-block !important;
  max-width:120px !important;       
  min-width:96px !important;
}

.ctx-range select,
.ctx-range button,
.ctx-range .wrap-inner{
  border:1px solid #d1d5db !important;
  border-radius:9999px !important;
  padding:4px 10px !important;
  font-size:13px !important;
  height:32px !important;
  background:#f9fafb !important;
  box-shadow:0 1px 2px rgba(0,0,0,.04) !important;
  cursor:pointer !important;
}

/* hover */
.ctx-range:hover select,
.ctx-range:hover button{
  border-color:#3b82f6 !important;
}

.ctx-range .container, .ctx-range .label-wrap{ padding:0 !important; border:none !important; }



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
        with gr.Row():
            quick_filters = gr.CheckboxGroup(
                choices=["Open Models","Small Models (<9B)"],
                value=[], label=""
            )
            gr.HTML("<span class='mini-chip'>Input Context Length</span>")
    
        # Dropdown جمع‌وجور (بدون لیبل داخلی)
        context_range = gr.Dropdown(
            choices=CONTEXT_RANGE_CHOICES,
            value=None,
            label="",          # لیبل داخلی نمی‌خوایم
            show_label=False,  # پسِش هم مخفی
            container=False,
            elem_classes=["ctx-range"],
        )



        brand_filters = gr.CheckboxGroup(
            choices=["OpenAI","Anthropic","Google","Meta","Qwen","Mistral","DeepSeek","xAI"],
            value=[], label=""
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
                    inputs=[search_input, task_selector],
                    outputs=output_html,
                )
                task_selector.change(
                    fn=make_filter_func(df, table_id),
                    inputs=[search_input, task_selector],
                    outputs=output_html,
                )
                quick_filters.change(
                    fn=make_pipeline_filter(df, table_id),
                    inputs=[search_input, task_selector, quick_filters, brand_filters],
                    outputs=output_html,
                )
                brand_filters.change(
                    fn=make_pipeline_filter(df, table_id),
                    inputs=[search_input, task_selector, quick_filters, brand_filters],
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
