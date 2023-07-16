from analytics import (
    data,
    contacts,
    find_phone,
    updated_best,
    updated_worse,
    fig_pie_animated,
    fig_line
)
from dash import Dash, dcc, html
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State

app = Dash(__name__)
ALLOWED_TYPES = ("text", "number")

app.layout = html.Div(
    children=[
        html.Link(
            href="https://fonts.googleapis.com/css?family=Crimson+Text|Work+Sans:400,700",
            rel="stylesheet"
        ),
        html.Link(
            href="/static/styles.css",
            rel="stylesheet"
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H1(
                            children="Text Message Analysis",
                            className="h1-main",
                            style={"text-align": "center"}  # Center align the title
                        ),
                        html.H3(
                            children="Here's how you interacted with your friends",
                            className="subtitle",
                            style={"text-align": "center"}  # Center align the header
                        ),
                    ],
                    className="header-bar",
                ),
            ],
            className="header-container",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.H2(
                                    "Your Best 'Ride or Dies'",
                                    className="h2-section"
                                ),
                                html.Ul(
                                    [
                                        html.Li(
                                            f"{friend} Score: {scores}",
                                            className="li-item"
                                        )
                                        for friend, scores in updated_best[:5]
                                    ]
                                ),
                            ],
                            className="left-section",
                        ),
                        html.Div(
                            children=[
                                html.H2(
                                    "Here's who you could be a little nicer to!",
                                    className="h2-section"
                                ),
                                html.Ul(
                                    [
                                        html.Li(
                                            f"{friend} Score: {scores}",
                                            className="li-item"
                                        )
                                        for friend, scores in updated_worse[:5]
                                    ]
                                ),
                            ],
                            className="left-section",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.H2(
                                            "Some of the words that make you the happiest",
                                            className="h2-section"
                                        ),
                                        html.Img(
                                            id="joy-wordcloud",
                                            src=app.get_asset_url("joy_wordcloud.png"),
                                            style={"width": "400px", "height": "300px"},
                                        ),
                                    ],
                                    style={"margin-bottom": "20px"},
                                )
                            ],
                            className="left-section",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.H2(
                                            "Here's how many messages you sent recently",
                                            className="h2-section"
                                        ),
                                        dcc.Graph(
                                            id="sentiment-line-chart",
                                            figure=fig_line,
                                            style={"height": "400px"},
                                        )
                                    ],
                                    style={"margin-bottom": "20px"},
                                )
                            ],
                            className="left-section",
                        )
                    ],
                    className="left-section-container",
                ),
                html.Div(
                    children=[
                        html.H2(
                            "Sentiment Distribution",
                            className="h2-section"
                        ),
                        dcc.Graph(
                            id="sentiment-pie-chart",
                            figure=fig_pie_animated,
                            style={"height": "400px"},
                        ),
                        html.H2(
                            "Search a Friend",
                            className="h2-section"
                        ),
                        html.H3(
                            "See how they scored, ranked, and the average vibe of their messages in a radar graph!",
                            className="h3-section"
                        ),
                        dcc.Input(
                            id="friend_input",
                            type="text",
                            placeholder="Enter your friend's phone number (eg. +12157965565)",
                            className="friend-input"
                        ),
                        html.Button(
                            "Search",
                            id="search-button",
                            className="search-button"
                        ),
                        html.Div(id="search-results"),
                        html.Div(
                            dcc.Graph(
                                id="emotion-star-plot",
                                style={"height": "400px"},
                            ),
                            id="emotion-star-plot-container",
                            className="right-section-container",
                            style={"display": "none"}
                        )
                    ],
                    className="right-section-container",
                ),
            ],
            className="grid-container",
        ),
    ],
    className="app-layout",
)

@app.callback(
    Output("search-results", "children"),
    Output("sentiment-pie-chart", "figure"),
    Output("emotion-star-plot-container", "style"),
    Output("emotion-star-plot", "figure"),
    inputs=[Input("search-button", "n_clicks")],
    state=[State("friend_input", "value")]
)
def search_friend(n_clicks, friend_input):
    if (
        n_clicks is None
        or n_clicks == 0
        or friend_input is None
        or friend_input == ""
    ):
        return None

    friend_df = data.loc[data['Sent From'] == friend_input]
    if len(friend_df) == 0:
        return None
    else:
        friends_name = find_phone(str(friend_input), contacts)
        if not friends_name:
            friends_name = "No contact name stored"

        # Emotion star plot graph
        fig_star_plot = go.Figure()
        for emotion in emotion_weights.keys():
            fig_star_plot.add_trace(
                go.Scatterpolar(
                    r=[friend_df[emotion].mean()],
                    theta=[emotion.capitalize()],
                    fill="toself",
                    name=emotion.capitalize(),
                )
            )
        fig_star_plot.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=True,
            title=f"Emotion Star Plot for {friends_name}",
            font=dict(color="black", size=12, family="Consolas, monospace"),
        )

        friend_score = round(sum(friend_df['Pos/Neg Score']), 1)
        friend_rank = friend_df['Rank'].iloc[0]

        return (
            html.Div(
                [
                    html.P(f"{friend_input} is saved as {friends_name}", style={"color": "#ffffff", "font-size": "16px"}),
                    html.P(f"Friend Score: {friend_score}", style={"color": "#ffffff", "font-size": "16px"}),
                    html.P(f"Friend Rank: {friend_rank}", style={"color": "#ffffff", "font-size": "16px"}),
                ]
            ),
            fig_pie,
            {"display": "block"} if n_clicks > 0 else {"display": "none"},
            fig_star_plot if len(friend_df) > 0 else go.Figure(),
        )

if __name__ == "__main__":
    app.run_server()
