import pandas as pd
import json
import os
import uuid
from datetime import datetime
import pytz
from datasets import load_dataset, Dataset

FIXED_COLUMNS = ["model", "params", "license", "precision", "type"]


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
# ---------------- Style ----------------
HTML_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600&family=Poppins:wght@500;700&display=swap');

    body, table {
        font-family: 'Vazirmatn', 'Poppins', sans-serif;
    }
    .main-title {
    font-family: 'Poppins', 'Vazirmatn', sans-serif;
    font-size: 34px;
    font-weight: 500;
    color: #222;
    text-align: center;
    margin: 10px 0 20px 0;
}

    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        border: 1px solid #f5f5f5;
    }
    .styled-table th {
        background-color: #fafafa;
        font-weight: 600;
        padding: 8px 10px;
        border: 1px solid #f3f3f3;
        text-align: center;
        font-size: 12px;
    }
    .styled-table td {
        padding: 6px 8px;
        border: 1px solid #f3f3f3;
        font-size: 12px;
        color: #222;
        text-align: center;
        background-repeat: no-repeat;
        background-size: 100% 100%;
    }
    .styled-table tr:nth-child(even) {
        background-color: #fcfcfc;
    }
    .styled-table tr:hover {
        background-color: #f1f7ff;
    }
    .model-col a {
        color: #0066cc;
        text-decoration: none;
        font-weight: 500;
    }
    .model-col a:hover {
        text-decoration: underline;
    }
</style>
"""


# ---------------- Load Data ----------------
def load_all_data(path: str):
    """Load results.jsonl and split into dataframes by task groups."""
    rows = []
    with open(os.path.join(path, "results.jsonl"), "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    df = pd.DataFrame(rows)

    base_cols = ["Model", "Precision", "#Params (B)", "Context"]
    dfs = {}

    for group, tasks in TASK_GROUPS.items():
        cols = base_cols + [col for col in tasks if col in df.columns]
        sub_df = df[cols].copy()

        for col in tasks:
            if col in sub_df.columns:
                sub_df[col] = pd.to_numeric(sub_df[col], errors="coerce")

        dfs[group] = sub_df

    return dfs
    
def sort_dataframe(df: pd.DataFrame, col: str, ascending: bool = True):
    if col in df.columns:
        return df.sort_values(by=col, ascending=ascending).reset_index(drop=True)
    return df

# ---------------- Gradient ----------------
def value_to_gradient_range(value: float, min_val: float = 0, max_val: float = 100) -> str:
    """
    Map value (0-100) to a pastel gradient background.
    Colors: pink → yellow → green (pastel).
    """
    ratio = (value - min_val) / (max_val - min_val)
    ratio = max(0, min(1, ratio))

    pink = (255, 179, 186)   # #ffb3ba
    yellow = (255, 245, 186) # #fff5ba
    green = (186, 255, 201)  # #baffc9

    if ratio < 0.5:
        # Pink → Yellow
        t = ratio / 0.5
        r = int(pink[0] + t * (yellow[0] - pink[0]))
        g = int(pink[1] + t * (yellow[1] - pink[1]))
        b = int(pink[2] + t * (yellow[2] - pink[2]))
    else:
        # Yellow → Green
        t = (ratio - 0.5) / 0.5
        r = int(yellow[0] + t * (green[0] - yellow[0]))
        g = int(yellow[1] + t * (green[1] - yellow[1]))
        b = int(yellow[2] + t * (green[2] - yellow[2]))

    return f"linear-gradient(90deg, rgba({r},{g},{b},0.4), rgba({r},{g},{b},0.9))"

# ---------------- Table Renderer ----------------
# def df_to_styled_html(df: pd.DataFrame, table_id: str = "leaderboard") -> str:
def df_to_styled_html(
    df: pd.DataFrame, 
    table_id: str = "leaderboard", 
    active_col=None, 
    ascending=None
) -> str:
    """Convert DataFrame into styled HTML leaderboard table with gradients and sortable headers (JS)."""
    if df.empty:
        return "<p>No results found.</p>"

    task_columns = [c for c in df.columns if c not in ["Model", "Precision", "#Params (B)", "License", "Organization", "Context"]]
    df = df.dropna(how="all", subset=task_columns)
    df = df[~df[task_columns].apply(lambda row: all(str(v) in ["--", "nan", "NaN"] for v in row), axis=1)]

    if "Model" in df.columns:
        def linkify(m):
            if isinstance(m, str) and "/" in m:
                if m.lower().startswith(("openai/", "anthropic/", "google/")):
                    return str(m)
                return f"<a href='https://huggingface.co/{m}' target='_blank'>{m}</a>"
            return str(m)
        df["Model"] = df["Model"].apply(linkify)

    # HTML Table
    html = HTML_STYLE
    html += f"<table id='{table_id}' class='styled-table'>"
    html += "<thead><tr>"

    for col in df.columns:
        if col.lower() in ["model", "precision", "license", "organization"]:
            html += f"<th>{col}</th>"
        else:
            up_color = "color:#999;"
            down_color = "color:#999;"
            if active_col == col:
                if ascending:
                    up_color = "color:#2563eb;font-weight:bold;"
                else:
                    down_color = "color:#2563eb;font-weight:bold;"

            html += f"""
            <th>
                {col}
                <button style='all:unset;cursor:pointer;' 
                        onclick="document.getElementById('{table_id}_{col}_asc').click()">
                    <span style='{up_color}'>&uarr;</span>
                </button>
                <button style='all:unset;cursor:pointer;' 
                        onclick="document.getElementById('{table_id}_{col}_desc').click()">
                    <span style='{down_color}'>&darr;</span>
                </button>
            </th>
            """

    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            value = row[col]
            if pd.isna(value) or str(value).lower() in ["nan", "none", "--"]:
                html += "<td>--</td>"
            elif isinstance(value, (int, float)):
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
    # return html
    return f"<div class='table-wrapper'>{html}</div>"



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

# # ---------------- Submit Request ----------------
# DATASET_NAME = "ailabs-itrc/requests"
# HF_TOKEN = os.environ.get("HF_TOKEN")

# def submit_request(model_name, revision, precision, weight_type,
#                    model_type, params, license_str, private_bool):
#     """Submit a model request to HuggingFace dataset."""
#     try:
#         try:
#             dataset = load_dataset(DATASET_NAME, split="train", token=HF_TOKEN)
#         except Exception:
#             dataset = Dataset.from_list([])

#         existing_models = [entry["model"] for entry in dataset if "model" in entry]
#         if model_name in existing_models:
#             return f"⚠️ Model '{model_name}' already exists."

#         tehran = pytz.timezone("Asia/Tehran")
#         now = datetime.now(tehran)
#         persian_time = now.strftime("%Y-%m-%dT%H:%M:%S")

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
#             "status": "⏳ pending"
#         }

#         dataset = dataset.add_item(new_entry)
#         dataset.push_to_hub(DATASET_NAME, token=HF_TOKEN)

#         return f"✅ Submitted! ID: {new_entry['id']}"
#     except Exception as e:
#         return f"❌ Error: {str(e)}"

import os, uuid, json
from datetime import datetime
import pytz
import pandas as pd
from datasets import load_dataset, Dataset
from huggingface_hub import HfApi, HfHubHTTPError

HF_TOKEN = os.environ.get("HF_TOKEN")
DATASET_NAME = "ailabs-itrc/requests"   # یا your-username/requests

def ensure_private_dataset(repo_id: str, token: str):
    """
    اگر دیتاست وجود نداشته باشد، آن را به صورت Private می‌سازد.
    اگر وجود دارد، کاری نمی‌کند.
    """
    api = HfApi(token=token)
    try:
        # اگر نبود، بساز
        api.create_repo(
            repo_id=repo_id,          # مثال: "ailabs-itrc/requests"
            repo_type="dataset",
            private=True,             # مهم: پرایوت
            exist_ok=True
        )
    except HfHubHTTPError as e:
        # اگر 403 گرفتی یعنی توکن دسترسی ساخت زیر org را ندارد
        raise RuntimeError(
            f"Cannot create dataset '{repo_id}'. "
            f"Check Org Write permission for this token. Original: {e}"
        )

def submit_request(
    model_name, revision, precision, weight_type,
    model_type, params, license_str, private_bool
):
    try:
        if not HF_TOKEN:
            return "❌ Error: Secret HF_TOKEN not found in Space."

        # 1) مطمئن شو دیتاست وجود دارد (و پرایوت است)
        ensure_private_dataset(DATASET_NAME, HF_TOKEN)

        # 2) دیتاست را بخوان (اگر خالی بود، از لیست خالی شروع می‌کنیم)
        try:
            dataset = load_dataset(DATASET_NAME, split="train", token=HF_TOKEN)
        except Exception:
            dataset = Dataset.from_list([])  # دیتاست جدید/خالی

        # 3) چک تکراری نبودن
        existing_models = [entry.get("model") for entry in dataset]
        if model_name in existing_models:
            return f"⚠️ Model '{model_name}' already exists."

        # 4) رکورد جدید
        tehran = pytz.timezone("Asia/Tehran")
        now = datetime.now(tehran).strftime("%Y-%m-%dT%H:%M:%S")

        new_entry = {
            "id": str(uuid.uuid4()),
            "model": model_name,
            "revision": revision,
            "precision": precision,
            "weight_type": weight_type,
            "submitted_time": now,
            "model_type": model_type,
            "params": float(params) if (params not in [None, ""]) else None,
            "license": license_str,
            "private": bool(private_bool),
            "status": "⏳ pending"
        }

        dataset = dataset.add_item(new_entry)

        # 5) پوش به هاب
        dataset.push_to_hub(DATASET_NAME, token=HF_TOKEN)

        return f"✅ Submitted! ID: {new_entry['id']}"
    except HfHubHTTPError as e:
        # خطاهای هاب را خواناتر کن
        return (
            "❌ Error while pushing to Hub:\n"
            f"{e}\n\n"
            "راهنما: اگر 403 می‌بینی، توکن باید Org Write برای 'ailabs-itrc' داشته باشد "
            "یا DATASET_NAME را موقتاً به فضای شخصی خودت ببری."
        )
    except Exception as e:
        return f"❌ Error: {e}"
