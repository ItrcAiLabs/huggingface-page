# import pandas as pd

# # ---------------- Style ----------------
# HTML_STYLE = """
# <style>
#     @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600&family=Poppins:wght@500;700&display=swap');
#     body, table {
#         font-family: 'Vazirmatn', 'Poppins', sans-serif;
#     }
#     .main-title {
#         font-family: 'Poppins', 'Vazirmatn', sans-serif;
#         font-size: 34px;
#         font-weight: 500;
#         color: #222;
#         text-align: center;
#         margin: 10px 0 20px 0;
#     }
#     .styled-table {
#         width: 100%;
#         border-collapse: collapse;
#         font-size: 13px;
#         border: 1px solid #f5f5f5;
#     }
#     .styled-table th {
#         background-color: #fafafa;
#         font-weight: 600;
#         padding: 8px 10px;
#         border: 1px solid #f3f3f3;
#         text-align: center;
#         font-size: 12px;
#     }
#     .styled-table td {
#         padding: 6px 8px;
#         border: 1px solid #f3f3f3;
#         font-size: 12px;
#         color: #222;
#         text-align: center;
#         background-repeat: no-repeat;
#         background-size: 100% 100%;
#     }
#     .styled-table tr:nth-child(even) {
#         background-color: #fcfcfc;
#     }
#     .styled-table tr:hover {
#         background-color: #f1f7ff;
#     }
#     .model-col a {
#         color: #0066cc;
#         text-decoration: none;
#         font-weight: 500;
#     }
#     .model-col a:hover {
#         text-decoration: underline;
#     }

#     /* DARK THEME */
#     @media (prefers-color-scheme: dark) {
#         body {
#             background: #111827;
#             color: #f9fafb;
#         }
#         .main-title {
#             color: #f9fafb;
#         }
#         .styled-table {
#             border: 1px solid #374151;
#         }
#         .styled-table th {
#             background-color: #374151;
#             color: #e5e7eb;
#             border: 1px solid #4b5563;
#         }
#         .styled-table td {
#             background-color: #1f2937;
#             color: #f9fafb;
#             border: 1px solid #374151;
#         }
#         .styled-table tr:nth-child(even) {
#             background-color: #111827;
#         }
#         .styled-table tr:hover {
#             background-color: #2563eb33;
#         }
#         .model-col a {
#             color: #93c5fd;
#         }
#     }
# </style>
# """

# # ---------------- Gradient ----------------
# def value_to_gradient_range(value: float, min_val: float = 0, max_val: float = 100, theme="light") -> str:
#     """
#     Map value (0-100) to a gradient background.
#     Light: pink → yellow → green (pastel).
#     Dark: purple → blue → green (soft).
#     """
#     ratio = (value - min_val) / (max_val - min_val)
#     ratio = max(0, min(1, ratio))

#     if theme == "dark":
#         start = (147, 51, 234)   # purple
#         mid = (56, 189, 248)     # blue
#         end = (34, 197, 94)      # green
#     else:
#         start = (255, 179, 186)   # pink
#         mid = (255, 245, 186)     # yellow
#         end = (186, 255, 201)     # green

#     if ratio < 0.5:
#         t = ratio / 0.5
#         r = int(start[0] + t * (mid[0] - start[0]))
#         g = int(start[1] + t * (mid[1] - start[1]))
#         b = int(start[2] + t * (mid[2] - start[2]))
#     else:
#         t = (ratio - 0.5) / 0.5
#         r = int(mid[0] + t * (end[0] - mid[0]))
#         g = int(mid[1] + t * (end[1] - mid[1]))
#         b = int(mid[2] + t * (end[2] - mid[2]))

#     return f"linear-gradient(90deg, rgba({r},{g},{b},0.4), rgba({r},{g},{b},0.9))"

# # ---------------- Table Renderer ----------------
# def df_to_styled_html(
#     df: pd.DataFrame, 
#     table_id: str = "leaderboard", 
#     active_col=None, 
#     ascending=None,
#     theme="light"
# ) -> str:
#     """Convert DataFrame into styled HTML leaderboard table with gradients and sortable headers (JS)."""
#     if df.empty:
#         return "<p>No results found.</p>"

#     task_columns = [c for c in df.columns if c not in ["Model", "Precision", "#Params (B)", "License", "Organization", "Context"]]
#     df = df.dropna(how="all", subset=task_columns)
#     df = df[~df[task_columns].apply(lambda row: all(str(v) in ["--", "nan", "NaN"] for v in row), axis=1)]

#     if "Model" in df.columns:
#         def linkify(m):
#             if isinstance(m, str) and "/" in m:
#                 if m.lower().startswith(("openai/", "anthropic/", "google/gemini")):
#                     return str(m)
#                 return f"<a href='https://huggingface.co/{m}' target='_blank'>{m}</a>"
#             return str(m)
#         df["Model"] = df["Model"].apply(linkify)

#     # HTML Table
#     html = HTML_STYLE
#     html += f"<table id='{table_id}' class='styled-table'>"
#     html += "<thead><tr>"

#     for col in df.columns:
#         if col == active_col:
#             arrow = "▲" if ascending else "▼"
#             html += f"<th onclick='sortTable(\"{table_id}\", \"{col}\")'>{col} {arrow}</th>"
#         else:
#             html += f"<th onclick='sortTable(\"{table_id}\", \"{col}\")'>{col}</th>"
#     html += "</tr></thead><tbody>"

#     for _, row in df.iterrows():
#         html += "<tr>"
#         for col in df.columns:
#             val = row[col]
#             if pd.isna(val) or val == "--":
#                 cell = f"<td>--</td>"
#             elif isinstance(val, (int, float)):
#                 gradient = value_to_gradient_range(float(val), 0, 100, theme=theme)
#                 cell = f"<td style='background: {gradient}'>{val:.1f}</td>"
#             else:
#                 cls = "model-col" if col == "Model" else ""
#                 cell = f"<td class='{cls}'>{val}</td>"
#             html += cell
#         html += "</tr>"

#     html += "</tbody></table>"

#     html += f"""
#     <script>
#     function sortTable(tableId, columnName) {{
#         const table = document.getElementById(tableId);
#         const tbody = table.tBodies[0];
#         const rows = Array.from(tbody.querySelectorAll("tr"));
#         const headers = Array.from(table.querySelectorAll("th"));
#         const colIndex = headers.findIndex(th => th.textContent.trim().startsWith(columnName));
#         if (colIndex === -1) return;
#         const isAsc = !headers[colIndex].classList.contains("asc");
#         headers.forEach(h => h.classList.remove("asc","desc"));
#         headers[colIndex].classList.add(isAsc ? "asc" : "desc");
#         rows.sort((a,b) => {{
#             const aText = a.children[colIndex].textContent.trim();
#             const bText = b.children[colIndex].textContent.trim();
#             const aVal = parseFloat(aText); const bVal = parseFloat(bText);
#             if (!isNaN(aVal) && !isNaN(bVal)) return isAsc ? aVal-bVal : bVal-aVal;
#             return isAsc ? aText.localeCompare(bText) : bText.localeCompare(aText);
#         }});
#         rows.forEach(r => tbody.appendChild(r));
#     }}
#     </script>
#     """
#     return html
import pandas as pd
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

    hidden_cols = ["Organization", "OpenSource", "Brand"]
    df = df[[c for c in df.columns if c not in hidden_cols]]
    
    if "Model" in df.columns:
        def linkify(m):
            if isinstance(m, str) and "/" in m:
                if m.lower().startswith(("openai/", "anthropic/", "google/gemma")):
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

