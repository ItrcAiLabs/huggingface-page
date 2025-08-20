import gradio as gr
import pandas as pd

# دیتای تست
df = pd.DataFrame({
    "Model": ["A", "B", "C", "D"],
    "Score": [0.85, 0.65, 0.92, 0.71],
    "Params": [1.3, 2.1, 0.9, 5.4],
})

# تبدیل به HTML جدول
def df_to_styled_html(df: pd.DataFrame, table_id: str = "leaderboard") -> str:
    html = f"<table id='{table_id}' class='styled-table'>"
    html += "<thead><tr>"
    for col in df.columns:
        html += f"""
        <th>
            {col}
            <button style='all:unset;cursor:pointer;' 
                    onclick="document.getElementById('{table_id}_{col}_btn').click()">
                <span class='sort-icon'>⇅</span>
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
    return df_to_styled_html(sorted_df), not ascending


# اپ ساده برای تست
with gr.Blocks() as demo:
    ascending = gr.State(True)
    output_html = gr.HTML(value=df_to_styled_html(df))

    # دکمه‌های مخفی برای هر ستون
    for col in df.columns:
        btn = gr.Button(visible=False, elem_id=f"leaderboard_{col}_btn")
        btn.click(
            lambda asc, c=col: sort_table(c, asc),
            inputs=ascending,
            outputs=[output_html, ascending],
        )

if __name__ == "__main__":
    demo.launch()
