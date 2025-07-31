import pandas as pd
import numpy as np
import plotly.express as px
import plotly.colors as pc

# Parameters
num_bins = 10  # You can change this (e.g., 5, 20, etc.)

# Generate daily coverage for 1 year
np.random.seed(42)
dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
coverage = np.random.rand(len(dates))  # 0 to 1

df = pd.DataFrame({
    "Date": dates,
    "Coverage": coverage
})

# Bin coverage into equal-width bins
bin_edges = np.linspace(0, 1, num_bins + 1)
bin_labels = [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(num_bins)]  # for color mapping
df["Bin"] = pd.cut(df["Coverage"], bins=bin_edges, labels=bin_labels, include_lowest=True)

# Group consecutive days in same bin
df["Group"] = (df["Bin"] != df["Bin"].shift()).cumsum()

grouped = df.groupby("Group").agg({
    "Date": ['first', 'last'],
    "Coverage": 'mean',
    "Bin": 'first'
}).reset_index(drop=True)

grouped.columns = ["Start", "End", "AvgCoverage", "BinLabel"]
grouped["Sensor"] = "Sensor A"

# Normalize bin values to map to a color scale
norm_bins = [float(label) for label in grouped["BinLabel"]]
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
