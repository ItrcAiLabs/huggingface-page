import gradio as gr
from utils import submit_request, load_all_data, df_to_styled_html, TASK_GROUPS, filter_table

# ---------------- Load leaderboard data ----------------
dfs = load_all_data("data/")
df_sbu = dfs["SBU"]
df_uq  = dfs["UQ"]
df_aut = dfs["AUT"]

# ---------------- Custom CSS ----------------
CUSTOM_CSS = """
.main-title {
    text-align: center !important;
    font-family: 'Raleway','Vazirmatn',sans-serif !important;
    font-size: 46px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px;
    background: linear-gradient(90deg, #1e40af, #2563eb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0px 3px 8px rgba(0,0,0,0.25);
    margin: 25px 0 15px 0 !important;
}
.section-title {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #222 !important;
    margin: 10px 0;
    font-family: 'Vazirmatn','Roboto',sans-serif !important;
}
.search-box input {
    border: 2px solid #ccc !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-size: 14px !important;
    font-family: 'Vazirmatn','Roboto',sans-serif !important;
}
.task-box .wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.task-box label {
    font-size: 13px !important;
    font-weight: 500 !important;
    border-radius: 12px !important;
    padding: 6px 12px !important;
    background: #f7f7f7 !important;
    border: 1px solid #ddd !important;
}
.styled-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 14px;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.styled-table thead {
    background: #f9fafb;
}
.styled-table th {
    padding: 12px 16px;
    font-weight: 600;
    text-align: left;
    border-bottom: 1px solid #e5e7eb;
}
.styled-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #f1f1f1;
}
.styled-table tbody tr:hover {
    background: #f3f4f6;
}
"""

def make_sort_func(col, df, table_id, ascending):
    def _sort():
        sorted_df = df.sort_values(by=col, ascending=ascending)
        return df_to_styled_html(
            sorted_df,
            table_id=table_id,
            active_col=col,
            ascending=ascending,
        )
    return _sort


# ---------------- Gradio App ----------------
with gr.Blocks(css=CUSTOM_CSS) as demo:
    with gr.Tab("📊 Persian Benchmark"):
        # main tabs
        tabs = [
            ("🏛️ SBU", df_sbu, "leaderboard_sbu"),
            ("🎓 UQ", df_uq, "leaderboard_uq"),
            ("⚙️ AUT", df_aut, "leaderboard_aut"),
        ]

        def make_filter_func(current_df, table_id):
            return lambda s, tasks: filter_table(s, tasks, current_df, table_id=table_id)

        # 🏆 Title
        gr.HTML("<h1 class='main-title'>Tarazban Leaderboard</h1>")
        gr.HTML("""
        <div style='text-align:center; margin-bottom:30px; font-family:"Vazirmatn",sans-serif;'>
            <p style='font-size:16px; color:#555;'>Interactive Persian NLP Leaderboard — Compare models across multiple benchmarks</p>
            <div style='margin-top:15px;'>
                <img src='https://huggingface.co/front/assets/huggingface_logo-noborder.svg' width='60' style='margin:0 10px;'/>
                <img src='https://upload.wikimedia.org/wikipedia/commons/3/38/Flag_of_Persia.svg' width='60' style='margin:0 10px;'/>
            </div>
        </div>
        """)

        # 🔍 Search bar
        gr.Markdown("<div class='section-title'>🔍 Search Models</div>")
        search_input = gr.Textbox(
            placeholder="Type model name...",
            elem_classes=["search-box"],
        )

        # subtabs for SBU / UQ / AUT
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
                    if col.lower() not in ["model", "precision",  "license", "organization"]:
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

    with gr.Tab("ℹ️ About"):
        gr.Markdown(
            """
            # Tarazban
            A leaderboard for Persian NLP models, grouped by **SBU**, **UQ**, and **AUT** tasks.  
            You can search, filter tasks, and compare models interactively.
            """
        )

    with gr.Tab("📥 Submit Model Request"):
        model_name = gr.Textbox(
            label="Model Name",
            placeholder="Enter model name (e.g., ailabs-itrc/model-name)",
        )
        revision = gr.Dropdown(["main"], label="Revision")
        precision = gr.Dropdown(["fp16", "bf16", "int8", "int4"], label="Precision")
        weight_type = gr.Dropdown(["Original"], label="Weight Type")
        model_type = gr.Dropdown(
            ["🔶 Fine-tuned", "⭕ Instruction-tuned", "🟢 Pretrained"],
            label="Model Type",
        )
        params = gr.Number(label="Params (Billions)")
        license_str = gr.Dropdown(["custom", "mit", "apache-2.0"], label="License")
        private_bool = gr.Checkbox(label="Private Model")
        submit_btn = gr.Button("Submit")

        output_status = gr.Textbox(label="Submission Status")

        submit_btn.click(
            fn=submit_request,
            inputs=[
                model_name,
                revision,
                precision,
                weight_type,
                model_type,
                params,
                license_str,
                private_bool,
            ],
            outputs=output_status,
        )

if __name__ == "__main__":
    demo.launch()
