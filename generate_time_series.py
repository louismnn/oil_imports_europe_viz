import plotly.graph_objects as go
import util



def generate_init_graph() -> go.Figure:

    fig = go.Figure()
    
    fig.update_layout(
        showlegend=True,
        xaxis_type='category',

        yaxis=dict(
            type='linear',
            range=[1, 100]
            ),

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(color="white"),
            bgcolor="rgba(0,0,0,0)"
            ),

        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),

        height=200,
        autosize=True,
        margin=dict(t=0, b=0, l=0, r=0),
    )

    fig.update_xaxes(
        side="bottom",
        ticklabelposition="outside",
        ticks="inside",
        showline=False,
        showgrid=False,
        fixedrange=True,
        tickangle=90,
        tickfont=dict(size=7, color="white")
    )

    fig.update_yaxes(
        showticklabels=False,
        showline=False,
        showgrid=False,
        fixedrange=True,
        ticklabelposition="inside",
        ticks="",
    )

    fig.update_traces(visible=False)

    return fig



def generate_time_series(iso_code: str):

    fig = generate_init_graph()

    df, weights = util.order_datas(iso_code)

    colors = [
        '#30123b', '#4145ab', '#4675ed', '#39a2fc', '#1bcfd4', '#24eca6',
        '#61fc6c', '#a4fc3b', '#d1e834', '#f3c63a', '#fe9b2d', '#f36315',
        '#d93806','#b11901', '#7a0402', '#440154', '#482878', '#3e4989',
        '#31688e','#26828e','#1f9e89', '#35b779', '#6ece58', '#b5de2b',
        '#fde725']

    x = list(df.index)
    y = list(df.columns)

    for col, color in zip(y, colors):
        fig.add_trace(go.Scatter(
            x=x, y=df[col],
            mode='lines',
            line=dict(width=0.8, color=color),
            stackgroup='one',
            name = util.get_country_name(col),
            groupnorm='percent'
        ))

    fig.update_xaxes(tickmode="array", tickvals=x[1:-1])

    return fig, weights