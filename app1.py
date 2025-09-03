import gradio as gr
# from utils1 import submit_request, load_all_data, df_to_styled_html, TASK_GROUPS, filter_table,CUSTOM_CSS,make_brand_chip_css_by_id,SMALL_PARAMS_B,make_pipeline_filter,collect_brands,apply_quick_filters,make_sort_func,df_sbu,df_uq,df_aut
import pandas as pd
import gradio as gr
from src.tarazban.hf_submission import submit_request
from src.tarazban.dataio import load_all_data, TASK_GROUPS
from src.tarazban.render import df_to_styled_html
from src.tarazban.filters import filter_table,apply_quick_filters,make_pipeline_filter
from src.tarazban.brands import  make_brand_chip_css_by_id, collect_brands
with open("static/styles.css", "r", encoding="utf-8") as f:
    CUSTOM_CSS = f.read()
dfs = load_all_data("data/")
df_sbu = dfs["SBU"]
df_uq  = dfs["UQ"]
df_aut = dfs["AUT"]


# ---------------- Gradio App ----------------
with gr.Blocks(css=CUSTOM_CSS) as demo:
    # gr.HTML(make_brand_icon_css())
    gr.HTML(make_brand_chip_css_by_id())   # ← لوگوهای بدون JS و بدون :has()

    # ===== Navbar =====
    gr.HTML("""
        <div class="hero">
          <div class="title-wrap">
            <h1 class="main-title">
              <span class="title-accent">Tarazban</span> Leaderboard
            </h1>
            <p class="subtitle">
              Interactive Persian NLP Leaderboard — <span>Compare models across multiple benchmarks</span>
            </p>
          </div>
        </div>
        """)

    with gr.Tab("📊 Benchmarks"):
        # # 🏆 Title
        # gr.HTML("<h1 class='main-title'>Tarazban Leaderboard</h1>")
        # gr.HTML("""
        # <div style='text-align:center; margin-bottom:30px; font-family:"Vazirmatn",sans-serif;'>
        #     <p style='font-size:16px; color:#555;'>Interactive Persian NLP Leaderboard — Compare models across multiple benchmarks</p>
            
        # </div>
        # """)

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
                # brand_filters = gr.CheckboxGroup(
                #     choices=["OpenAI","Anthropic","Google","Meta","Qwen","Mistral","DeepSeek","xAI"],
                #     value=[], label="",
                #     elem_classes=["brand-chips"],   # ← مهم
                # )
                # with gr.Row():
                    # cb_openai    = gr.Checkbox(label="OpenAI",    value=False, elem_id="brand_openai")
                    # cb_anthropic = gr.Checkbox(label="Anthropic", value=False, elem_id="brand_anthropic")
                    # cb_google    = gr.Checkbox(label="Google",    value=False, elem_id="brand_google")
                    # cb_meta      = gr.Checkbox(label="Meta",      value=False, elem_id="brand_meta")
                    # cb_qwen      = gr.Checkbox(label="Qwen",      value=False, elem_id="brand_qwen")
                    # cb_mistral   = gr.Checkbox(label="Mistral",   value=False, elem_id="brand_mistral")
                    # cb_deepseek  = gr.Checkbox(label="DeepSeek",  value=False, elem_id="brand_deepseek")
                    # cb_xai       = gr.Checkbox(label="xAI",       value=False, elem_id="brand_xai")
                    with gr.Row(elem_classes=["brand-row"]):
                        cb_openai    = gr.Checkbox(label="OpenAI",    value=False, elem_id="brand_openai")
                        cb_anthropic = gr.Checkbox(label="Anthropic", value=False, elem_id="brand_anthropic")
                        cb_google    = gr.Checkbox(label="Google",    value=False, elem_id="brand_google")
                        cb_meta      = gr.Checkbox(label="Meta",      value=False, elem_id="brand_meta")
                        cb_qwen      = gr.Checkbox(label="Qwen",      value=False, elem_id="brand_qwen")
                        cb_mistral   = gr.Checkbox(label="Mistral",   value=False, elem_id="brand_mistral")
                        cb_deepseek  = gr.Checkbox(label="DeepSeek",  value=False, elem_id="brand_deepseek")
                        cb_xai       = gr.Checkbox(label="xAI",       value=False, elem_id="brand_xai")


        
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
        def make_filter_func_by_checkboxes(current_df, table_id):
            def _fn(search_text, task_cols, quick, openai, anthropic, google, meta, qwen, mistral, deepseek, xai, ctx_range):
                brands = collect_brands(openai, anthropic, google, meta, qwen, mistral, deepseek, xai)
                df1 = apply_quick_filters(current_df, quick or [], brands, ctx_range)
                # return filter_table(search_text, task_cols, df1, table_id=table_id)
                return filter_table(search_text, task_cols, df1.drop(columns=["Organization","Brand","OpenSource"], errors="ignore"), table_id=table_id)

            return _fn
                
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
            
                # output_html = gr.HTML(value=df_to_styled_html(df, table_id=table_id))
                output_html = gr.HTML(value=df_to_styled_html(df.drop(columns=["Organization","Brand","OpenSource"], errors="ignore"), table_id=table_id))

            
                # تابع فیلتر که ۸ چک‌باکس را به لیست برند تبدیل می‌کند
                filter_fn = make_filter_func_by_checkboxes(df, table_id)
            
                # دکمه‌های سورت مثل قبل
                for col in df.columns:
                    if col.lower() not in ["model", "precision", "license", "organization"]:
                        btn_asc = gr.Button(visible=False, elem_id=f"{table_id}_{col}_asc")
                        btn_desc = gr.Button(visible=False, elem_id=f"{table_id}_{col}_desc")
                        btn_asc.click(make_sort_func(col, df, table_id, True), inputs=None, outputs=output_html)
                        btn_desc.click(make_sort_func(col, df, table_id, False), inputs=None, outputs=output_html)
            
                # ورودی‌های مشترک برای همه تریگرها
                brand_inputs = [cb_openai, cb_anthropic, cb_google, cb_meta, cb_qwen, cb_mistral, cb_deepseek, cb_xai]
                common_inputs = [search_input, task_selector, quick_filters, *brand_inputs, context_range]
            
                # تریگرها: همه باید از filter_fn استفاده کنند و ۸ چک‌باکس را پاس بدهند
                search_input.change(fn=filter_fn, inputs=common_inputs, outputs=output_html)
                task_selector.change(fn=filter_fn, inputs=common_inputs, outputs=output_html)
                quick_filters.change(fn=filter_fn, inputs=common_inputs, outputs=output_html)
                context_range.change(fn=filter_fn, inputs=common_inputs, outputs=output_html)
            
                # هر کدام از ۸ چک‌باکس هم اگر عوض شد، همین فیلتر اجرا شود
                for cb in brand_inputs:
                    cb.change(fn=filter_fn, inputs=common_inputs, outputs=output_html)

    with gr.Tab("🌐 About Tarazban"):
        gr.Markdown("""
        # Tarazban
        A leaderboard for Persian NLP models, grouped by **SBU**, **UQ**, and **AUT** tasks.  
        You can search, filter tasks, and compare models interactively.
        """)

    with gr.Tab("🚀 Submit Model"):
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
