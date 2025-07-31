import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# --- Simulated sensor data over a year ---
np.random.seed(0)
date_range = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
data = pd.DataFrame({
    "date": date_range,
    "coverage": np.random.randint(0, 101, size=len(date_range))  # 0–100%
})

# --- Rolling window configurations ---
rolling_windows = {
    "Weekly (7d)": 7,
    "Biweekly (14d)": 14,
    "Monthly (30d)": 30,
    "Quarterly (90d)": 90,
}

# --- Color mapping function using RdYlGn ---
def get_colors(values):
    normed = (values - 0) / 100
    normed = normed.fillna(0).clip(0, 1)
    return px.colors.sample_colorscale("RdYlGn", normed)

# --- Start building figure ---
fig = go.Figure()

# 1. Add raw data line
fig.add_trace(go.Scatter(
    x=data["date"], y=data["coverage"],
    mode="lines", name="Raw Coverage",
    line=dict(color="lightblue"),
    hoverinfo="x+y"
))

# 2. Add bar traces for each rolling window
for label, window in rolling_windows.items():
    smoothed = data["coverage"].rolling(window=window, center=True).mean()
    fig.add_trace(go.Bar(
        x=data["date"],
        y=smoothed,
        name=label,
        marker_color=get_colors(smoothed),
        opacity=0.5,
        visible=(label == "Weekly (7d)")  # Only one shown by default
    ))

# --- Layout tweaks ---
fig.update_layout(
    title="Sensor Coverage Over Time (Rolling Averages)",
    xaxis_title="Date",
    yaxis_title="Coverage (%)",
    barmode="overlay",
    hovermode="x unified",
    height=500,
    legend_title="Rolling Window",
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    )
)

fig.show()
