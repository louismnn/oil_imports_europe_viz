import plotly.graph_objects as go
import util


def generate_time_series(iso_code: str | None) -> go.Figure:

    fig = go.Figure()

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
            font=dict(color="black"),
            bgcolor="rgba(0,0,0,0)"),

        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),

        height=400,
        autosize=True,

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
        showticklabels=False,
        showline=False,
        showgrid=False,
        ticklabelposition="inside",
        ticks="inside",
    )

    if iso_code == None:
        return fig
    
    df = util.order_datas(iso_code)

    x = list(df.index)
    y = list(df.columns)
    y.remove("TOTAL")

    for col in y:
        fig.add_trace(go.Scatter(
            x=x, y=df[col],
            mode='lines',
            line=dict(width=0.5),
            stackgroup='one',
            name = util.get_country_name(col),
            groupnorm='percent'
        ))

    return fig