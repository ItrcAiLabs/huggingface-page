import gradio as gr
from utils import submit_request, load_all_data, df_to_styled_html, TASK_GROUPS, filter_table


# ---------------- Load leaderboard data ----------------
dfs = load_all_data("data/")

df_sbu = dfs["SBU"]
df_uq  = dfs["UQ"]
df_aut = dfs["AUT"]

# ---------------- Custom CSS ----------------
CUSTOM_CSS = """
<style>
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
        margin: 25px 0 35px 0 !important;
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
    th {
        cursor: pointer;
        position: relative;
        padding-right: 20px;
    th .sort-icon {
        margin-left: 6px;
        font-size: 12px;
        color: #999;
    }
    th.asc .sort-icon,
    th.desc .sort-icon {
        color: #2563eb;
        font-weight: bold;
    }
    </style>
    """


# ---------------- Gradio App ----------------
# ---------------- Gradio App ----------------
with gr.Blocks(css=CUSTOM_CSS) as demo:
    # inject sort.js globally 
    with open("static/sort.js", "r", encoding="utf-8") as f:
        sort_js = f.read()
    gr.HTML(f"<script>{sort_js}</script>")

    
    
    with gr.Tab("📊 Persian Leaderboard"):
         # main tabs
        tabs = [
            ("🏛️ SBU", df_sbu, "leaderboard_sbu"),
            ("🎓 UQ", df_uq, "leaderboard_uq"),
            ("⚙️ AUT", df_aut, "leaderboard_aut"),
        ]
        # 🔄 Helper function for connecting correct dataframe
        def make_filter_func(current_df, table_id):
            return lambda s, tasks: filter_table(s, tasks, current_df, table_id=table_id)

        # 🏆 Title
        gr.HTML("""
            <h1 style="
                text-align:center;
                font-family:'Raleway','Vazirmatn',sans-serif;
                font-size:46px;
                font-weight:700;
                letter-spacing:1.5px;
            
                background: linear-gradient(90deg, #1e40af, #2563eb);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0px 3px 8px rgba(0,0,0,0.25);
                margin: 25px 0 35px 0;
            ">
                Tarazban Leaderboard
            </h1>
            """)




        # 🔍 Search bar at top
        gr.Markdown("<div class='section-title'>🔍 Search Models</div>")
        search_input = gr.Textbox(
            placeholder="Type model name...",
            elem_classes=["search-box"],
        )

        # ✅ Task selector below search
        # gr.Markdown("<div class='section-title'>📑 Select Task Columns</div>")
        # all_tasks = [col for group in TASK_GROUPS.values() for col in group]
        # task_selector = gr.CheckboxGroup(
        #     choices=all_tasks,
        #     value=all_tasks,
        #     label="",
        #     elem_classes=["task-box"],
        # )
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
            sort_col = gr.Dropdown(
                choices=df.columns.tolist(),
                value=df.columns[0],
                label="Sort by column"
            )
            sort_order = gr.Radio(
                choices=["Ascending", "Descending"],
                value="Descending",
                label="Order"
            )
            
            output_html = gr.HTML(value=df_to_styled_html(df, table_id=table_id))
            # ---------------- event connection ----------------
            def update_table(search, tasks, col, order):
                sorted_df = sort_dataframe(df, col, ascending=(order == "Ascending"))
                return filter_table(search, tasks, sorted_df, table_id=table_id)
        
            search_input.change(
                fn=update_table,
                inputs=[search_input, task_selector, sort_col, sort_order],
                outputs=output_html,
            )
            task_selector.change(
                fn=update_table,
                inputs=[search_input, task_selector, sort_col, sort_order],
                outputs=output_html,
            )
            sort_col.change(
                fn=update_table,
                inputs=[search_input, task_selector, sort_col, sort_order],
                outputs=output_html,
            )
            sort_order.change(
                fn=update_table,
                inputs=[search_input, task_selector, sort_col, sort_order],
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


        
       

        # for tab_name, df, table_id in tabs:
        #     with gr.Tab(tab_name):
        #         output_html = gr.HTML(value=df_to_styled_html(df, table_id=table_id))

        #         search_input.change(
        #             fn=make_filter_func(df, table_id),
        #             inputs=[search_input, task_selector],
        #             outputs=output_html,
        #         )
        #         task_selector.change(
        #             fn=make_filter_func(df, table_id),
        #             inputs=[search_input, task_selector],
        #             outputs=output_html,
        #         )
    
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

