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
    font-family: 'Raleway','Vazirmatn',sans-serif !important;
    font-size: 42px !important;
    font-weight: 600 !important;
    text-align: center;
    margin: 15px 0 25px 0 !important;

    
    background: linear-gradient(90deg, #6a11cb, #2575fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    
    text-shadow: 1px 1px 3px rgba(0,0,0,0.1);

   
    letter-spacing: 1.5px;

    
    transition: transform 0.3s ease;
}

.main-title:hover {
    transform: scale(1.03);
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
</style>
"""

# ---------------- Gradio App ----------------
with gr.Blocks(css=CUSTOM_CSS) as demo:
    with gr.Tab("📊 Persian Leaderboard"):

        # 🏆 Title
        gr.HTML("<h1 class='main-title'>Tarazban Leaderboard</h1>")

        # 🔍 Search bar at top
        gr.Markdown("<div class='section-title'>🔍 Search Models</div>")
        search_input = gr.Textbox(
            placeholder="Type model name...",
            elem_classes=["search-box"],
        )

        # ✅ Task selector below search
        gr.Markdown("<div class='section-title'>📑 Select Task Columns</div>")
        all_tasks = [col for group in TASK_GROUPS.values() for col in group]
        task_selector = gr.CheckboxGroup(
            choices=all_tasks,
            value=all_tasks,
            label="",
            elem_classes=["task-box"],
        )

        # 🔄 Helper function برای اتصال دیتافریم درست
        def make_filter_func(current_df, table_id):
            return lambda s, tasks: filter_table(s, tasks, current_df, table_id=table_id)

        # تب‌های اصلی
        tabs = [
            ("🏛️ SBU", df_sbu, "leaderboard_sbu"),
            ("🎓 UQ", df_uq, "leaderboard_uq"),
            ("⚙️ AUT", df_aut, "leaderboard_aut"),
        ]

        for tab_name, df, table_id in tabs:
            with gr.Tab(tab_name):
                output_html = gr.HTML(value=df_to_styled_html(df, table_id=table_id))

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

# import gradio as gr
# from utils import submit_request, load_all_data, df_to_styled_html, TASK_GROUPS, filter_table

# # ---------------- Load leaderboard data ----------------
# dfs = load_all_data("data/")

# df_sbu = dfs["SBU"]
# df_uq  = dfs["UQ"]
# df_aut = dfs["AUT"]

# # ---------------- Custom CSS ----------------
# CUSTOM_CSS = """
# <style>
#     .section-title {
#         font-size: 18px !important;
#         font-weight: 700 !important;
#         color: #222 !important;
#         margin: 10px 0;
#         font-family: 'Vazirmatn','Roboto',sans-serif !important;
#     }
#     .search-box input {
#         border: 2px solid #ccc !important;
#         border-radius: 8px !important;
#         padding: 8px 12px !important;
#         font-size: 14px !important;
#         font-family: 'Vazirmatn','Roboto',sans-serif !important;
#     }
#     .task-box .wrap {
#         display: flex;
#         flex-wrap: wrap;
#         gap: 8px;
#     }
#     .task-box label {
#         font-size: 13px !important;
#         font-weight: 500 !important;
#         border-radius: 12px !important;
#         padding: 6px 12px !important;
#         background: #f7f7f7 !important;
#         border: 1px solid #ddd !important;
#     }
# </style>
# """

# # ---------------- Gradio App ----------------
# with gr.Blocks(css=CUSTOM_CSS) as demo:
#     with gr.Tab("📊 Persian Leaderboard"):

#         # 🔍 Search bar at top
#         gr.Markdown("<div class='section-title'>🔍 Search Models</div>")
#         search_input = gr.Textbox(
#             placeholder="Type model name...",
#             elem_classes=["search-box"],
#         )

#         # ✅ Task selector below search
#         gr.Markdown("<div class='section-title'>📑 Select Task Columns</div>")
#         all_tasks = [col for group in TASK_GROUPS.values() for col in group]
#         task_selector = gr.CheckboxGroup(
#             choices=all_tasks,
#             value=all_tasks,
#             label="",
#             elem_classes=["task-box"],
#         )

#         # 🔄 Helper function برای اتصال دیتافریم درست
#         def make_filter_func(current_df, table_id):
#             return lambda s, tasks: filter_table(s, tasks, current_df, table_id=table_id)

#         # تب‌های اصلی
#         tabs = [
#             ("🏛️ SBU", df_sbu, "leaderboard_sbu"),
#             ("🎓 UQ", df_uq, "leaderboard_uq"),
#             ("⚙️ AUT", df_aut, "leaderboard_aut"),
#         ]

#         for tab_name, df, table_id in tabs:
#             with gr.Tab(tab_name):
#                 output_html = gr.HTML(value=df_to_styled_html(df, table_id=table_id))

#                 search_input.change(
#                     fn=make_filter_func(df, table_id),
#                     inputs=[search_input, task_selector],
#                     outputs=output_html,
#                 )
#                 task_selector.change(
#                     fn=make_filter_func(df, table_id),
#                     inputs=[search_input, task_selector],
#                     outputs=output_html,
#                 )

#     with gr.Tab("ℹ️ About"):
#         gr.Markdown(
#             """
#             # Tarazban
#             A leaderboard for Persian NLP models, grouped by **SBU**, **UQ**, and **AUT** tasks.  
#             You can search, filter tasks, and compare models interactively.
#             """
#         )

#     with gr.Tab("📥 Submit Model Request"):
#         model_name = gr.Textbox(
#             label="Model Name",
#             placeholder="Enter model name (e.g., ailabs-itrc/model-name)",
#         )
#         revision = gr.Dropdown(["main"], label="Revision")
#         precision = gr.Dropdown(["fp16", "bf16", "int8", "int4"], label="Precision")
#         weight_type = gr.Dropdown(["Original"], label="Weight Type")
#         model_type = gr.Dropdown(
#             ["🔶 Fine-tuned", "⭕ Instruction-tuned", "🟢 Pretrained"],
#             label="Model Type",
#         )
#         params = gr.Number(label="Params (Billions)")
#         license_str = gr.Dropdown(["custom", "mit", "apache-2.0"], label="License")
#         private_bool = gr.Checkbox(label="Private Model")
#         submit_btn = gr.Button("Submit")

#         output_status = gr.Textbox(label="Submission Status")

#         submit_btn.click(
#             fn=submit_request,
#             inputs=[
#                 model_name,
#                 revision,
#                 precision,
#                 weight_type,
#                 model_type,
#                 params,
#                 license_str,
#                 private_bool,
#             ],
#             outputs=output_status,
#         )

# if __name__ == "__main__":
#     demo.launch()

# # import gradio as gr
# # from utils import submit_request, load_all_data, df_to_styled_html, TASK_GROUPS, filter_table

# # # ---------------- Load leaderboard data ----------------
# # dfs = load_all_data("data/")

# # df_sbu = dfs["SBU"]
# # df_uq  = dfs["UQ"]
# # df_aut = dfs["AUT"]

# # # ---------------- Custom CSS ----------------
# # CUSTOM_CSS = """
# # <style>
# #     .section-title {
# #         font-size: 18px !important;
# #         font-weight: 700 !important;
# #         color: #222 !important;
# #         margin: 10px 0;
# #         font-family: 'Vazirmatn','Roboto',sans-serif !important;
# #     }
# #     .search-box input {
# #         border: 2px solid #ccc !important;
# #         border-radius: 8px !important;
# #         padding: 8px 12px !important;
# #         font-size: 14px !important;
# #         font-family: 'Vazirmatn','Roboto',sans-serif !important;
# #     }
# #     .task-box .wrap {
# #         display: flex;
# #         flex-wrap: wrap;
# #         gap: 8px;
# #     }
# #     .task-box label {
# #         font-size: 13px !important;
# #         font-weight: 500 !important;
# #         border-radius: 12px !important;
# #         padding: 6px 12px !important;
# #         background: #f7f7f7 !important;
# #         border: 1px solid #ddd !important;
# #     }
# # </style>
# # """

# # # ---------------- Gradio App ----------------
# # with gr.Blocks(css=CUSTOM_CSS) as demo:
# #     with gr.Tab("📊 Persian Leaderboard"):

# #         # 🔍 Search bar at top
# #         gr.Markdown("<div class='section-title'>🔍 Search Models</div>")
# #         search_input = gr.Textbox(
# #             placeholder="Type model name...",
# #             elem_classes=["search-box"],
# #         )

# #         # ✅ Task selector below search
# #         gr.Markdown("<div class='section-title'>📑 Select Task Columns</div>")
# #         all_tasks = [col for group in TASK_GROUPS.values() for col in group]
# #         task_selector = gr.CheckboxGroup(
# #             choices=all_tasks,
# #             value=all_tasks,
# #             label="",
# #             elem_classes=["task-box"],
# #         )

# #         # 🔄 Helper function for binding correct df
# #         def make_filter_func(current_df):
# #             return lambda s, tasks: filter_table(s, tasks, current_df)

# #         # تب‌های اصلی
# #         for tab_name, df in [("🏛️ SBU", df_sbu), ("🎓 UQ", df_uq), ("⚙️ AUT", df_aut)]:
# #             with gr.Tab(tab_name):
# #                 output_html = gr.HTML(value=df_to_styled_html(df))

# #                 search_input.change(
# #                     fn=make_filter_func(df),
# #                     inputs=[search_input, task_selector],
# #                     outputs=output_html,
# #                 )
# #                 task_selector.change(
# #                     fn=make_filter_func(df),
# #                     inputs=[search_input, task_selector],
# #                     outputs=output_html,
# #                 )

# #     with gr.Tab("ℹ️ About"):
# #         gr.Markdown(
# #             """
# #             # Tarazban
# #             A leaderboard for Persian NLP models, grouped by **SBU**, **UQ**, and **AUT** tasks.  
# #             You can search, filter tasks, and compare models interactively.
# #             """
# #         )

# #     with gr.Tab("📥 Submit Model Request"):
# #         model_name = gr.Textbox(
# #             label="Model Name",
# #             placeholder="Enter model name (e.g., ailabs-itrc/model-name)",
# #         )
# #         revision = gr.Dropdown(["main"], label="Revision")
# #         precision = gr.Dropdown(["fp16", "bf16", "int8", "int4"], label="Precision")
# #         weight_type = gr.Dropdown(["Original"], label="Weight Type")
# #         model_type = gr.Dropdown(
# #             ["🔶 Fine-tuned", "⭕ Instruction-tuned", "🟢 Pretrained"],
# #             label="Model Type",
# #         )
# #         params = gr.Number(label="Params (Billions)")
# #         license_str = gr.Dropdown(["custom", "mit", "apache-2.0"], label="License")
# #         private_bool = gr.Checkbox(label="Private Model")
# #         submit_btn = gr.Button("Submit")

# #         output_status = gr.Textbox(label="Submission Status")

# #         submit_btn.click(
# #             fn=submit_request,
# #             inputs=[
# #                 model_name,
# #                 revision,
# #                 precision,
# #                 weight_type,
# #                 model_type,
# #                 params,
# #                 license_str,
# #                 private_bool,
# #             ],
# #             outputs=output_status,
# #         )

# # if __name__ == "__main__":
# #     demo.launch()

# # # import gradio as gr
# # # from utils import submit_request, load_all_data, df_to_styled_html, TASK_GROUPS, filter_table

# # # # ---------------- Load leaderboard data ----------------
# # # dfs = load_all_data("data/")

# # # df_sbu = dfs["SBU"]
# # # df_uq  = dfs["UQ"]
# # # df_aut = dfs["AUT"]

# # # # ---------------- Custom CSS ----------------
# # # CUSTOM_CSS = """
# # # <style>
# # #     .section-title {
# # #         font-size: 18px !important;
# # #         font-weight: 700 !important;
# # #         color: #222 !important;
# # #         margin: 10px 0;
# # #         font-family: 'Vazirmatn','Roboto',sans-serif !important;
# # #     }
# # #     .search-box input {
# # #         border: 2px solid #ccc !important;
# # #         border-radius: 8px !important;
# # #         padding: 8px 12px !important;
# # #         font-size: 14px !important;
# # #         font-family: 'Vazirmatn','Roboto',sans-serif !important;
# # #     }
# # #     .task-box .wrap {
# # #         display: flex;
# # #         flex-wrap: wrap;
# # #         gap: 8px;
# # #     }
# # #     .task-box label {
# # #         font-size: 13px !important;
# # #         font-weight: 500 !important;
# # #         border-radius: 12px !important;
# # #         padding: 6px 12px !important;
# # #         background: #f7f7f7 !important;
# # #         border: 1px solid #ddd !important;
# # #     }
# # # </style>
# # # """

# # # # ---------------- Gradio App ----------------
# # # with gr.Blocks(css=CUSTOM_CSS) as demo:
# # #     with gr.Tab("📊 Persian Leaderboard"):

# # #         # 🔍 Search bar at top
# # #         gr.Markdown("<div class='section-title'>🔍 Search Models</div>")
# # #         search_input = gr.Textbox(
# # #             placeholder="Type model name...",
# # #             elem_classes=["search-box"],
# # #         )

# # #         # ✅ Task selector below search
# # #         gr.Markdown("<div class='section-title'>📑 Select Task Columns</div>")
# # #         all_tasks = [col for group in TASK_GROUPS.values() for col in group]
# # #         task_selector = gr.CheckboxGroup(
# # #             choices=all_tasks,
# # #             value=all_tasks,
# # #             label="",
# # #             elem_classes=["task-box"],
# # #         )

# # #         # تب‌های اصلی برای دیتاست‌ها
# # #         with gr.Tabs():
# # #             for tab_name, df in [("🏛️ SBU", df_sbu), ("🎓 UQ", df_uq), ("⚙️ AUT", df_aut)]:
# # #                 with gr.Tab(tab_name):
# # #                     output_html = gr.HTML(value=df_to_styled_html(df))

# # #                     # سرچ و فیلتر روی هر تب
# # #                     search_input.change(
# # #                         fn=lambda s, tasks, _df=df: filter_table(s, tasks, _df),
# # #                         inputs=[search_input, task_selector],
# # #                         outputs=output_html,
# # #                     )
# # #                     task_selector.change(
# # #                         fn=lambda s, tasks, _df=df: filter_table(s, tasks, _df),
# # #                         inputs=[search_input, task_selector],
# # #                         outputs=output_html,
# # #                     )

# # #     with gr.Tab("ℹ️ About"):
# # #         gr.Markdown(
# # #             """
# # #             # Tarazban
# # #             A leaderboard for Persian NLP models, grouped by **SBU**, **UQ**, and **AUT** tasks.  
# # #             You can search, filter tasks, and compare models interactively.
# # #             """
# # #         )

# # #     with gr.Tab("📥 Submit Model Request"):
# # #         model_name = gr.Textbox(
# # #             label="Model Name",
# # #             placeholder="Enter model name (e.g., ailabs-itrc/model-name)",
# # #         )
# # #         revision = gr.Dropdown(["main"], label="Revision")
# # #         precision = gr.Dropdown(["fp16", "bf16", "int8", "int4"], label="Precision")
# # #         weight_type = gr.Dropdown(["Original"], label="Weight Type")
# # #         model_type = gr.Dropdown(
# # #             ["🔶 Fine-tuned", "⭕ Instruction-tuned", "🟢 Pretrained"],
# # #             label="Model Type",
# # #         )
# # #         params = gr.Number(label="Params (Billions)")
# # #         license_str = gr.Dropdown(["custom", "mit", "apache-2.0"], label="License")
# # #         private_bool = gr.Checkbox(label="Private Model")
# # #         submit_btn = gr.Button("Submit")

# # #         output_status = gr.Textbox(label="Submission Status")

# # #         submit_btn.click(
# # #             fn=submit_request,
# # #             inputs=[
# # #                 model_name,
# # #                 revision,
# # #                 precision,
# # #                 weight_type,
# # #                 model_type,
# # #                 params,
# # #                 license_str,
# # #                 private_bool,
# # #             ],
# # #             outputs=output_status,
# # #         )

# # # if __name__ == "__main__":
# # #     demo.launch()

# # # # import gradio as gr
# # # # from utils import submit_request, load_all_data, df_to_styled_html, TASK_GROUPS, filter_table

# # # # # ---------------- Load leaderboard data ----------------
# # # # dfs = load_all_data("data/")

# # # # df_sbu = dfs["SBU"]
# # # # df_uq  = dfs["UQ"]
# # # # df_aut = dfs["AUT"]

# # # # # ---------------- Custom CSS ----------------
# # # # CUSTOM_CSS = """
# # # # <style>
# # # #     .section-title {
# # # #         font-size: 18px !important;
# # # #         font-weight: 700 !important;
# # # #         color: #222 !important;
# # # #         margin: 10px 0;
# # # #         font-family: 'Vazirmatn','Roboto',sans-serif !important;
# # # #     }
# # # #     .search-box input {
# # # #         border: 2px solid #ccc !important;
# # # #         border-radius: 8px !important;
# # # #         padding: 8px 12px !important;
# # # #         font-size: 14px !important;
# # # #         font-family: 'Vazirmatn','Roboto',sans-serif !important;
# # # #     }
# # # #     .task-box .wrap {
# # # #         display: flex;
# # # #         flex-wrap: wrap;
# # # #         gap: 8px;
# # # #     }
# # # #     .task-box label {
# # # #         font-size: 13px !important;
# # # #         font-weight: 500 !important;
# # # #         border-radius: 12px !important;
# # # #         padding: 6px 12px !important;
# # # #         background: #f7f7f7 !important;
# # # #         border: 1px solid #ddd !important;
# # # #     }
# # # # </style>
# # # # """

# # # # # ---------------- Gradio App ----------------
# # # # with gr.Blocks(css=CUSTOM_CSS) as demo:
# # # #     with gr.Tab("📊 Persian Leaderboard"):

# # # #         # 🔍 Search bar at top
# # # #         gr.Markdown("<div class='section-title'>🔍 Search Models</div>")
# # # #         search_input = gr.Textbox(
# # # #             placeholder="Type model name...",
# # # #             elem_classes=["search-box"],
# # # #         )

# # # #         # ✅ Task selector below search
# # # #         gr.Markdown("<div class='section-title'>📑 Select Task Columns</div>")
# # # #         all_tasks = [col for group in TASK_GROUPS.values() for col in group]
# # # #         task_selector = gr.CheckboxGroup(
# # # #             choices=all_tasks,
# # # #             value=all_tasks,
# # # #             label="",
# # # #             elem_classes=["task-box"],
# # # #         )

# # # #         with gr.Tabs():
# # # #             with gr.Tab("🏛️ SBU"):
# # # #                 output_sbu = gr.HTML(value=df_to_styled_html(df_sbu))
# # # #                 search_input.change(
# # # #                     fn=lambda s, tasks: filter_table(s, tasks, df_sbu),
# # # #                     inputs=[search_input, task_selector],
# # # #                     outputs=output_sbu,
# # # #                 )
# # # #                 task_selector.change(
# # # #                     fn=lambda s, tasks: filter_table(s, tasks, df_sbu),
# # # #                     inputs=[search_input, task_selector],
# # # #                     outputs=output_sbu,
# # # #                 )

# # # #             with gr.Tab("🎓 UQ"):
# # # #                 output_uq = gr.HTML(value=df_to_styled_html(df_uq))
# # # #                 search_input.change(
# # # #                     fn=lambda s, tasks: filter_table(s, tasks, df_uq),
# # # #                     inputs=[search_input, task_selector],
# # # #                     outputs=output_uq,
# # # #                 )
# # # #                 task_selector.change(
# # # #                     fn=lambda s, tasks: filter_table(s, tasks, df_uq),
# # # #                     inputs=[search_input, task_selector],
# # # #                     outputs=output_uq,
# # # #                 )

# # # #             with gr.Tab("⚙️ AUT"):
# # # #                 output_aut = gr.HTML(value=df_to_styled_html(df_aut))
# # # #                 search_input.change(
# # # #                     fn=lambda s, tasks: filter_table(s, tasks, df_aut),
# # # #                     inputs=[search_input, task_selector],
# # # #                     outputs=output_aut,
# # # #                 )
# # # #                 task_selector.change(
# # # #                     fn=lambda s, tasks: filter_table(s, tasks, df_aut),
# # # #                     inputs=[search_input, task_selector],
# # # #                     outputs=output_aut,
# # # #                 )

# # # #     with gr.Tab("ℹ️ About"):
# # # #         gr.Markdown(
# # # #             """
# # # #             # Tarazban
# # # #             A leaderboard for Persian NLP models, grouped by **SBU**, **UQ**, and **AUT** tasks.  
# # # #             You can search, filter tasks, and compare models interactively.
# # # #             """
# # # #         )

# # # #     with gr.Tab("📥 Submit Model Request"):
# # # #         model_name = gr.Textbox(
# # # #             label="Model Name",
# # # #             placeholder="Enter model name (e.g., ailabs-itrc/model-name)",
# # # #         )
# # # #         revision = gr.Dropdown(["main"], label="Revision")
# # # #         precision = gr.Dropdown(["fp16", "bf16", "int8", "int4"], label="Precision")
# # # #         weight_type = gr.Dropdown(["Original"], label="Weight Type")
# # # #         model_type = gr.Dropdown(
# # # #             ["🔶 Fine-tuned", "⭕ Instruction-tuned", "🟢 Pretrained"],
# # # #             label="Model Type",
# # # #         )
# # # #         params = gr.Number(label="Params (Billions)")
# # # #         license_str = gr.Dropdown(["custom", "mit", "apache-2.0"], label="License")
# # # #         private_bool = gr.Checkbox(label="Private Model")
# # # #         submit_btn = gr.Button("Submit")

# # # #         output_status = gr.Textbox(label="Submission Status")

# # # #         submit_btn.click(
# # # #             fn=submit_request,
# # # #             inputs=[
# # # #                 model_name,
# # # #                 revision,
# # # #                 precision,
# # # #                 weight_type,
# # # #                 model_type,
# # # #                 params,
# # # #                 license_str,
# # # #                 private_bool,
# # # #             ],
# # # #             outputs=output_status,
# # # #         )

# # # # if __name__ == "__main__":
# # # #     demo.launch()
