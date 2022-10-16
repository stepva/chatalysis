import plotly as pl
import plotly.graph_objects as go


def messages_pie(people: dict) -> str:
    """Prepares the HTML code for the Messages pie chart

    :param people: dict of message counts of the conversation
    :return: HTML code of the chart"""
    labels = []
    data = []
    background = [
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
    ]

    names = [x for x in people if x != "total"]

    if len(names) == 2:
        labels = [names[1], names[0]]
        data = [people[names[1]], people[names[0]]]

    else:
        for n in sorted(people.items(), key=lambda item: item[1], reverse=True)[1:10]:
            labels.append(n[0])
            data.append(n[1])
        if len(names) > 9:
            labels.append("Others")
            sofar = sum(data)
            data.append(people["total"] - sofar)

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=data,
                hole=0.5,
                texttemplate="%{percent:.0%}",
                showlegend=False,
                direction="clockwise",
                sort=False,
                marker=dict(colors=background, line=dict(color="#000000", width=1)),
            )
        ]
    )
    fig.update_layout(
        title={
            "text": "Messages distribution",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=15, color="grey"),
        },
        margin=dict(b=1, t=40, l=20, r=1),
        autosize=False,
        width=200,
        height=200,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    # fig.show()
    html = pl.offline.plot(fig, include_plotlyjs=False, output_type="div")
    return html


def hourly_messages_line(hours: dict) -> str:
    """Prepares the HTML code for the Hourly Messages line chart

    :param hours: dict of message counts per hour of day of the conversation
    :return: HTML code of the chart"""
    data = list(hours.values())

    data = [h / sum(hours.values()) for h in hours.values()]
    fig = go.Figure(
        data=[
            go.Scatter(
                x=list(hours.keys()),
                y=data,
                marker_color="rgba(0,0,0,0.8)",
                fill="tozeroy",
                fillcolor="rgba(0,0,0,0.2)",
                line_shape="spline",
                hovertemplate="%{y:.2%}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title={
            "text": "Messages throughout the day",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=15, color="grey"),
        },
        margin=dict(b=25, t=20, l=1, r=20),
        autosize=True,
        height=225,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        bargap=0.1,
        bargroupgap=0,
        xaxis=dict(linecolor="rgba(0,0,0,0.75)", dtick=4),
        yaxis=dict(linecolor="rgba(0,0,0,0.75)", showticklabels=False),
        hovermode="x",
    )
    # fig.show()
    html = pl.offline.plot(fig, include_plotlyjs=False, output_type="div")
    return html


def daily_messages_bar(days: dict) -> str:
    """Prepares the HTML code for the Daily Messages bar chart

    :param days: dict of message counts per day of the conversation
    :return: HTML code of the chart"""
    data = list(days.values())

    fig = go.Figure(data=[go.Bar(x=list(days.keys()), y=data, marker_color="rgba(0,0,0,0.75)", marker_line_width=0)])
    fig.update_layout(
        title={
            "text": "Daily messages over time",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=15, color="grey"),
        },
        margin=dict(b=25, t=20, l=1, r=20),
        autosize=True,
        height=225,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        bargap=0.1,
        bargroupgap=0,
        xaxis=dict(linecolor="rgba(0,0,0,0.75)"),
        yaxis=dict(linecolor="rgba(0,0,0,0.75)"),
        hovermode="x",
    )
    # fig.show()
    html = pl.offline.plot(fig, include_plotlyjs=False, output_type="div")
    return html
