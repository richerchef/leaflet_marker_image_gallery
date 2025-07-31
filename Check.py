import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc

# Setup
colorscale = pc.diverging.RdYlGn[::-1]

# Create multiple sensor data
sensors = ['Sensor A', 'Sensor B']
all_data = []

for sensor in sensors:
    df = pd.DataFrame({
        'Sensor': [sensor] * 10,
        'Start': pd.date_range('2025-01-01', periods=10, freq='30D'),
        'End': pd.date_range('2025-01-01', periods=10, freq='30D') + pd.Timedelta(days=1),
        'Coverage': np.random.uniform(0, 1, size=10)
    })
    df['Color'] = pd.cut(df['Coverage'], bins=10, labels=False).astype(int)
    df['Color'] = df['Color'].apply(lambda i: colorscale[i])
    all_data.append(df)

df = pd.concat(all_data)

# Create initial empty figure
fig = go.Figure()

# Add traces per sensor
for sensor in df['Sensor'].unique():
    subdf = df[df['Sensor'] == sensor]
    for _, row in subdf.iterrows():
        fig.add_trace(go.Bar(
            x=[(row['End'] - row['Start']).days],
            y=[row['Sensor']],
            base=row['Start'],
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
