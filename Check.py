import pandas as pd
import numpy as np
import plotly.express as px

# Step 1: Generate daily coverage data
np.random.seed(1)
dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
coverage = np.random.uniform(0, 1, size=len(dates))  # Coverage as float between 0-1

df = pd.DataFrame({
    "Date": dates,
    "Coverage": coverage
})

# Step 2: Bin coverage into thresholds
def coverage_label(c):
    if c < 0.5:
        return "Low (<50%)"
    elif c < 0.7:
        return "Medium (50–70%)"
    else:
        return "High (>70%)"

df["CoverageLabel"] = df["Coverage"].apply(coverage_label)

# Step 3: Group consecutive days with same label into blocks
df["Group"] = (df["CoverageLabel"] != df["CoverageLabel"].shift()).cumsum()

grouped = df.groupby("Group").agg({
    "Date": ["first", "last"],
    "Coverage": "mean",
    "CoverageLabel": "first"
}).reset_index(drop=True)

grouped.columns = ["Start", "End", "AvgCoverage", "CoverageLabel"]
grouped["Sensor"] = "Sensor A"

# Step 4: Create timeline
fig = px.timeline(
    grouped,
    x_start="Start",
    x_end="End",
    y="Sensor",
    color="CoverageLabel",
    color_discrete_map={
        "Low (<50%)": "red",
        "Medium (50–70%)": "orange",
        "High (>70%)": "green"
    },
    hover_data={"AvgCoverage": ":.0%"},  # show average coverage of block
    title="Sensor A Coverage Timeline (2024)"
)

# Optional layout tweaks
fig.update_yaxes(autorange="reversed")  # Gantt-style
fig.update_layout(
    height=300,
    xaxis_title="Date",
    yaxis_title="",
    bargap=0.1,
    margin=dict(l=20, r=20, t=40, b=40)
)

fig.show()
# Optional: Add a line on top of fill
fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Coverage'] * 100,
    mode='lines',
    line=dict(shape='hv', color='darkgreen', width=2),
    name='',
    hoverinfo='skip',
    showlegend=False
))

# Layout
fig.update_layout(
    title='Sensor A Coverage Over Time (Weekly)',
    yaxis_title='Coverage (%)',
    xaxis_title='Date',
    yaxis_range=[0, 100],
    height=400,
    plot_bgcolor='white'
)

fig.show()
df = pd.DataFrame(data)

# Assign color by threshold
def coverage_color(cov):
    if cov < 0.5:
        return 'red'
    elif cov < 0.7:
        return 'orange'
    elif cov < 0.9:
        return 'yellowgreen'
    else:
        return 'green'

df['Color'] = df['Coverage'].apply(coverage_color)

# Compute average coverage per sensor for legend label
avg_cov = df.groupby('Sensor')['Coverage'].mean().reset_index()
avg_cov['CoverageLabel'] = avg_cov['Coverage'].apply(lambda c: f"{c*100:.1f}%")
df = df.merge(avg_cov[['Sensor', 'CoverageLabel']], on='Sensor', how='left')
df['LegendLabel'] = df.apply(lambda row: f"{row['Sensor']} ({row['CoverageLabel']})", axis=1)

# Sort y-axis alphabetically or by avg coverage
df['Sensor'] = pd.Categorical(df['Sensor'], categories=sorted(df['Sensor'].unique()), ordered=True)

# Plot
fig = px.timeline(
    df,
    x_start='Start',
    x_end='End',
    y='Sensor',
    color='Color',
    color_discrete_map='identity',
    hover_data={'Coverage': ':.0%'}
)

fig.update_yaxes(autorange='reversed')
fig.update_layout(
    title="Sensor Coverage Timeline - 2024",
    height=700,
    margin=dict(t=60, b=20),
    legend_title_text='Sensors (Avg Coverage)'
)

# Update legend labels and groupings to avoid duplicates
seen = set()
for trace in fig.data:
    sensor_name = trace.y[0]
    label = df[df['Sensor'] == sensor_name]['LegendLabel'].iloc[0]
    trace.name = label
    trace.legendgroup = label
    if label not in seen:
        trace.showlegend = True
        seen.add(label)
    else:
        trace.showlegend = False

fig.show()
