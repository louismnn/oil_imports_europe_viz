import plotly.graph_objects as go
import pandas as pd
import json
import util


def generate_time_series(iso_code: str | None) -> go.Figure:

    if iso_code == None:
        return go.Figure()
    
    df = util.order_datas(iso_code)

    x = list(df.index)
    y = list(df.columns)
    y.remove("TOTAL")

    fig = go.Figure()

    for col in y:
        fig.add_trace(go.Scatter(
            x=x, y=df[col],
            mode='lines',
            line=dict(width=0.5), # , color='rgb(184, 247, 212)'
            stackgroup='one',
            name = util.get_country_name(col),
            groupnorm='percent' # sets the normalization for the sum of the stackgroup
        ))

    fig.update_layout(
        showlegend=True,
        xaxis_type='category',

        yaxis=dict(
            type='linear',
            range=[1, 100],
            ticksuffix='%'),

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(color="white"),
            bgcolor="rgba(0,0,0,0)"),

        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),

        height=175,
        width=1350,

        margin=dict(t=0, b=0, l=0, r=0),
    )

    fig.update_xaxes(
        side="bottom",
        ticklabelposition="outside",
        ticks="inside",
        showline=False,
        showgrid=False,
        tickangle=45,
        tickfont=dict(size=10, color="white")
    )

    fig.update_yaxes(
        visible=False,
        ticklabelposition="inside",
        ticks="inside",
    )

    return fig