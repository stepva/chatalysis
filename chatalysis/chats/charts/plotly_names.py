from typing import Any
import plotly as pl
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from plotly.subplots import make_subplots


def groupchat_names_plot(group_names: list[dict[str, Any]], from_day: date, to_day: date) -> str:
    if not group_names:
        return ""

    df = pd.DataFrame(group_names)
    df["from"] = df["timestamp"].apply(lambda x: datetime.fromtimestamp(x // 1000))
    df["to"] = df["timestamp"].apply(lambda x: datetime.fromtimestamp(x // 1000)).shift(-1)
    df["to"] = df["to"].fillna(to_day)
    df["type"] = "Chat name"

    fig1 = px.timeline(
        df,
        x_start="from",
        x_end="to",
        y="type",
        color="group_name",
        color_discrete_sequence=[
            "hsla(42, 79%, 54%, 0.4)",
            "hsla(45, 98%, 67%, 0.2)",
            "hsla(42, 79%, 54%, 0.6)",
            "hsla(45, 98%, 67%, 0.4)",
            "hsla(42, 79%, 54%, 0.8)",
            "hsla(45, 98%, 67%, 0.6)",
            "hsla(42, 79%, 54%, 1)",
            "hsla(45, 98%, 67%, 0.8)",
            "hsla(69, 100%, 66%, 0.6)",
            "hsla(17, 80%, 66%, 0.5)",
        ],
        text="group_name",
        hover_data={"from": True, "to": True, "group_name": True, "type": False, "timestamp": False},
        height=125,
        range_x=[from_day, to_day],
    )
    fig1.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        xaxis=dict(linecolor="rgba(0,0,0,0.75)"),
    )
    fig1.update_traces(textposition="inside")
    fig1.update_yaxes(visible=False)
    fig1.update_yaxes(fixedrange=True)
    fig1.update_layout(margin=dict(b=25, t=25, l=1, r=20))

    fig = make_subplots(figure=fig1)
    fig.update_layout(
        title={
            "text": "Chat names over time",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=15, color="grey"),
        }
    )
    # fig.show()

    html = pl.offline.plot(fig, include_plotlyjs=False, output_type="div")
    return html
