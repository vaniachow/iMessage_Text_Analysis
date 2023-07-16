import pandas as pd
from dash import Dash, dcc, html, callback
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import re

data = pd.read_csv("complete.csv")
app = Dash(external_stylesheets=[dbc.themes.QUARTZ])
ALLOWED_TYPES = ("text", "number")

'''
CONTACTS
'''
contacts = pd.read_csv("contacts.csv")
for index, row in contacts.iterrows():
    temp = str(row['Phone'])
    temp = re.sub(r"[^\d+]", "", temp)
    if temp and temp[0] != "+":
        temp = "+1" + temp
    contacts.at[index, 'Phone'] = temp


def find_phone(number, contacts):
    for index, row in contacts.iterrows():
        if row['Phone'] == number:
            name = ""
            if not pd.isna(row['First name']):
                name += str(row['First name']) + " "
            if not pd.isna(row['Last name']):
                name += str(row['Last name'])
            return name
    return None


'''
DATA_ANALYSIS
'''
## Best Friend
emotion_weights = {
    'joy': 10, 'surprise': 5, 'love': 5, 'fear': -0.5, 'anger': -1, 'sadness': -1
}

friend_quality = {}
message_counts = {}

for index, row in data.iterrows():
    friend = row['Sent From']
    if friend != 'Me':
        if friend not in friend_quality.keys():
            friend_quality[friend] = {}
            for emotion in emotion_weights.keys():
                friend_quality[friend][emotion] = []
            message_counts[friend] = 0
        for emotion, weight in emotion_weights.items():
            friend_quality[friend][emotion].append(row[emotion] * weight)
        message_counts[friend] += 1

for friend in friend_quality.keys():
    for emotion in emotion_weights.keys():
        if message_counts[friend] > 0:
            friend_quality[friend][emotion] = sum(friend_quality[friend][emotion]) / message_counts[friend]
        else:
            friend_quality[friend][emotion] = 0

best_friends = sorted(friend_quality.items(), key=lambda x: sum(x[1].values()), reverse=True)
updated_best = [("0", "0") for _ in range(5)]
a, b = 0, 0
while a < 5:
    name_avail = find_phone(best_friends[b][0], contacts)
    if name_avail:
        updated_best[a] = (name_avail, round(sum(best_friends[b][1].values()), 1))
        a += 1
    b += 1

updated_worse = [("0", "0") for _ in range(5)]
i, j = 0, len(best_friends) - 1
while i < 5:
    name_avail = find_phone(best_friends[j][0], contacts)
    if name_avail:
        updated_worse[i] = (name_avail, round(sum(best_friends[j][1].values()), 1))
        i += 1
    j -= 1

## Friend Rank
for friend in friend_quality.keys():
    data.loc[data['Sent From'] == friend, 'Pos/Neg Score'] = sum(friend_quality[friend].values())
data['Rank'] = round(data['Pos/Neg Score'].rank(ascending=False), 0).fillna(0).astype(int)

## Plot
data['Time'] = pd.to_datetime(data['Time'])
sentiment_month_counts = data.groupby(['sentiment', pd.Grouper(key='Time', freq='M')]).size().reset_index(name='count')
frames = []
for month in sentiment_month_counts['Time'].unique():
    month_data = sentiment_month_counts[sentiment_month_counts['Time'] == month]
    fig_pie = go.Figure(data=[go.Pie(
        labels=month_data['sentiment'],
        values=month_data['count'],
        hovertemplate='%{label}: %{value}'
    )])
    fig_pie.update_layout(title=f"Sentiment Distribution - {month.strftime('%B %Y')}")
    frame = go.Frame(data=fig_pie.data, layout=fig_pie.layout)
    frames.append(frame)

fig_pie_animated = go.Figure(data=frames[0].data, layout=frames[0].layout, frames=frames[1:])
fig_pie_animated.update_layout(
    updatemenus=[{
        'type': 'buttons',
        'buttons': [{'label': 'Play', 'method': 'animate', 'args': [None]}]
    }],
    showlegend=False
)
fig_pie_animated.update_traces(textinfo='label+percent', hoverinfo='skip')

## Line graph
data['Time'] = pd.to_datetime(data['Time'])
message_counts = data.groupby(pd.Grouper(key='Time', freq='W'))['Time'].count().reset_index(name='Total Messages')
# Set x-axis range from the earliest to the latest message date
x_min = data['Time'].min().to_pydatetime().date()
x_max = data['Time'].max().to_pydatetime().date()
# Line graph
fig_line = go.Figure(data=go.Scatter(
    x=message_counts['Time'],
    y=message_counts['Total Messages'],
    hovertemplate='Week of %{x}: %{y} messages'
))
fig_line.update_traces(mode='lines+markers')
fig_line.update_layout(
    title='Total Messages Over Time',
    xaxis_title='Time',
    yaxis_title='Total Messages',
    xaxis_range=[x_min, x_max]
)

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
