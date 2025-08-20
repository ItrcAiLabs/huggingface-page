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
            html += f"<td>{row[col]}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html


# تابع سورت
def sort_table(col, ascending):
    sorted_df = df.sort_values(by=col, ascending=ascending)
    return df_to_styled_html(sorted_df, active_col=col, ascending=ascending)


# اپ تست
with gr.Blocks() as demo:
    output_html = gr.HTML(value=df_to_styled_html(df))

    # دکمه‌های مخفی برای هر ستون (asc و desc جدا)
    for col in df.columns:
        btn_asc = gr.Button(visible=False, elem_id=f"leaderboard_{col}_asc")
        btn_desc = gr.Button(visible=False, elem_id=f"leaderboard_{col}_desc")

        btn_asc.click(
            lambda c=col: sort_table(c, True),
            inputs=None,
            outputs=output_html,
        )
        btn_desc.click(
            lambda c=col: sort_table(c, False),
            inputs=None,
            outputs=output_html,
        )

if __name__ == "__main__":
    demo.launch()
