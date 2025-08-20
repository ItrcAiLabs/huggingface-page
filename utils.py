# import os
# import json
# import uuid
# import pytz
# import pandas as pd
# from datetime import datetime
# from datasets import load_dataset, Dataset

# # ---------------- Task Groups ----------------
# TASK_GROUPS = {
#     "SBU": [
#         "General Medicine",
#         "Complementary & Alternative Medicine",
#         "Emergency Medicine",
#         "Constitution of IRI",
#         "Other legal Domains",
#         "Religion",
#         "Grammar, Proverbs & Strings",
#         "Lexical Semantics",
#         "Encyclopedic Knowledge",
#         "Recommendation & Human Preferences",
#         "Text Completion",
#         "Poems & Lyrics",
#         "Paraphrase",
#         "Style Transfer",
#         "Emotion",
#         "Irony",
#         "Metaphor",
#         "Empathy, Intimacy & Trust",
#         "Ethics & Bias",
#         "Toxicity",
#         "Human Rights"
#     ],
#     "UQ": [
#         "belebel_e",
#         "farstail",
#         "pn_summary_categorization",
#         "pn_summary_summarize",
#         "Parsinlu_translation_fa_en",
#         "Parsinlu_translation_en_fa",
#         "persian_MMLU",
#         "ARC_easy",
#         "ARC_challenge"
#     ],
#     "AUT": []
# }

# # ---------------- Load Data ----------------
# def load_all_data(path):
#     rows = []
#     with open(path + "results.jsonl", "r", encoding="utf-8") as f:
#         for line in f:
#             rows.append(json.loads(line))

#     df = pd.DataFrame(rows)

#     # ستون‌های مشترک
#     base_cols = ["Model", "Precision", "#Params (B)"]

#     dfs = {}
#     for group, tasks in TASK_GROUPS.items():
#         cols = base_cols + [col for col in tasks if col in df.columns]
#         dfs[group] = df[cols].copy()
#     return dfs

# # ---------------- Gradient Coloring ----------------
# def value_to_gradient_range(value: float, min_val: float = 0, max_val: float = 100) -> str:
#     value = max(min_val, min(max_val, value))
#     ratio = (value - min_val) / (max_val - min_val)

#     red = int(255 * (1 - ratio))
#     green = int(255 * ratio)
#     blue = 100
#     return f"linear-gradient(90deg, rgba({red},{green},{blue},0.3), rgba({red},{green},{blue},0.8))"

# def apply_gradient(df: pd.DataFrame) -> pd.DataFrame:
#     df = df.copy()
#     for col in df.columns:
#         if col not in ["Model", "Precision", "#Params (B)"]:
#             if pd.api.types.is_numeric_dtype(df[col]):
#                 df[col] = df[col].apply(
#                     lambda v: f"<div style='background:{value_to_gradient_range(v)};padding:4px'>{v:.1f}</div>"
#                     if pd.notnull(v) else "-"
#                 )
#     return df

# # ---------------- Tabbed HTML ----------------
# def df_to_tabbed_html(dfs: dict[str, pd.DataFrame]) -> str:
#     html = """
#     <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
#     <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
#     <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

#     <style>
#         body { font-family: 'Tahoma', sans-serif; }
#         .tabs { margin-bottom: 15px; }
#         .tabs button {
#             background: #eee; border: none; padding: 10px 20px;
#             cursor: pointer; margin-right: 5px; border-radius: 6px 6px 0 0;
#         }
#         .tabs button.active { background: #0044cc; color: white; }
#         .tabcontent { display: none; }
#         table.dataTable { width: 100% !important; font-size: 13px; }
#         td, th { text-align: center; vertical-align: middle; }
#     </style>
#     """

#     # Tabs header
#     html += "<div class='tabs'>"
#     for i, name in enumerate(dfs.keys()):
#         active = "active" if i == 0 else ""
#         html += f"<button class='tablink {active}' onclick=\"openTab(event, 'tab-{name}')\">{name}</button>"
#     html += "</div>"

#     # Tabs content
#     for i, (name, df) in enumerate(dfs.items()):
#         styled_df = df.copy()

#         if "Model" in styled_df.columns:
#             styled_df["Model"] = styled_df["Model"].apply(
#                 lambda m: f"<a href='https://huggingface.co/{m}' target='_blank' "
#                           f"style='color:#0044cc;text-decoration:none;'>{m}</a>"
#             )

#         styled_df = apply_gradient(styled_df)

#         table_html = styled_df.to_html(
#             classes=f"display compact cell-border", index=False, escape=False
#         )

#         display = "block" if i == 0 else "none"
#         html += f"<div id='tab-{name}' class='tabcontent' style='display:{display}'>"
#         html += table_html
#         html += "</div>"

#     # JS
#     html += """
#     <script>
#     function openTab(evt, tabId) {
#         var i, tabcontent, tablinks;
#         tabcontent = document.getElementsByClassName("tabcontent");
#         for (i = 0; i < tabcontent.length; i++) {
#             tabcontent[i].style.display = "none";
#         }
#         tablinks = document.getElementsByClassName("tablink");
#         for (i = 0; i < tablinks.length; i++) {
#             tablinks[i].classList.remove("active");
#         }
#         document.getElementById(tabId).style.display = "block";
#         evt.currentTarget.classList.add("active");
#     }
#     $(document).ready(function() {
#         $('table.display').DataTable({
#             scrollX: true,
#             paging: false,
#             searching: false,
#             info: false
#         });
#     });
#     </script>
#     """

#     return html

# # ---------------- Filtering ----------------
# def filter_table(search: str, tasks: list, df: pd.DataFrame) -> str:
#     if search:
#         df = df[df["Model"].str.contains(search, case=False, na=False)]
#     if tasks:
#         base_cols = ["Model", "Precision", "#Params (B)"]
#         selected_cols = base_cols + [col for col in tasks if col in df.columns]
#         df = df[selected_cols]
#     return df.to_html(index=False, escape=False)

# # ---------------- Submit Request ----------------
# HF_TOKEN = os.environ.get("HF_TOKEN")
# DATASET_NAME = "ailabs-itrc/requests"

# def submit_request(model_name, revision, precision, weight_type,
#                    model_type, params, license_str, private_bool):
#     url = f"https://huggingface.co/{model_name}"
#     try:
#         try:
#             dataset = load_dataset(DATASET_NAME, split="train")
#         except Exception:
#             dataset = Dataset.from_list([])

#         existing_models = [entry["model"] for entry in dataset if "model" in entry]
#         if model_name in existing_models:
#             return f"⚠️ Model '{model_name}' already exists."

#         tehran = pytz.timezone("Asia/Tehran")
#         now = datetime.now(tehran)
#         persian_time = now.strftime("%Y-%m-%dT%H:%M:%S.%f")

#         new_entry = {
#             "id": str(uuid.uuid4()),
#             "model": model_name,
#             "revision": revision,
#             "precision": precision,
#             "weight_type": weight_type,
#             "submitted_time": persian_time,
#             "model_type": model_type,
#             "params": float(params) if params else None,
#             "license": license_str,
#             "private": bool(private_bool),
#             "status": "❗ unknown"
#         }

#         dataset = dataset.add_item(new_entry)
#         dataset.push_to_hub(DATASET_NAME, token=HF_TOKEN)

#         return f"✅ Submitted! ID: {new_entry['id']}"

#     except Exception as e:
#         return f"❌ Error: {str(e)}"

import pandas as pd
import json
import os
import uuid
from datetime import datetime
import pytz
from datasets import load_dataset, Dataset

# ---------------- Task Groups ----------------
TASK_GROUPS = {
    "SBU": [
        "General Medicine",
        "Complementary & Alternative Medicine",
        "Emergency Medicine",
        "Constitution of IRI",
        "Other legal Domains",
        "Religion",
        "Grammar, Proverbs & Strings",
        "Lexical Semantics",
        "Encyclopedic Knowledge",
        "Recommendation & Human Preferences",
        "Text Completion",
        "Poems & Lyrics",
        "Paraphrase",
        "Style Transfer",
        "Emotion",
        "Irony",
        "Metaphor",
        "Empathy, Intimacy & Trust",
        "Ethics & Bias",
        "Toxicity",
        "Human Rights",
    ],
    "UQ": [
        "belebel_e",
        "farstail",
        "pn_summary_categorization",
        "pn_summary_summarize",
        "Parsinlu_translation_fa_en",
        "Parsinlu_translation_en_fa",
        "persian_MMLU",
        "ARC_easy",
        "ARC_challenge",
    ],
    "AUT": []
}

# ---------------- Styles ----------------
HTML_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600&family=Roboto:wght@400;500&display=swap');

    body, table {
        font-family: 'Vazirmatn', 'Roboto', sans-serif;
    }
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        border: 1px solid #eee;
    }
    .styled-table th {
        background-color: #f9f9f9;
        font-weight: 600;
        padding: 6px 8px;
        border: 1px solid #eee;
        text-align: center;
        font-size: 12px;
    }
    .styled-table td {
        padding: 6px 8px;
        border: 1px solid #eee;
        font-size: 12px;
        color: #222;
        background-repeat: no-repeat;
        background-size: 100% 100%;
        text-align: center;
    }
    .styled-table tr:nth-child(even) {
        background-color: #fcfcfc;
    }
    .styled-table tr:hover {
        background-color: #f1f7ff;
    }
</style>
"""

# ---------------- Load Data ----------------
def load_all_data(path):
    rows = []
    with open(path + "results.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    df = pd.DataFrame(rows)

    # ستون‌های مشترک
    base_cols = ["Model", "Precision", "#Params (B)"]

    # دیتافریم جدا برای هر گروه
    dfs = {}
    for group, tasks in TASK_GROUPS.items():
        cols = base_cols + [col for col in tasks if col in df.columns]
        dfs[group] = df[cols].copy()

    return dfs

# ---------------- Gradient ----------------
# def value_to_gradient_range(value: float, min_val: float = 0, max_val: float = 100) -> str:
#     ratio = (value - min_val) / (max_val - min_val)
#     ratio = max(0, min(1, ratio))
#     red = int(255 * (1 - ratio))
#     green = int(255 * ratio)
#     blue = 100
#     return f"linear-gradient(90deg, rgba({red},{green},{blue},0.3), rgba({red},{green},{blue},0.8))"
def value_to_gradient_range(value: float, min_val: float = 0, max_val: float = 100) -> str:
    """
    Map value (0-100) to a pastel gradient background without matplotlib.
    Colors: pink → yellow → green (pastel).
    """
    ratio = (value - min_val) / (max_val - min_val)
    ratio = max(0, min(1, ratio))

    # رنگ‌های پاستیلی (RGB)
    pink = (255, 179, 186)   # #ffb3ba
    yellow = (255, 245, 186) # #fff5ba
    green = (186, 255, 201)  # #baffc9

    if ratio < 0.5:
        # Interpolate pink → yellow
        t = ratio / 0.5
        r = int(pink[0] + t * (yellow[0] - pink[0]))
        g = int(pink[1] + t * (yellow[1] - pink[1]))
        b = int(pink[2] + t * (yellow[2] - pink[2]))
    else:
        # Interpolate yellow → green
        t = (ratio - 0.5) / 0.5
        r = int(yellow[0] + t * (green[0] - yellow[0]))
        g = int(yellow[1] + t * (green[1] - yellow[1]))
        b = int(yellow[2] + t * (green[2] - yellow[2]))

    return f"linear-gradient(90deg, rgba({r},{g},{b},0.4), rgba({r},{g},{b},0.9))"

# ---------------- Table (Single) ----------------------------2222222222222222222222222222222222222222222222222222222222222222222222222222


# def df_to_styled_html(df: pd.DataFrame) -> str:
#     if df.empty:
#         return "<p>No results found.</p>"

#     # حذف ردیف‌های نامعتبر
#     task_columns = [c for c in df.columns if c not in ["Model", "Precision", "#Params (B)"]]
#     df = df.dropna(how="all", subset=task_columns)
#     df = df[~df[task_columns].apply(lambda row: all(str(v) in ["--", "nan", "NaN"] for v in row), axis=1)]

#     # استایل
#     html = HTML_STYLE + """
#     <style>
#         .styled-table { width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #eee; }
#         .styled-table th, .styled-table td { padding: 6px 8px; border: 1px solid #eee; text-align: center; font-size: 12px; }
#         .styled-table th { background-color: #f9f9f9; cursor: pointer; position: relative; }
#         .styled-table th .sort-icons { position: absolute; right: 4px; top: 50%; transform: translateY(-50%); font-size: 10px; }
#         .styled-table td.model-col { color: #0077ff; font-weight: normal; }
#         .styled-table tr:nth-child(even) { background-color: #fcfcfc; }
#         .styled-table tr:hover { background-color: #f1f7ff; }
#     </style>
#     """

#     # جدول
#     html += "<table id='leaderboard' class='styled-table'>"
#     html += "<thead><tr>"
#     for col in df.columns:
#         if col in ["Model", "Precision", "#Params (B)"]:
#             html += f"<th>{col}</th>"
#         else:
#             html += f"<th>{col}<span class='sort-icons'>▲▼</span></th>"
#     html += "</tr></thead><tbody>"

#     for _, row in df.iterrows():
#         html += "<tr>"
#         for col in df.columns:
#             value = row[col]
#             if isinstance(value, (int, float)):
#                 if col == "#Params (B)":
#                     html += f"<td>{int(value)}</td>"
#                 else:
#                     bg = value_to_gradient_range(value)
#                     html += f"<td data-value='{value}' style='background:{bg};'>{value:.1f}</td>"
#             else:
#                 if col == "Model":
#                     html += f"<td class='model-col'>{value}</td>"
#                 else:
#                     html += f"<td>{value}</td>"
#         html += "</tr>"
#     html += "</tbody></table>"

#     # جاوااسکریپت مرتب‌سازی
#     html += """
#     <script>
#     document.querySelectorAll("#leaderboard th").forEach((th, index) => {
#         th.addEventListener("click", () => {
#             const table = th.closest("table");
#             const tbody = table.querySelector("tbody");
#             const rows = Array.from(tbody.querySelectorAll("tr"));
#             const ascending = th.classList.toggle("asc");
#             th.classList.remove("desc");
#             if (!ascending) {
#                 th.classList.add("desc");
#             }
#             rows.sort((a, b) => {
#                 let aVal = a.children[index].getAttribute("data-value") || a.children[index].innerText;
#                 let bVal = b.children[index].getAttribute("data-value") || b.children[index].innerText;
#                 if (!isNaN(aVal) && !isNaN(bVal)) {
#                     aVal = parseFloat(aVal); bVal = parseFloat(bVal);
#                 }
#                 return ascending ? aVal - bVal : bVal - aVal;
#             });
#             rows.forEach(r => tbody.appendChild(r));
#         });
#     });
#     </script>
#     """

#     return html
# def df_to_styled_html(df: pd.DataFrame, table_id: str="leaderboard" ) -> str:
#     if df.empty:
#         return "<p>No results found.</p>"

#     # حذف ردیف‌های نامعتبر
#     task_columns = [c for c in df.columns if c not in ["Model", "Precision", "#Params (B)"]]
#     df = df.dropna(how="all", subset=task_columns)
#     df = df[~df[task_columns].apply(lambda row: all(str(v) in ["--", "nan", "NaN"] for v in row), axis=1)]

#     # استایل
#     html = HTML_STYLE + f"""
#     <style>
#         .styled-table {{ width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #eee; }}
#         .styled-table th, .styled-table td {{ padding: 6px 8px; border: 1px solid #eee; text-align: center; font-size: 12px; }}
#         .styled-table th {{ background-color: #f9f9f9; cursor: pointer; position: relative; }}
#         .styled-table th .sort-icons {{ position: absolute; right: 4px; top: 50%; transform: translateY(-50%); font-size: 10px; }}
#         .styled-table td.model-col {{ color: #0077ff; font-weight: normal; }}
#         .styled-table tr:nth-child(even) {{ background-color: #fcfcfc; }}
#         .styled-table tr:hover {{ background-color: #f1f7ff; }}
#     </style>
#     """

#     # جدول
#     html += f"<table id='{table_id}' class='styled-table'>"
#     html += "<thead><tr>"
#     for col in df.columns:
#         if col in ["Model", "Precision", "#Params (B)"]:
#             html += f"<th>{col}</th>"
#         else:
#             html += f"<th>{col}<span class='sort-icons'>▲▼</span></th>"
#     html += "</tr></thead><tbody>"

#     for _, row in df.iterrows():
#         html += "<tr>"
#         for col in df.columns:
#             value = row[col]
#             if isinstance(value, (int, float)):
#                 if col == "#Params (B)":
#                     html += f"<td>{int(value)}</td>"
#                 else:
#                     bg = value_to_gradient_range(value)
#                     html += f"<td data-value='{value}' style='background:{bg};'>{value:.1f}</td>"
#             else:
#                 if col == "Model":
#                     html += f"<td class='model-col'>{value}</td>"
#                 else:
#                     html += f"<td>{value}</td>"
#         html += "</tr>"
#     html += "</tbody></table>"

#     # جاوااسکریپت مرتب‌سازی
#     html += f"""
#     <script>
#     document.querySelectorAll("#{table_id} th").forEach((th, index) => {{
#         th.addEventListener("click", () => {{
#             const table = th.closest("table");
#             const tbody = table.querySelector("tbody");
#             const rows = Array.from(tbody.querySelectorAll("tr"));
#             const ascending = th.classList.toggle("asc");
#             th.classList.remove("desc");
#             if (!ascending) {{
#                 th.classList.add("desc");
#             }}
#             rows.sort((a, b) => {{
#                 let aVal = a.children[index].getAttribute("data-value") || a.children[index].innerText;
#                 let bVal = b.children[index].getAttribute("data-value") || b.children[index].innerText;
#                 if (!isNaN(aVal) && !isNaN(bVal)) {{
#                     aVal = parseFloat(aVal); bVal = parseFloat(bVal);
#                 }}
#                 return ascending ? aVal - bVal : bVal - aVal;
#             }});
#             rows.forEach(r => tbody.appendChild(r));
#         }});
#     }});
#     </script>
#     """

#     return html

def df_to_styled_html(df: pd.DataFrame, table_id: str) -> str:
    if df.empty:
        return "<p>No results found.</p>"

    # حذف ردیف‌های نامعتبر
    task_columns = [c for c in df.columns if c not in ["Model", "Precision", "#Params (B)"]]
    df = df.dropna(how="all", subset=task_columns)
    df = df[~df[task_columns].apply(lambda row: all(str(v) in ["--", "nan", "NaN"] for v in row), axis=1)]

    # استایل
    html = f"""
    <style>
        #{table_id} {{
            width: 100%; border-collapse: collapse; font-size: 13px; border: 1px solid #eee;
        }}
        #{table_id} th, #{table_id} td {{
            padding: 6px 8px; border: 1px solid #eee; text-align: center; font-size: 12px;
        }}
        #{table_id} th {{
            background-color: #f9f9f9;
        }}
        #{table_id} td.model-col {{
            color: #0077ff; font-weight: normal;
        }}
        #{table_id} tr:nth-child(even) {{
            background-color: #fcfcfc;
        }}
        #{table_id} tr:hover {{
            background-color: #f1f7ff;
        }}
    </style>
    """

    # جدول
    html += f"<table id='{table_id}' class='styled-table'>"
    html += "<thead><tr>"
    for col in df.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            value = row[col]
            if isinstance(value, (int, float)):
                if col == "#Params (B)":
                    html += f"<td>{int(value)}</td>"
                else:
                    bg = value_to_gradient_range(value)
                    html += f"<td style='background:{bg};'>{value:.1f}</td>"
            else:
                if col == "Model":
                    html += f"<td class='model-col'>{value}</td>"
                else:
                    html += f"<td>{value}</td>"
        html += "</tr>"
    html += "</tbody></table>"

    return html


# ---------------- Table (Tabbed) ----------------
def df_to_tabbed_html(dfs: dict[str, pd.DataFrame]) -> str:
    html = HTML_STYLE + """
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

    <style>
        .tabs { margin-bottom: 15px; font-family: 'Vazirmatn', 'Roboto', sans-serif; }
        .tabs button {
            background: #eee; border: none; padding: 10px 18px;
            cursor: pointer; margin-right: 5px; border-radius: 8px 8px 0 0;
            font-size: 14px; font-weight: 500;
        }
        .tabs button.active { background: #0044cc; color: white; }
        .tabcontent { display: none; }
        table.dataTable { width: 100% !important; font-size: 13px; }
        td, th { text-align: center; vertical-align: middle; }
    </style>
    """

    # Tabs header
    html += "<div class='tabs'>"
    for i, name in enumerate(dfs.keys()):
        active = "active" if i == 0 else ""
        html += f"<button class='tablink {active}' onclick=\"openTab(event, 'tab-{name}')\">{name}</button>"
    html += "</div>"

    # Tabs content
    for i, (name, df) in enumerate(dfs.items()):
        styled_df = df.copy()

        task_columns = [c for c in styled_df.columns if c not in ["Model", "Precision", "#Params (B)"]]
        styled_df = styled_df.dropna(how="all", subset=task_columns)
        styled_df = styled_df[~styled_df[task_columns].apply(
            lambda row: all(str(v) in ["--", "nan", "NaN"] for v in row), axis=1
        )]

        if "Model" in styled_df.columns:
            styled_df["Model"] = styled_df["Model"].apply(
                lambda m: f"<a href='https://huggingface.co/{m}' target='_blank' "
                          f"style='color:#0044cc;text-decoration:none;font-weight:500;'>{m}</a>"
                if isinstance(m, str) and "/" in m else str(m)
            )

        def style_val(val, col):
            if isinstance(val, (int, float)):
                if col == "#Params (B)":
                    return str(int(val))
                bg = value_to_gradient_range(val)
                return f"<div style='background:{bg};padding:2px'>{val:.2f}</div>"
            return val

        styled_df = styled_df.apply(lambda row: [style_val(v, c) for c, v in row.items()],
                                    axis=1, result_type="broadcast")
        styled_df.columns = df.columns

        table_html = styled_df.to_html(classes="display compact cell-border",
                                       index=False, escape=False)

        display = "block" if i == 0 else "none"
        html += f"<div id='tab-{name}' class='tabcontent' style='display:{display}'>"
        html += table_html
        html += "</div>"

    html += """
    <script>
    function openTab(evt, tabId) {
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        tablinks = document.getElementsByClassName("tablink");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].classList.remove("active");
        }
        document.getElementById(tabId).style.display = "block";
        evt.currentTarget.classList.add("active");
    }
    $(document).ready(function() {
        $('table.display').DataTable({
            scrollX: true,
            paging: false,
            searching: false,
            info: false
        });
    });
    </script>
    """

    return html

# ---------------- Filter ----------------
# def filter_table(search: str, tasks: list, df: pd.DataFrame) -> str:
#     if search:
#         df = df[df["Model"].str.contains(search, case=False, na=False)]
#     if tasks:
#         base_cols = ["Model", "Precision", "#Params (B)"]
#         selected_cols = base_cols + [c for c in tasks if c in df.columns]
#         df = df[selected_cols]
#     return df_to_styled_html(df)

# ---------------- Filter ----------------
def filter_table(search: str, tasks: list, df: pd.DataFrame, table_id: str = "leaderboard") -> str:
    if search:
        df = df[df["Model"].str.contains(search, case=False, na=False)]
    if tasks:
        base_cols = ["Model", "Precision", "#Params (B)"]
        selected_cols = base_cols + [c for c in tasks if c in df.columns]
        df = df[selected_cols]
    return df_to_styled_html(df, table_id=table_id)


# ---------------- Submit Request ----------------
DATASET_NAME = "ailabs-itrc/requests"
HF_TOKEN = os.environ.get("HF_TOKEN")

def submit_request(model_name, revision, precision, weight_type,
                   model_type, params, license_str, private_bool):
    """Submit a model request to HuggingFace dataset."""
    try:
        try:
            dataset = load_dataset(DATASET_NAME, split="train", token=HF_TOKEN)
        except Exception:
            dataset = Dataset.from_list([])

        existing_models = [entry["model"] for entry in dataset if "model" in entry]
        if model_name in existing_models:
            return f"⚠️ Model '{model_name}' already exists."

        tehran = pytz.timezone("Asia/Tehran")
        now = datetime.now(tehran)
        persian_time = now.strftime("%Y-%m-%dT%H:%M:%S")

        new_entry = {
            "id": str(uuid.uuid4()),
            "model": model_name,
            "revision": revision,
            "precision": precision,
            "weight_type": weight_type,
            "submitted_time": persian_time,
            "model_type": model_type,
            "params": float(params) if params else None,
            "license": license_str,
            "private": bool(private_bool),
            "status": "⏳ pending"
        }

        dataset = dataset.add_item(new_entry)
        dataset.push_to_hub(DATASET_NAME, token=HF_TOKEN)

        return f"✅ Submitted! ID: {new_entry['id']}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# # import pandas as pd
# # import json

# # TASK_GROUPS = {
# #     "SBU": [
# #         "General Medicine",
# #         "Complementary & Alternative Medicine",
# #         "Emergency Medicine",
# #         "Constitution of IRI",
# #         "Other legal Domains",
# #         "Religion",
# #         "Grammar, Proverbs & Strings",
# #         "Lexical Semantics",
# #         "Encyclopedic Knowledge",
# #         "Recommendation & Human Preferences",
# #         "Text Completion",
# #         "Poems & Lyrics",
# #         "Paraphrase",
# #         "Style Transfer",
# #         "Emotion",
# #         "Irony",
# #         "Metaphor",
# #         "Empathy, Intimacy & Trust",
# #         "Ethics & Bias",
# #         "Toxicity",
# #         "Human Rights"
# #     ],
# #     "UQ": [
# #         "belebel_e",
# #         "farstail",
# #         "pn_summary_categorization",
# #         "pn_summary_summarize",
# #         "Parsinlu_translation_fa_en",
# #         "Parsinlu_translation_en_fa",
# #         "persian_MMLU",
# #         "ARC_easy",
# #         "ARC_challenge"
# #     ],
# #     "AUT": []
# # }


# # def load_all_data(path):
# #     rows = []
# #     with open(path + "results.jsonl", "r", encoding="utf-8") as f:
# #         for line in f:
# #             rows.append(json.loads(line))

# #     df = pd.DataFrame(rows)

# #     # ستون‌های مشترک
# #     base_cols = ["Model", "Precision", "#Params (B)"]

# #     # دیتافریم جدا برای هر گروه
# #     dfs = {}
# #     for group, tasks in TASK_GROUPS.items():
# #         cols = base_cols + [col for col in tasks if col in df.columns]
# #         dfs[group] = df[cols].copy()

# #     return dfs

# # def value_to_gradient_range(value: float, min_val: float = 0, max_val: float = 100) -> str:
# #     """
# #     Map a numeric value to a green-to-red gradient (good → bad).
# #     0 = قرمز / 100 = سبز.
# #     """
# #     # نرمال‌سازی بین 0 و 1
# #     ratio = (value - min_val) / (max_val - min_val)
# #     ratio = max(0, min(1, ratio))

# #     # تبدیل ratio به رنگ (قرمز → زرد → سبز)
# #     red = int(255 * (1 - ratio))
# #     green = int(255 * ratio)
# #     blue = 100  # کمی آبی برای خوشگل‌تر شدن

# #     return f"linear-gradient(90deg, rgba({red},{green},{blue},0.3), rgba({red},{green},{blue},0.8))"


# # def df_to_styled_html(df: pd.DataFrame) -> str:
# #     """Convert DataFrame into styled HTML leaderboard table with gradient coloring."""

# #     if df.empty:
# #         return "<p>No results found.</p>"

# #     # 🔹 حذف ردیف‌هایی که هیچ مقداری ندارن (همه NaN یا "--")
# #     task_columns = [col for col in df.columns if col not in ["Model", "Precision", "#Params (B)"]]
# #     df = df.dropna(how="all", subset=task_columns)
# #     df = df[~df[task_columns].apply(lambda row: all(str(v) in ["--", "nan", "NaN"] for v in row), axis=1)]

# #     # 🔹 ساخت جدول HTML دستی (برای کنترل گرادیان)
# #     html = "<table class='styled-table'>"

# #     # ---- Header ----
# #     html += "<thead><tr>"
# #     for col in df.columns:
# #         html += f"<th>{col}</th>"
# #     html += "</tr></thead><tbody>"

# #     # ---- Data Rows ----
# #     for _, row in df.iterrows():
# #         html += "<tr>"
# #         for col in df.columns:
# #             value = row[col]
# #             if isinstance(value, (int, float)):
# #                 if col == "#Params (B)":
# #                     # برای تعداد پارامترها بدون اعشار
# #                     html += f"<td>{int(value)}</td>"
# #                 else:
# #                     bg = value_to_gradient_range(value)
# #                     html += f"<td style='background:{bg};'>{value:.1f}</td>"
# #             else:
# #                 html += f"<td>{value}</td>"
# #         html += "</tr>"

# #     html += "</tbody></table>"
# #     return HTML_STYLE + html



# # def filter_table(search: str, tasks: list, df: pd.DataFrame) -> str:
# #     if search:
# #         df = df[df["Model"].str.contains(search, case=False, na=False)]
# #     if tasks:
# #         base_cols = ["Model", "Precision", "#Params (B)"]
# #         selected_cols = base_cols + [col for col in tasks if col in df.columns]
# #         df = df[selected_cols]
# #     return df_to_styled_html(df)


# # def submit_request(*args, **kwargs):
# #     return "✅ Model submission received!"

# # # from datasets import load_dataset, Dataset
# # # import pandas as pd
# # # import json
# # # from datetime import datetime
# # # import pytz
# # # import uuid
# # # import os
# # # import requests

# # # # Dataset name for requests
# # # DATASET_NAME = "ailabs-itrc/requests"

# # # TASK_GROUPS = {
# # #     "SBU": [
# # #         "General Medicine",
# # #         "Complementary & Alternative Medicine",
# # #         "Emergency Medicine",
# # #         "Constitution of IRI",
# # #         "Other legal Domains",
# # #         "Religion",
# # #         "Grammar, Proverbs & Strings",
# # #         "Lexical Semantics",
# # #         "Encyclopedic Knowledge",
# # #         "Recommendation & Human Preferences",
# # #         "Text Completion",
# # #         "Poems & Lyrics",
# # #         "Paraphrase",
# # #         "Style Transfer",
# # #         "Emotion",
# # #         "Irony",
# # #         "Metaphor",
# # #         "Empathy, Intimacy & Trust",
# # #         "Ethics & Bias",
# # #         "Toxicity",
# # #         "Human Rights"
# # #     ],
# # #     "UQ": [
# # #         "belebel_e",
# # #         "farstail",
# # #         "pn_summary_categorization",
# # #         "pn_summary_summarize",
# # #         "Parsinlu_translation_fa_en",
# # #         "Parsinlu_translation_en_fa",
# # #         "persian_MMLU",
# # #         "ARC_easy",
# # #         "ARC_challenge"
# # #     ],
# # #     "AUT": []
# # # }

# # # HF_TOKEN = os.environ.get("HF_TOKEN")
# # # REQUESTS_FILE = "requests.jsonl"

# # # HTML_STYLE = """
# # # <style>
# # #     .styled-table {
# # #         width: 100%;
# # #         border-collapse: collapse;
# # #         font-size: 13px;
# # #         border: 1px solid #eee;
# # #     }
# # #     .styled-table th {
# # #         background-color: #f9f9f9;
# # #         font-weight: 600;
# # #         padding: 6px 8px;
# # #         border: 1px solid #eee;
# # #         text-align: center;
# # #         font-size: 12px;
# # #     }
# # #     .styled-table td {
# # #         padding: 6px 8px;
# # #         border: 1px solid #eee;
# # #         font-size: 12px;
# # #         color: #222;
# # #         background-repeat: no-repeat;
# # #         background-size: 100% 100%;
# # #         text-align: center;
# # #     }
# # #     .styled-table tr:nth-child(even) {
# # #         background-color: #fcfcfc;
# # #     }
# # # </style>
# # # """

# # # def load_data(jsonl_file_path: str) -> pd.DataFrame:
# # #     """Load leaderboard data from a jsonl file."""
# # #     if not os.path.exists(jsonl_file_path):
# # #         return pd.DataFrame()
# # #     records = []
# # #     with open(jsonl_file_path, "r", encoding="utf-8") as f:
# # #         for line in f:
# # #             try:
# # #                 records.append(json.loads(line))
# # #             except json.JSONDecodeError:
# # #                 continue
# # #     df = pd.DataFrame(records)
# # #     return df

# # # def load_all_data(folder="data/") -> pd.DataFrame:
# # #     """Load and merge all jsonl result files inside a folder."""
# # #     dfs = []
# # #     if os.path.exists(folder):
# # #         for fname in os.listdir(folder):
# # #             if fname.endswith(".jsonl"):
# # #                 df = load_data(os.path.join(folder, fname))
# # #                 dfs.append(df)
# # #     if dfs:
# # #         df = pd.concat(dfs, axis=0, ignore_index=True).fillna("-")
# # #         return df
# # #     return pd.DataFrame()

# # # def value_to_gradient_range(value: float) -> str:
# # #     """Return background gradient color based on value (0-100)."""
# # #     value = max(0, min(100, value))
# # #     if value < 30:
# # #         color = "#f8d7da"
# # #     elif value < 60:
# # #         color = "#fff3cd"
# # #     else:
# # #         color = "#d4edda"
# # #     return f"linear-gradient(to right, {color} {value}%, transparent {value}%)"

# # # def df_to_styled_html(df: pd.DataFrame) -> str:
# # #     """Convert DataFrame into styled HTML leaderboard table."""
# # #     if df.empty:
# # #         return "<p>No data found.</p>"

# # #     df = df.copy()
# # #     if "Model" in df.columns:
# # #         df["Model"] = df["Model"].apply(
# # #             lambda m: f"<a href='https://huggingface.co/{m}' target='_blank' style='color:#0044cc;text-decoration:none;'>{m}</a>"
# # #         )

# # #     # توجه کن که توی JSON اسمش Avg هست
# # #     fixed_cols = ["Model", "Precision", "#Params (B)", "Avg"]

# # #     html = "<table class='styled-table'>"

# # #     # ---- Header Row 1 (Main categories) ----
# # #     html += "<thead><tr>"
# # #     for col in fixed_cols:
# # #         if col in df.columns:
# # #             html += f"<th rowspan='2'>{col}</th>"
# # #     for group_name, cols in TASK_GROUPS.items():
# # #         valid_cols = [c for c in cols if c in df.columns]
# # #         if valid_cols:
# # #             html += f"<th colspan='{len(valid_cols)}'>{group_name}</th>"
# # #     html += "</tr>"

# # #     # ---- Header Row 2 (Subtasks) ----
# # #     html += "<tr>"
# # #     for cols in TASK_GROUPS.values():
# # #         for col in cols:
# # #             if col in df.columns:
# # #                 html += f"<th>{col}</th>"
# # #     html += "</tr></thead><tbody>"

# # #     # ---- Data Rows ----
# # #     for _, row in df.iterrows():
# # #         html += "<tr>"
# # #         for col in fixed_cols:
# # #             if col in df.columns:
# # #                 html += f"<td>{row[col]}</td>"
# # #         for cols in TASK_GROUPS.values():
# # #             for col in cols:
# # #                 if col in df.columns:
# # #                     value = row.get(col)

# # #                     # هندل "--" و NaN
# # #                     if pd.isna(value) or str(value).strip() in ["--", "-", "nan"]:
# # #                         html += "<td>-</td>"
# # #                     else:
# # #                         try:
# # #                             val = float(value)
# # #                             bg = value_to_gradient_range(val)
# # #                             html += f"<td style='background: {bg};'>{val:.2f}</td>"
# # #                         except:
# # #                             html += f"<td>{value}</td>"
# # #         html += "</tr>"

# # #     html += "</tbody></table>"
# # #     return HTML_STYLE + html


# # # def apply_gradient(df: pd.DataFrame) -> pd.DataFrame:
# # #     """Apply background gradient to numeric values."""
# # #     df = df.copy()
# # #     for col in df.columns:
# # #         if col not in ["Model", "Precision", "#Params (B)", "Average"]:
# # #             if pd.api.types.is_numeric_dtype(df[col]):
# # #                 df[col] = df[col].apply(
# # #                     lambda v: f"<div style='background:{value_to_gradient_range(v)};padding:4px'>{v:.1f}</div>"
# # #                     if pd.notnull(v) else "-"
# # #                 )
# # #     return df


# # # def df_to_tabbed_html(dfs: dict[str, pd.DataFrame]) -> str:
# # #     """Render multiple DataFrames as tabbed DataTables with gradient coloring."""
# # #     # ---------------- Load DataTables CSS/JS ----------------
# # #     html = """
# # #     <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
# # #     <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
# # #     <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

# # #     <style>
# # #         .tabs { margin-bottom: 15px; }
# # #         .tabs button {
# # #             background: #eee; border: none; padding: 10px 20px;
# # #             cursor: pointer; margin-right: 5px; border-radius: 6px 6px 0 0;
# # #         }
# # #         .tabs button.active { background: #0044cc; color: white; }
# # #         .tabcontent { display: none; }
# # #         table.dataTable { width: 100% !important; font-size: 13px; }
# # #         td, th { text-align: center; vertical-align: middle; }
# # #     </style>
# # #     """

# # #     # ---------------- Tabs header ----------------
# # #     html += "<div class='tabs'>"
# # #     for i, name in enumerate(dfs.keys()):
# # #         active = "active" if i == 0 else ""
# # #         html += f"<button class='tablink {active}' onclick=\"openTab(event, 'tab-{name}')\">{name}</button>"
# # #     html += "</div>"

# # #     # ---------------- Tabs content (tables) ----------------
# # #     for i, (name, df) in enumerate(dfs.items()):
# # #         styled_df = df.copy()

# # #         # لینک برای HuggingFace مدل‌ها
# # #         if "Model" in styled_df.columns:
# # #             styled_df["Model"] = styled_df["Model"].apply(
# # #                 lambda m: f"<a href='https://huggingface.co/{m}' target='_blank' "
# # #                           f"style='color:#0044cc;text-decoration:none;'>{m}</a>"
# # #             )

# # #         # رنگ پس‌زمینه
# # #         styled_df = apply_gradient(styled_df)

# # #         table_html = styled_df.to_html(
# # #             classes=f"display compact cell-border", index=False, escape=False
# # #         )

# # #         display = "block" if i == 0 else "none"
# # #         html += f"<div id='tab-{name}' class='tabcontent' style='display:{display}'>"
# # #         html += table_html
# # #         html += "</div>"

# # #     # ---------------- JS for tabs + DataTables ----------------
# # #     html += """
# # #     <script>
# # #     function openTab(evt, tabId) {
# # #         var i, tabcontent, tablinks;
# # #         tabcontent = document.getElementsByClassName("tabcontent");
# # #         for (i = 0; i < tabcontent.length; i++) {
# # #             tabcontent[i].style.display = "none";
# # #         }
# # #         tablinks = document.getElementsByClassName("tablink");
# # #         for (i = 0; i < tablinks.length; i++) {
# # #             tablinks[i].classList.remove("active");
# # #         }
# # #         document.getElementById(tabId).style.display = "block";
# # #         evt.currentTarget.classList.add("active");
# # #     }
# # #     $(document).ready(function() {
# # #         $('table.display').DataTable({
# # #             scrollX: true,
# # #             paging: false,
# # #             searching: false,
# # #             info: false
# # #         });
# # #     });
# # #     </script>
# # #     """

# # #     return html





# # # def submit_request(model_name, revision, precision, weight_type,
# # #                    model_type, params, license_str, private_bool):
# # #     """Submit a model request to the hub dataset."""
# # #     url = f"https://huggingface.co/{model_name}"
# # #     try:
# # #         try:
# # #             dataset = load_dataset(DATASET_NAME, split="train")
# # #         except Exception:
# # #             dataset = Dataset.from_list([])

# # #         existing_models = [entry["model"] for entry in dataset if "model" in entry]
# # #         if model_name in existing_models:
# # #             return f"⚠️ Model '{model_name}' already exists."

# # #         tehran = pytz.timezone("Asia/Tehran")
# # #         now = datetime.now(tehran)
# # #         persian_time = now.strftime("%Y-%m-%dT%H:%M:%S.%f")

# # #         new_entry = {
# # #             "id": str(uuid.uuid4()),
# # #             "model": model_name,
# # #             "revision": revision,
# # #             "precision": precision,
# # #             "weight_type": weight_type,
# # #             "submitted_time": persian_time,
# # #             "model_type": model_type,
# # #             "params": float(params),
# # #             "license": license_str,
# # #             "private": bool(private_bool),
# # #             "status": "❗ unknown"
# # #         }

# # #         if not is_link_valid(url):
# # #             return f"❌ The model {model_name} does not exist on Hugging Face."

# # #         dataset = dataset.add_item(new_entry)
# # #         dataset.push_to_hub(DATASET_NAME, token=HF_TOKEN)

# # #         return f"✅ Submitted! ID: {new_entry['id']}"

# # #     except Exception as e:
# # #         return f"❌ Error: {str(e)}"


# # # def filter_table(df, keyword: str = "", columns: list = None):
# # #     """
# # #     Filter DataFrame rows by keyword across given columns.
# # #     - df: pandas DataFrame
# # #     - keyword: string to search (case-insensitive)
# # #     - columns: list of column names to search in (default: ["Model"])
# # #     """
# # #     if not keyword:
# # #         return df

# # #     if columns is None:
# # #         columns = ["Model"]

# # #     mask = False
# # #     for col in columns:
# # #         if col in df.columns:
# # #             mask = mask | df[col].astype(str).str.contains(keyword, case=False, na=False)

# # #     return df[mask]

