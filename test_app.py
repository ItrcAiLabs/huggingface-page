import gradio as gr
import pandas as pd

# یه دیتافریم ساده برای تست
df = pd.DataFrame({
    "Model": ["A", "B", "C"],
    "Accuracy": [0.7, 0.9, 0.8],
    "F1": [0.65, 0.88, 0.75],
})

def render_table(col, order):
    if col is None:
        dff = df
    else:
        asc = (order == "Ascending")
        dff = df.sort_values(by=col, ascending=asc)
    return dff.to_html(classes="styled-table", index=False)

with gr.Blocks() as demo:
    gr.Markdown("## 🔽 Test Leaderboard Sorting")

    sort_col = gr.Dropdown(choices=["Accuracy", "F1"], label="Sort by Column")
    sort_order = gr.Radio(["Ascending", "Descending"], value="Descending", label="Order")

    output_html = gr.HTML(value=render_table(None, "Descending"))

    sort_col.change(fn=render_table, inp
