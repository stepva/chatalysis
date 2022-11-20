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
    df["to"] = df["to"].fillna(pd.to_datetime(to_day))
    df["to_str"] = df["to"].dt.strftime("%-m/%-d/%Y")  # for some reason the d3 formatting did not work for this column
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
        ],
        text="group_name",
        custom_data=["from", "to_str", "group_name", "changed_by"],
        height=100,
        range_x=[from_day, to_day],
    )
    fig1.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        xaxis=dict(linecolor="rgba(0,0,0,0.75)"),
    )
    fig1.update_traces(
        textposition="inside",
        insidetextanchor="start",
        hovertemplate="<b>%{customdata[2]}</b><br>%{customdata[0]|%x} - %{customdata[1]}<br>Changed by %{customdata[3]}<extra></extra>",
    )
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


def nicknames_plot(nicknames: list[dict[str, Any]], from_day: date, to_day: date) -> str:
    if not nicknames:
        return ""

    df = pd.DataFrame(nicknames)
    df["from"] = df["timestamp"].apply(lambda x: datetime.fromtimestamp(x // 1000))
    df["to"] = df.groupby("target")["timestamp"].shift(-1)
    df.loc[~df["to"].isna(), "to"] = df.loc[~df["to"].isna(), "to"].apply(lambda x: datetime.fromtimestamp(x // 1000))
    df["to"] = df["to"].fillna(pd.to_datetime(to_day))
    df["to_str"] = df["to"].dt.strftime("%-m/%-d/%Y")  # for some reason the d3 formatting did not work for this column
    df["type"] = "nickname"
    n_targets = len(df["target"].unique())

    fig1 = px.timeline(
        df,
        x_start="from",
        x_end="to",
        y="target",
        color="nickname",
        color_discrete_sequence=[
            "hsla(42, 79%, 54%, 0.4)",
            "hsla(45, 98%, 67%, 0.2)",
            "hsla(42, 79%, 54%, 0.6)",
            "hsla(45, 98%, 67%, 0.4)",
            "hsla(42, 79%, 54%, 0.8)",
            "hsla(45, 98%, 67%, 0.6)",
            "hsla(42, 79%, 54%, 1)",
            "hsla(45, 98%, 67%, 0.8)",
        ],
        text="nickname",
        custom_data=["from", "to_str", "nickname", "changed_by"],
        range_x=[max([from_day, datetime(2015, 12, 18).date()]), to_day],
        height=min([75 * n_targets, 250]),
    )

    fig1.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        xaxis=dict(linecolor="rgba(0,0,0,0.75)"),
    )
    fig1.update_traces(
        textposition="inside",
        insidetextanchor="start",
        hovertemplate="<b>%{customdata[2]}</b><br>%{customdata[0]|%x} - %{customdata[1]}<br>Changed by %{customdata[3]}<extra></extra>",
    )
    y_fix_range = True if n_targets <= 5 else False
    fig1.update_yaxes(fixedrange=y_fix_range)
    fig1.update_layout(margin=dict(b=25, t=25, l=1, r=20), yaxis_title=None)

    fig = make_subplots(figure=fig1)
    fig.update_layout(
        title={
            "text": "Nicknames over time",
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
