import pandas as pd
import re
import plotly.graph_objects as go

data = pd.read_csv("complete.csv")

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
