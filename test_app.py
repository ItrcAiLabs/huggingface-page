import gradio as gr
from utils import submit_request, load_all_data, df_to_styled_html, TASK_GROUPS, filter_table
import pandas as pd

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
/* قاب کلی جدول */
.table-wrapper {
    border: 1px solid #dbeafe;       /* آبی خیلی ملایم */
    border-radius: 12px;
    overflow-x: auto;                
    box-shadow: 0 2px 6px rgba(59,130,246,0.05);
    margin: 20px 0;
}

/* جدول */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Inter','Vazirmatn',sans-serif;
    font-size: 14px;
    table-layout: auto; /* ستون‌ها خودکار متناسب */
}

/* هدر */
.styled-table thead {
    background: linear-gradient(90deg, #f9fbff, #eef6ff); /* آبی روشن */
}
.styled-table th {
    padding: 12px 10px;
    font-weight: 600;
    font-size: 13px;
    color: #1e3a8a;                  /* آبی شیک */
    text-align: left;
    border-bottom: 2px solid #bfdbfe;
    white-space: normal;             /* اجازه بشکنه */
    word-wrap: break-word;
    max-width: 180px;                /* هدر بیش از حد عریض نشه */
    line-height: 1.4;
}

/* بدنه */
.styled-table td {
    padding: 12px 10px;
    font-size: 14px;
    color: #333;
    border-bottom: 1px solid #dbeafe; /* خطوط داخلی آبی ملایم */
    max-width: 180px;                 /* ستون‌ها نسبتا یک اندازه */
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;              /* متن بدنه نشکنه */
}

/* راه‌راه */
.styled-table tbody tr:nth-child(even) {
    background: #fafcff;
}

/* افکت هاور */
.styled-table tbody tr:hover {
    background: #e0f2fe;
    transition: background 0.2s ease-in-out;
}

/* ستون مدل خاص */
.model-col {
    font-weight: 600;
    color: #2563eb;
}















# .styled-table {
#     width: 100%;
#     border-collapse: separate;
#     border-spacing: 0;
#     font-size: 14px;
#     border: 1px solid #e5e7eb;
#     border-radius: 12px;
#     overflow: hidden;
#     box-shadow: 0 3px 10px rgba(0,0,0,0.05);
#     background: white;
#     animation: fadeIn 0.5s ease;
# }
# .styled-table thead {
#     background: #f1f5f9;
# }
# .styled-table th {
#     padding: 12px 16px;
#     font-weight: 600;
#     text-align: left;
#     color: #1e3a8a;
#     border-bottom: 2px solid #e5e7eb;
#     font-size: 13px;
#     text-transform: uppercase;
# }
# .styled-table td {
#     padding: 12px 16px;
#     border-bottom: 1px solid #f1f1f1;
# }
# .styled-table tbody tr:nth-child(even) {
#     background: #fafafa;
# }
# .styled-table tbody tr:hover {
#     background: #e0e7ff !important;
#     transition: background 0.25s ease;
# }


/* ====== Animation ====== */
@keyframes fadeIn {
    from {opacity:0; transform: translateY(6px);}
    to {opacity:1; transform: translateY(0);}
}
"""

# ---------------- Sort Function ----------------
def make_sort_func(col, df, table_id, ascending):
    def _sort():
        temp_df = df.copy()
        if col in temp_df.columns:
            temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
        sorted_df = temp_df.sort_values(by=col, ascending=ascending, na_position="last")
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
            <div style='margin-top:15px;'>
                <img src='static/persian_flag.png' width='50' style='margin:0 10px;'/>
                <img src='static/ai_logo.png' width='50' style='margin:0 10px;'/>
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
