import gradio as gr
import pandas as pd

# دیتای تست
df = pd.DataFrame({
    "Model": ["A", "B", "C", "D"],
    "Score": [0.85, 0.65, 0.92, 0.71],
    "Params": [1.3, 2.1, 0.9, 5.4],
})

# HTML جدول
def df_to_styled_html(df: pd.DataFrame, table_id: str = "leaderboard", active_col=None, ascending=None) -> str:
    html = f"<table id='{table_id}' class='styled-table'>"
    html += "<thead><tr>"

    for col in df.columns:
        up_color = "color:#999;"  # پیش‌فرض خاکستری
        down_color = "color:#999;"
        if active_col == col:
            if ascending:
                up_color = "color:#2563eb;font-weight:bold;"  # آبی برای صعودی
            else:
                down_color = "color:#2563eb;font-weight:bold;"  # آبی برای نزولی

        html += f"""
        <th>
            {col}
            <button style='all:unset;cursor:pointer;' 
                    onclick="document.getElementById('{table_id}_{col}_asc').click()">
                <span style='{up_color}'>&uarr;</span>
