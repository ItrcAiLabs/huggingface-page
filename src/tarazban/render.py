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
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;600;700&family=Vazirmatn:wght@400;600&family=Poppins:wght@500;700&display=swap');
    body, table {
        font-family: 'Raleway', 'Vazirmatn', 'Poppins', sans-serif;
    }
    :root{
      --bg: #ffffff;
      --text: #222222;
      --muted: #4b5563;
      --table-border: #f5f5f5;
      --thead-bg: #fafafa;
      --cell-border: #f3f3f3;
      --link: #0066cc;
      --hover-row: #f1f7ff;
    }

    /* dark overrides when .theme-dark is on document root or body */
    .theme-dark, body.theme-dark, html.theme-dark {
      --bg: #0b1220;
      --text: #f9fafb;
      --muted: #94a3b8;
      --table-border: #374151;
      --thead-bg: #374151;
      --cell-border: #374151;
      --link: #93c5fd;
      --hover-row: rgba(37,99,235,0.2);
    }

    body, table {
        font-family: 'Vazirmatn', 'Poppins', sans-serif;
        background: var(--bg);
        color: var(--text);
    }

    .main-title {
        font-family: 'Poppins', 'Vazirmatn', sans-serif;
        font-size: 34px;
        font-weight: 500;
        color: var(--text);
        text-align: center;
        margin: 10px 0 20px 0;
    }

    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        border: 1px solid var(--table-border);
        background: transparent;
        color: var(--text);
    }
    .styled-table th {
        background-color: var(--thead-bg);
        font-weight: 600;
        padding: 8px 10px;
        border: 1px solid var(--cell-border);
        text-align: center;
        font-size: 12px;
        color: var(--text);
    }
    .styled-table td {
        padding: 6px 8px;
        border: 1px solid var(--cell-border);
        font-size: 12px;
        color: var(--text);
        text-align: center;
        background-repeat: no-repeat;
        background-size: 100% 100%;
    }
    .styled-table tr:nth-child(even) {
        background-color: rgba(0,0,0,0); /* leave to gradients or default */
    }
    .styled-table tr:hover {
        background-color: var(--hover-row);
    }
    .model-col a {
        color: var(--link);
        text-decoration: none;
        font-weight: 500;
    }
    .model-col a:hover { text-decoration: underline; }

    /* make sure inline gradient cells remain readable in dark (script will toggle) */
    .styled-table td[data-bg-dark] {
      transition: background .18s ease;
    }
</style>
"""
# ---------------- Gradient ----------------
# def value_to_gradient_range(value: float, min_val: float = 0, max_val: float = 100):
#     """
#     Map value (0-100) to two gradients: (light_theme_gradient, dark_theme_gradient).
#     Return tuple of CSS gradient strings.
#     """
#     ratio = (value - min_val) / (max_val - min_val)
#     ratio = max(0, min(1, ratio))

#     # light theme colors: pink -> yellow -> green (pastel)
#     l_start = (255, 179, 186)   # pink
#     l_mid   = (255, 245, 186)   # yellow
#     l_end   = (186, 255, 201)   # green

#     # dark theme colors: purple -> blue -> green (soft)
#     d_start = (147, 51, 234)    # purple
#     d_mid   = (56, 189, 248)    # blue
#     d_end   = (34, 197, 94)     # green

#     def interp(a, b, t):
#         return int(a + t * (b - a))

#     if ratio < 0.5:
#         t = ratio / 0.5
#         lr = interp(l_start[0], l_mid[0], t)
#         lg = interp(l_start[1], l_mid[1], t)
#         lb = interp(l_start[2], l_mid[2], t)

#         dr = interp(d_start[0], d_mid[0], t)
#         dg = interp(d_start[1], d_mid[1], t)
#         db = interp(d_start[2], d_mid[2], t)
#     else:
#         t = (ratio - 0.5) / 0.5
#         lr = interp(l_mid[0], l_end[0], t)
#         lg = interp(l_mid[1], l_end[1], t)
#         lb = interp(l_mid[2], l_end[2], t)

#         dr = interp(d_mid[0], d_end[0], t)
#         dg = interp(d_mid[1], d_end[1], t)
#         db = interp(d_mid[2], d_end[2], t)

#     light = f"linear-gradient(90deg, rgba({lr},{lg},{lb},0.4), rgba({lr},{lg},{lb},0.9))"
#     dark  = f"linear-gradient(90deg, rgba({dr},{dg},{db},0.28), rgba({dr},{dg},{db},0.76))"
#     return light, dark
def value_to_gradient_range(value: float, min_val: float = 0, max_val: float = 100):
    """
    Map value (0-100) to two variants:
      - light: pastel gradient (as before)
      - dark: single solid color with moderate alpha (no gradient)
    Return tuple: (light_css, dark_css)
    """
    ratio = (value - min_val) / (max_val - min_val)
    ratio = max(0, min(1, ratio))

    # light theme colors: pink -> yellow -> green (pastel)
    l_start = (255, 179, 186)   # pink
    l_mid   = (255, 245, 186)   # yellow
    l_end   = (186, 255, 201)   # green

    # dark theme colors (for solid color): purple -> blue -> green
    d_start = (147, 51, 234)    # purple
    d_mid   = (56, 189, 248)    # blue
    d_end   = (34, 197, 94)     # green

    def interp(a, b, t):
        return int(a + t * (b - a))

    if ratio < 0.5:
        t = ratio / 0.5
        lr = interp(l_start[0], l_mid[0], t)
        lg = interp(l_start[1], l_mid[1], t)
        lb = interp(l_start[2], l_mid[2], t)

        dr = interp(d_start[0], d_mid[0], t)
        dg = interp(d_start[1], d_mid[1], t)
        db = interp(d_start[2], d_mid[2], t)
    else:
        t = (ratio - 0.5) / 0.5
        lr = interp(l_mid[0], l_end[0], t)
        lg = interp(l_mid[1], l_end[1], t)
        lb = interp(l_mid[2], l_end[2], t)

        dr = interp(d_mid[0], d_end[0], t)
        dg = interp(d_mid[1], d_end[1], t)
        db = interp(d_mid[2], d_end[2], t)

    # light: keep the gradient visual
    light = f"linear-gradient(90deg, rgba({lr},{lg},{lb},0.4), rgba({lr},{lg},{lb},0.9))"
    # dark: use a single solid color with alpha for subtle background,
    # choose slightly stronger alpha for readability on dark surface
    dark  = f"rgba({dr},{dg},{db},0.28)"  # no gradient, just a tint

    return light, dark

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
                if m.lower().startswith(("openai/", "anthropic/", "google/gemini")):
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
                    bg_light, bg_dark = value_to_gradient_range(float(value))
                    html += (
                        f"<td data-bg-light=\"{bg_light}\" data-bg-dark=\"{bg_dark}\" "
                        f"style='background:{bg_light};'>{value:.1f}</td>"
                    )
            else:
                if col == "Model":
                    html += f"<td class='model-col'>{value}</td>"
                else:
                    html += f"<td>{value}</td>"
        html += "</tr>"

    html += "</tbody></table>"

    # ... بعد از ساخت جدول (قبل از return)

    html += """
    <script>
    (function(){
      function applyGradients(){
        var isDark = document.body.classList.contains('theme-dark') || document.documentElement.classList.contains('theme-dark');
        document.querySelectorAll('[data-bg-dark]').forEach(function(td){
          var light = td.getAttribute('data-bg-light');
          var dark  = td.getAttribute('data-bg-dark');
          td.style.background = isDark ? dark : light;
        });
      }
      // initial
      applyGradients();
      // observe class changes on root to respond to theme toggle
      new MutationObserver(function(){ applyGradients(); })
        .observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
      new MutationObserver(function(){ applyGradients(); })
        .observe(document.body, { attributes: true, attributeFilter: ['class'] });
    })();
    </script>
    """

    # return html
    return f"<div class='table-wrapper'>{html}</div>"

