import pandas as pd
from .render import df_to_styled_html


def make_sort_func(col, df, table_id, ascending):
    def _ctx_to_int(x):
        if pd.isna(x):
            return -1
        s = str(x).strip().lower().replace(" ", "")
        try:
            if s.endswith("m"):   
                return int(float(s[:-1]) * 1_000_000)
            if s.endswith("k"):   
                return int(float(s[:-1]) * 1_000)
            return int(float(s))
        except:
            return -1

    def _sort():
        temp_df = df.copy()
        if col in temp_df.columns:
            if col.lower() == "context":
                temp_df["__ctxnum"] = temp_df[col].apply(_ctx_to_int)
                sorted_df = temp_df.sort_values(
                    by="__ctxnum", ascending=ascending, na_position="last"
                ).drop(columns="__ctxnum")
            else:
                temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
                sorted_df = temp_df.sort_values(
                    by=col, ascending=ascending, na_position="last"
                )
        else:
            sorted_df = temp_df
        return df_to_styled_html(sorted_df, table_id=table_id, active_col=col, ascending=ascending)
    return _sort