import gradio as gr
from utils import submit_request, load_all_data, df_to_styled_html, TASK_GROUPS, filter_table

# ---------------- Load leaderboard data ----------------
dfs = load_all_data("data/")
df_sbu = dfs["SBU"]
df_uq  = dfs["UQ"]
df_aut = dfs["AUT"]

# ---------------- Custom CSS ----------------
CUSTOM_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Vazirmatn:wght@400;600;700&display=swap" rel="stylesheet">

<style>
body {
    font-family: 'Inter','Vazirmatn', sans-serif !important;
    background: #fafafa !important;
}

.main-title {
    text-align: center !important;
    font-size: 48px !important;
    font-weight: 700 !important;
    background: linear-gradient(90deg, #1e40af, #2563eb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0px 3px 10px rgba(0,0,0,0.15);
    margin: 25px 0 10px 0 !important;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #555;
    margin-bottom: 25px;
}

.logo-row {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-bottom: 40px;
    opacity: 0.7;
}

.styled-table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    width: 100% !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    font-family: 'Inter','Vazirmatn', sans-serif !important;
    font-size: 14px;
}

.styled-table thead {
    background: #f9fafb !important;
    font-weight: 600 !important;
}

.styled-table th, .styled-table td {
    padding: 12px 16px !important;
    border-bottom: 1px solid #e5e7eb !important;
    text-align: left !important;
}

.styled-table tbody tr:hover {
    background: #f3f4f6 !important;
}

.section-title {
    font-size: 18px !important;
    font-weight: 600 !important;
    margin: 10px 0;
    color: #222 !important;
}

.search-box input {
    border: 2px solid #ccc !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-size: 14px !important;
}

.filter-box label {
    background: #f7f7f7 !important;
    border: 1px solid #ddd !important;
    border-radius: 20px !important;
    padding: 6px 14px !important;
    font-size: 13px !important;
    font-weight: 500;
}
</style>
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

    # 🏆 Title
    gr.HTML("<h1 class='main-title'>Tarazban Leaderboard</h1>")
    gr.HTML("""
        <div class="subtitle">
            Analyze and compare <b>Persian NLP Models</b> across benchmarks, pricing, and capabilities.
        </div>
        <div class="logo-row">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg" height="32"/>
            <img src="https://upload.wikimedia.org/wikipedia/commons/4/44/Mistral_logo.png" height="32"/>
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/69/AI_icon.png" height="32"/>
            <img src="https://upload.wikimedia.org/wikipedia/commons/4/4a/Logo_2013_Google.png" height="32"/>
        </div>
    """)

    with gr.Tab("📊 Persian Benchmark"):

        # 🔍 Search bar at top
        gr.Markdown("<div class='section-title'>🔍 Search Models</div>")
        search_input = gr.Textbox(placeholder="Type model name...", elem_classes=["search-box"])

        # ⭐ Quick Filters
        gr.Markdown("<div class='section-title'>⚡ Quick Filters</div>")
        quick_filters = gr.CheckboxGroup(
            choices=["Multimodal", "Open Models", "Long Context", "Small Models (<8B)"],
            value=[],
            label="",
            elem_classes=["filter-box"],
        )

        org_filters = gr.CheckboxGroup(
            choices=["OpenAI", "Anthropic", "Google", "Meta", "Qwen", "Mistral", "DeepSeek", "xAI"],
            value=[],
            label="Organizations",
            elem_classes=["filter-box"],
        )

        # Tabs for datasets
        tabs = [
            ("🏛️ SBU", df_sbu, "leaderboard_sbu"),
            ("🎓 UQ", df_uq, "leaderboard_uq"),
            ("⚙️ AUT", df_aut, "leaderboard_aut"),
        ]

        def make_filter_func(current_df, table_id):
            return lambda s, tasks: filter_table(s, tasks, current_df, table_id=table_id)

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
                    if col.lower() not in ["model", "precision"]:
                        btn_asc = gr.Button(visible=False, elem_id=f"{table_id}_{col}_asc")
                        btn_desc = gr.Button(visible=False, elem_id=f"{table_id}_{col}_desc")

                        btn_asc.click(make_sort_func(col, df, table_id, True), outputs=output_html)
                        btn_desc.click(make_sort_func(col, df, table_id, False), outputs=output_html)

                search_input.change(make_filter_func(df, table_id), [search_input, task_selector], output_html)
                task_selector.change(make_filter_func(df, table_id), [search_input, task_selector], output_html)


    with gr.Tab("ℹ️ About"):
        gr.Markdown("""
        # Tarazban  
        A leaderboard for Persian NLP models, grouped by **SBU**, **UQ**, and **AUT** tasks.  
        You can search, filter tasks, and compare models interactively.
        """)

    with gr.Tab("📥 Submit Model Request"):
        model_name = gr.Textbox(label="Model Name", placeholder="Enter model name (e.g., ailabs-itrc/model-name)")
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

# import gradio as gr
# import pandas as pd

# # دیتای تست
# df = pd.DataFrame({
#     "Model": ["A", "B", "C", "D"],
#     "Score": [0.85, 0.65, 0.92, 0.71],
#     "Params": [1.3, 2.1, 0.9, 5.4],
# })

# # HTML جدول
# def df_to_styled_html(df: pd.DataFrame, table_id: str = "leaderboard", active_col=None, ascending=None) -> str:
#     html = f"<table id='{table_id}' class='styled-table'>"
#     html += "<thead><tr>"

#     for col in df.columns:
#         up_color = "color:#999;"  # پیش‌فرض خاکستری
#         down_color = "color:#999;"
#         if active_col == col:
#             if ascending:
#                 up_color = "color:#2563eb;font-weight:bold;"  # آبی برای صعودی
#             else:
#                 down_color = "color:#2563eb;font-weight:bold;"  # آبی برای نزولی

#         html += f"""
#         <th>
#             {col}
#             <button style='all:unset;cursor:pointer;' 
#                     onclick="document.getElementById('{table_id}_{col}_asc').click()">
#                 <span style='{up_color}'>&uarr;</span>
#             </button>
#             <button style='all:unset;cursor:pointer;' 
#                     onclick="document.getElementById('{table_id}_{col}_desc').click()">
#                 <span style='{down_color}'>&darr;</span>
#             </button>
#         </th>
#         """

#     html += "</tr></thead><tbody>"
#     for _, row in df.iterrows():
#         html += "<tr>"
#         for col in df.columns:
#             html += f"<td>{row[col]}</td>"
#         html += "</tr>"
#     html += "</tbody></table>"
#     return html


# # تابع سورت
# def sort_table(col, ascending):
#     sorted_df = df.sort_values(by=col, ascending=ascending)
#     return df_to_styled_html(sorted_df, active_col=col, ascending=ascending)


# # اپ تست
# with gr.Blocks() as demo:
#     output_html = gr.HTML(value=df_to_styled_html(df))

#     # دکمه‌های مخفی برای هر ستون (asc و desc جدا)
#     for col in df.columns:
#         btn_asc = gr.Button(visible=False, elem_id=f"leaderboard_{col}_asc")
#         btn_desc = gr.Button(visible=False, elem_id=f"leaderboard_{col}_desc")

#         btn_asc.click(
#             lambda c=col: sort_table(c, True),
#             inputs=None,
#             outputs=output_html,
#         )
#         btn_desc.click(
#             lambda c=col: sort_table(c, False),
#             inputs=None,
#             outputs=output_html,
#         )

# if __name__ == "__main__":
#     demo.launch()
