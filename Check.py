import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Simulate random sensor data
np.random.seed(1)
date_range = pd.date_range(start="2024-01-01", end="2024-12-31", freq='D')

sensors = ['Sensor A', 'Sensor B']
data = []

for sensor in sensors:
    coverage_values = np.random.randint(0, 101, size=len(date_range))
    
    for i, date in enumerate(date_range):
        data.append({
            'Sensor': sensor,
            'Date': date,
            'Coverage': coverage_values[i]
        })

df = pd.DataFrame(data)

# Bin coverage values into segments (e.g., every 10%)
bin_size = 10
df['Bin'] = (df['Coverage'] // bin_size) * bin_size

# Group consecutive days with same bin value
df['Group'] = (df['Bin'] != df.groupby('Sensor')['Bin'].shift()).cumsum()
grouped = df.groupby(['Sensor', 'Group', 'Bin']).agg(
    Start=('Date', 'min'),
    End=('Date', 'max'),
    Coverage=('Coverage', 'mean')  # average coverage for tooltip
).reset_index()

# Ensure end > start by adding 1 day
grouped['End'] = grouped['End'] + pd.Timedelta(days=1)

# Color scale from red (0%) to green (100%)
import matplotlib.pyplot as plt
cmap = plt.get_cmap("RdYlGn")

def coverage_to_color(value):
    rgba = cmap(value / 100)
    return f"rgba({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)}, {rgba[3]})"

grouped['Color'] = grouped['Coverage'].apply(coverage_to_color)

# Plot
fig = go.Figure()
sensors_seen = set()

for _, row in grouped.iterrows():
    show_legend = row['Sensor'] not in sensors_seen
    fig.add_trace(go.Bar(
        x=[(row['End'] - row['Start']).days],
        y=[row['Sensor']],
        base=row['Start'],
        orientation='h',
        marker=dict(color=row['Color']),
        hovertext=f"{row['Coverage']:.1f}%",
        name=row['Sensor'],
        showlegend=show_legend  # 👈 Only show sensor once in legend
    ))
    sensors_seen.add(row['Sensor'])

fig.update_layout(
    barmode='stack',
    title='Sensor Coverage Timeline',
    xaxis_title='Date',
    yaxis_title='Sensor',
    legend_title='Click to toggle sensors',
    xaxis=dict(type='date')
)

fig.show()            base=row['Start'],
            orientation='h',
            marker=dict(color=row['Color']),
            hovertext=f"{row['Coverage']*100:.1f}%",
            name=row['Sensor'],
            showlegend=False  # We'll use custom buttons instead
        ))

# Create buttons for each sensor
buttons = []
for i, sensor in enumerate(sensors):
    visible = [False] * len(fig.data)
    for j, trace in enumerate(fig.data):
        if trace.name == sensor:
            visible[j] = True
    buttons.append(dict(label=sensor,
                        method="update",
                        args=[{"visible": visible},
                              {"title": f"Viewing: {sensor}"}]))

# Add "All" button
buttons.insert(0, dict(label="All",
                       method="update",
                       args=[{"visible": [True]*len(fig.data)},
                             {"title": "All Sensors"}]))

# Update layout with buttons
fig.update_layout(
    title="Sensor Coverage Timeline",
    updatemenus=[dict(
        type="dropdown",
        buttons=buttons,
        direction="down",
        showactive=True,
        x=0.1,
        xanchor="left",
        y=1.2,
        yanchor="top"
    )],
    barmode='stack',
    xaxis_title="Date",
    yaxis=dict(autorange="reversed")
)

fig.show()norm_bins = [float(label) for label in grouped["BinLabel"]]
colorscale = px.colors.sequential.RdYlGn[::-1]  # Reverse to go from red (low) to green (high)

# Map normalized bin values to color scale
def get_color(value):
    # Normalize between 0 and 1
    norm = value
    idx = int(norm * (len(colorscale) - 1))
    return colorscale[idx]

grouped["Color"] = [get_color(b) for b in norm_bins]

# Plot timeline
fig = px.timeline(
    grouped,
    x_start="Start",
    x_end="End",
    y="Sensor",
    color="Color",  # color column must exist; we'll override it
    color_discrete_map={c: c for c in grouped["Color"]},
    hover_data={"AvgCoverage": ":.0%"},
    title=f"Sensor A Coverage Timeline ({num_bins} Bins)"
)

fig.update_yaxes(autorange="reversed")
fig.update_layout(
    height=300,
    xaxis_title="Date",
    yaxis_title="",
    showlegend=False,
    margin=dict(l=20, r=20, t=40, b=40)
)

fig.show()
