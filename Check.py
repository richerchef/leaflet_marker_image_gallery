import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Simulated daily coverage data
date_range = pd.date_range("2024-01-01", "2024-12-31", freq="D")
data = pd.DataFrame({
    "date": date_range,
    "coverage": np.random.uniform(0, 100, len(date_range))
})
data.set_index("date", inplace=True)

# Bin options
bin_sizes = {
    "Weekly": "W",
    "Biweekly": "2W",
    "Monthly": "M",
    "Quarterly": "Q"
}

fig = go.Figure()

for label, freq in bin_sizes.items():
    binned = data["coverage"].resample(freq).mean().reset_index()
    fig.add_trace(go.Bar(
        x=binned["date"],
        y=binned["coverage"],
        name=label,
        marker_color=[
            f"rgb({255 - int(c*2.55)}, {int(c*2.55)}, 0)"
            for c in binned["coverage"]
        ],
        visible=True if label == "Weekly" else "legendonly"
    ))

# Add range slider + layout tweaks
fig.update_layout(
    title="Chunky Bars of Sensor Coverage",
    xaxis=dict(
        rangeslider=dict(visible=True),
        type="date"
    ),
    yaxis_title="Coverage (%)",
    barmode="overlay"
)

fig.show()
